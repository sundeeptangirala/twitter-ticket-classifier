#!/usr/bin/env python3
"""
Twitter Ticket Classifier - File-based Version
Reads tweets from input_tweets.csv and generates output_tickets.csv
"""

import pandas as pd
from transformers import pipeline
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Classification keywords for banking departments
DEPARTMENT_KEYWORDS = {
    "Cards": ["credit card", "debit card", "card declined", "atm", "card ate"],
    "Accounts": ["checking", "savings", "account", "balance", "deposit"],
    "Loans": ["mortgage", "loan", "refinance", "home loan", "auto loan"],
    "Digital": ["app", "online", "mobile", "website", "login", "error"],
    "Fraud": ["suspicious", "fraud", "unauthorized", "didn't make", "scam"]
}

def classify_department(text):
    """Classify tweet to appropriate bank department."""
    text_lower = text.lower()
    for dept, keywords in DEPARTMENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return dept
    return "General"

def classify_priority(sentiment_score, text):
    """Determine priority based on sentiment and urgent keywords."""
    urgent_words = ["immediately", "urgent", "help", "fraud", "suspicious"]
    text_lower = text.lower()
    if sentiment_score < 0.3 or any(word in text_lower for word in urgent_words):
        return "High"
    elif sentiment_score < 0.6:
        return "Medium"
    else:
        return "Low"

def main(input_file='input_tweets.csv', output_file='output_tickets.csv'):
    print("Reading tweets from input file...")
    
    # Read tweets from CSV
    try:
        input_df = pd.read_csv(input_file)
        tweets = input_df.to_dict('records')
        print(f"Loaded {len(tweets)} tweets from {input_file}\n")
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please run create_input_tweets.py first.")
        return
    
    # Load sentiment analysis model
    print("Loading sentiment analysis model...")
    classifier = pipeline("sentiment-analysis", 
                         model="distilbert-base-uncased-finetuned-sst-2-english")
    
    # Process tweets
    tickets = []
    print(f"Processing {len(tweets)} tweets...\n")
    
    for tweet in tweets:
        # Sentiment analysis
        sentiment_result = classifier(tweet["text"][:512])[0]
        sentiment_score = (sentiment_result['score'] if sentiment_result['label'] == 'POSITIVE' 
                          else 1 - sentiment_result['score'])
        
        # Classification
        department = classify_department(tweet["text"])
        priority = classify_priority(sentiment_score, tweet["text"])
        
        # Create ticket
        ticket = {
            "Ticket_ID": f"TKT-{tweet['tweet_id']}",
            "Tweet_ID": tweet['tweet_id'],
            "Username": tweet['username'],
            "Tweet_Text": tweet['text'],
            "Timestamp": tweet['timestamp'],
            "Department": department,
            "Priority": priority,
            "Sentiment": sentiment_result['label'],
            "Sentiment_Score": f"{sentiment_score:.2f}",
            "Status": "Open",
            "Created_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        tickets.append(ticket)
        print(f"  {tweet['username']} \u2192 {department} ({priority})")
    
    # Save results
    df = pd.DataFrame(tickets)
    df.to_csv(output_file, index=False)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Input: {input_file} ({len(tweets)} tweets)")
    print(f"Output: {output_file} ({len(tickets)} tickets)")
    print(f"\nDepartment Summary:")
    for dept, count in df['Department'].value_counts().items():
        print(f"  {dept}: {count}")
    print(f"\nPriority Summary:")
    for priority, count in df['Priority'].value_counts().items():
        print(f"  {priority}: {count}")

if __name__ == "__main__":
    main()
