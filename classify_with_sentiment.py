"""
Twitter Ticket Classifier with Sentiment Analysis

Enhanced version that performs:
1. Ticket classification (department/issue type)
2. Sentiment analysis with three categories:
   - Positive: Happy customers, praise
   - Neutral-AtRisk: Frustrated but not yet churning
   - Negative: Angry customers at risk of attrition
"""

import csv
import json
import pathlib
from typing import Dict, List, Tuple, Any
from transformers import pipeline
import torch

# ---- CONFIG ----

INPUT_CSV = pathlib.Path("input_tweets.csv")
OUTPUT_CSV = pathlib.Path("output_tickets_with_sentiment.csv")

# Sentiment thresholds for attrition risk
ATRISK_KEYWORDS = [
    "cancel", "closing account", "switching", "leaving", "done with",
    "terrible", "awful", "worst", "disgusted", "disappointed",
    "never again", "lost customer", "unacceptable"
]

# ---- MODELS ----

def load_models():
    """Load both classification and sentiment analysis models."""
    device = 0 if torch.cuda.is_available() else -1
    
    # Ticket classifier (zero-shot)
    ticket_classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=device
    )
    
    # Sentiment analyzer
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=device
    )
    
    return ticket_classifier, sentiment_analyzer

# ---- CLASSIFICATION ----

def classify_ticket(text: str, classifier) -> Dict[str, Any]:
    """Classify tweet into department/issue categories."""
    candidate_labels = [
        "card_declined",
        "atm_issue",
        "account_balance",
        "fraud_security",
        "app_technical",
        "branch_location",
        "fees_charges",
        "loan_mortgage",
        "general_inquiry"
    ]
    
    result = classifier(text, candidate_labels)
    return {
        "category": result["labels"][0],
        "confidence": result["scores"][0]
    }

# ---- SENTIMENT ANALYSIS ----

def analyze_sentiment_detailed(text: str, analyzer) -> Dict[str, Any]:
    """
    Perform sentiment analysis with attrition risk detection.
    
    Returns:
        - sentiment: 'positive', 'neutral_atrisk', 'negative'
        - score: confidence score
        - attrition_risk: low/medium/high
    """
    # Get base sentiment
    result = analyzer(text)[0]
    base_label = result["label"].lower()  # 'positive' or 'negative'
    base_score = result["score"]
    
    # Check for attrition risk keywords
    text_lower = text.lower()
    attrition_keywords_found = [
        kw for kw in ATRISK_KEYWORDS if kw in text_lower
    ]
    
    # Determine final sentiment and attrition risk
    if base_label == "positive" and base_score > 0.8:
        sentiment = "positive"
        attrition_risk = "low"
    elif base_label == "negative" and base_score > 0.7:
        # Check if it's just frustrated or truly negative
        if attrition_keywords_found:
            sentiment = "negative"
            attrition_risk = "high"
        else:
            sentiment = "neutral_atrisk"
            attrition_risk = "medium"
    elif base_label == "negative" and attrition_keywords_found:
        sentiment = "negative"
        attrition_risk = "high"
    else:
        # Ambiguous cases - check for attrition keywords
        if attrition_keywords_found:
            sentiment = "neutral_atrisk"
            attrition_risk = "medium"
        else:
            sentiment = "neutral_atrisk"
            attrition_risk = "low"
    
    return {
        "sentiment": sentiment,
        "confidence": base_score,
        "attrition_risk": attrition_risk,
        "risk_keywords": attrition_keywords_found[:3]  # Top 3
    }

# ---- PROCESSING ----

def process_tweets(input_path: pathlib.Path, output_path: pathlib.Path):
    """Read tweets, classify, analyze sentiment, write output."""
    print("Loading models...")
    ticket_classifier, sentiment_analyzer = load_models()
    
    print(f"Reading tweets from {input_path}...")
    tweets = []
    with input_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tweets.append(row)
    
    print(f"Processing {len(tweets)} tweets...")
    results = []
    
    for idx, tweet in enumerate(tweets, 1):
        text = tweet["text"]
        
        # Classify ticket
        ticket_class = classify_ticket(text, ticket_classifier)
        
        # Analyze sentiment
        sentiment = analyze_sentiment_detailed(text, sentiment_analyzer)
        
        # Combine results
        result = {
            "tweet_id": tweet.get("id", f"tweet_{idx}"),
            "username": tweet.get("username", "unknown"),
            "text": text,
            "ticket_category": ticket_class["category"],
            "ticket_confidence": round(ticket_class["confidence"], 3),
            "sentiment": sentiment["sentiment"],
            "sentiment_confidence": round(sentiment["confidence"], 3),
            "attrition_risk": sentiment["attrition_risk"],
            "risk_keywords": "|".join(sentiment["risk_keywords"]) if sentiment["risk_keywords"] else "",
            "priority": determine_priority(ticket_class, sentiment)
        }
        
        results.append(result)
        
        if idx % 10 == 0:
            print(f"  Processed {idx}/{len(tweets)} tweets")
    
    # Write output
    print(f"Writing results to {output_path}...")
    fieldnames = [
        "tweet_id", "username", "text", "ticket_category", "ticket_confidence",
        "sentiment", "sentiment_confidence", "attrition_risk", "risk_keywords", "priority"
    ]
    
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Done! Processed {len(results)} tweets.")
    print_summary(results)

def determine_priority(ticket_class: Dict, sentiment: Dict) -> str:
    """Determine ticket priority based on category and sentiment."""
    category = ticket_class["category"]
    attrition_risk = sentiment["attrition_risk"]
    
    # High priority: fraud, attrition risk, or critical issues
    if category == "fraud_security" or attrition_risk == "high":
        return "HIGH"
    elif attrition_risk == "medium" or category in ["card_declined", "atm_issue"]:
        return "MEDIUM"
    else:
        return "LOW"

def print_summary(results: List[Dict]):
    """Print summary statistics."""
    total = len(results)
    
    # Sentiment breakdown
    sentiments = {}
    for r in results:
        s = r["sentiment"]
        sentiments[s] = sentiments.get(s, 0) + 1
    
    # Attrition risk
    risks = {}
    for r in results:
        risk = r["attrition_risk"]
        risks[risk] = risks.get(risk, 0) + 1
    
    print("\n=== SUMMARY ===")
    print(f"Total tweets: {total}")
    print("\nSentiment breakdown:")
    for sent, count in sentiments.items():
        pct = (count/total)*100
        print(f"  {sent}: {count} ({pct:.1f}%)")
    
    print("\nAttrition risk:")
    for risk, count in risks.items():
        pct = (count/total)*100
        print(f"  {risk}: {count} ({pct:.1f}%)")

# ---- MAIN ----

if __name__ == "__main__":
    import sys
    
    input_file = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT_CSV
    output_file = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT_CSV
    
    process_tweets(input_file, output_file)
