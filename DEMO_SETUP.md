# Building a Working Demo

This guide walks you through creating a complete working demo of the Twitter Ticket Classifier system.

## Quick Demo Setup (Without Twitter API)

For testing without Twitter API credentials, we'll create a demo with mock data.

### Step 1: Clone and Setup

```bash
git clone https://github.com/sundeeptangirala/twitter-ticket-classifier.git
cd twitter-ticket-classifier
pip install -r requirements.txt
```

### Step 2: Create Demo Script with Mock Data

Create `demo.py`:

```python
"""Demo script with mock tweet data - no Twitter API needed."""
import csv
import os
import uuid
import re
from transformers import pipeline

# Mock tweet data
MOCK_TWEETS = [
    {
        "id": "1234567890",
        "text": "My card was declined at the ATM but I have sufficient balance! Need help urgently @YourBank",
        "author_username": "frustrated_customer",
        "created_at": "2025-12-25T20:00:00.000Z"
    },
    {
        "id": "1234567891",
        "text": "Thanks @YourBank for the quick resolution on my loan query. Great service!",
        "author_username": "happy_user",
        "created_at": "2025-12-25T19:30:00.000Z"
    },
    {
        "id": "1234567892",
        "text": "URGENT: Someone withdrew money from my account! Suspected fraud. Card number 1234-5678-9012-3456",
        "author_username": "scared_customer",
        "created_at": "2025-12-25T19:00:00.000Z"
    },
    {
        "id": "1234567893",
        "text": "Your mobile app keeps crashing when I try to transfer money. Fix this @YourBank",
        "author_username": "tech_user",
        "created_at": "2025-12-25T18:30:00.000Z"
    },
    {
        "id": "1234567894",
        "text": "Charged me an unexpected fee of $25 on my account. What is this for?",
        "author_username": "concerned_customer",
        "created_at": "2025-12-25T18:00:00.000Z"
    },
]

# Configuration
CANDIDATE_LABELS = [
    "card issue", "account issue", "loan issue",
    "digital banking issue", "fraud or security issue",
    "general inquiry", "praise"
]

DEPT_MAP = {
    "card issue": "QUEUE_CARDS",
    "account issue": "QUEUE_ACCOUNTS",
    "loan issue": "QUEUE_LOANS",
    "digital banking issue": "QUEUE_DIGITAL",
    "fraud or security issue": "QUEUE_FRAUD",
    "general inquiry": "QUEUE_GENERAL",
    "praise": "QUEUE_SOCIAL"
}

ISSUE_LABELS = [
    "card issue", "account issue", "loan issue",
    "digital banking issue", "fraud or security issue"
]

# Initialize classifier
print("Loading classification model... (this may take a minute)")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
print("Model loaded successfully!\n")

def redact_pii(text):
    """Redact sensitive information."""
    text = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "****CARD****", text)
    text = re.sub(r"\b\d{10,12}\b", "****ACCOUNT****", text)
    return text

def compute_severity(label, text):
    """Compute ticket severity."""
    t = text.lower()
    if any(w in t for w in ["fraud", "stolen", "urgent", "scam", "unauthorized"]):
        return "High"
    if any(w in t for w in ["fee", "charge", "declined", "crash"]):
        return "Medium"
    return "Low"

def classify_tweet(text, threshold=0.6):
    """Classify tweet using zero-shot classification."""
    result = classifier(text, candidate_labels=CANDIDATE_LABELS, multi_label=False)
    best_label = result["labels"][0]
    best_score = float(result["scores"][0])
    
    is_issue = best_label in ISSUE_LABELS and best_score >= threshold
    
    return {
        "ticket_type": "issue" if is_issue else "non-issue",
        "queue": DEPT_MAP.get(best_label),
        "model_label": best_label,
        "score": best_score
    }

def create_csv_ticket(tweet, clf_result):
    """Create ticket row for CSV."""
    ticket_id = f"BANKTW-{uuid.uuid4().hex[:8].upper()}"
    tweet_url = f"https://x.com/i/web/status/{tweet['id']}"
    redacted_text = redact_pii(tweet['text'])
    severity = compute_severity(clf_result['model_label'], tweet['text'])
    
    return [
        ticket_id,
        tweet['id'],
        tweet_url,
        tweet['author_username'],
        tweet['created_at'],
        clf_result['ticket_type'],
        clf_result['model_label'],
        clf_result['queue'] or "",
        severity,
        round(clf_result['score'], 4),
        "en",
        redacted_text,
        "Twitter"
    ]

def run_demo():
    """Run the complete demo."""
    csv_file = "twitter_tickets_demo.csv"
    
    # Create CSV
    header = [
        "ticket_id", "tweet_id", "tweet_url", "handle", "created_at",
        "issue_flag", "model_label", "department_queue", "severity",
        "confidence", "language", "tweet_text_redacted", "source_channel"
    ]
    
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        print("Processing mock tweets...\n")
        print("="*80)
        
        for i, tweet in enumerate(MOCK_TWEETS, 1):
            print(f"\nTweet {i}/{len(MOCK_TWEETS)}:")
            print(f"From: @{tweet['author_username']}")
            print(f"Text: {tweet['text'][:100]}..." if len(tweet['text']) > 100 else f"Text: {tweet['text']}")
            
            # Classify
            result = classify_tweet(tweet['text'])
            
            print(f"Classification: {result['model_label']} (confidence: {result['score']:.2%})")
            print(f"Ticket Type: {result['ticket_type']}")
            print(f"Department: {result['queue'] or 'N/A'}")
            
            # Create ticket if it's an issue
            if result['ticket_type'] == 'issue':
                row = create_csv_ticket(tweet, result)
                writer.writerow(row)
                print(f"✓ Ticket created: {row[0]}")
            else:
                print("✗ No ticket created (non-issue)")
            
            print("-"*80)
    
    print(f"\n✓ Demo complete! Check '{csv_file}' for results.")
    print(f"\nSummary:")
    print(f"- Processed {len(MOCK_TWEETS)} tweets")
    print(f"- Created tickets for issues only")
    print(f"- Output saved to: {csv_file}")

if __name__ == "__main__":
    run_demo()
```

### Step 3: Run the Demo

```bash
python demo.py
```

**Expected Output:**
- Console logs showing classification of each mock tweet
- A file `twitter_tickets_demo.csv` with ticket data
- Classification confidence scores
- Department routing decisions

### Step 4: View Results

Open `twitter_tickets_demo.csv` in Excel or any spreadsheet app to see:
- Ticket IDs
- Tweet classifications
- Department assignments
- Severity levels
- Redacted PII

---

## Full Production Setup (With Twitter API)

### Prerequisites

1. **Twitter Developer Account**
   - Go to https://developer.twitter.com/
   - Create a new app
   - Get your Bearer Token from the "Keys and tokens" tab

2. **Python Environment**
   ```bash
   python --version  # Should be 3.9+
   pip install -r requirements.txt
   ```

### Setup Steps

1. **Create `.env` file:**

```bash
TWITTER_BEARER_TOKEN=your_actual_bearer_token_here
TARGET_HANDLE=elonmusk
MAX_TWEETS_PER_FETCH=10
CONFIDENCE_THRESHOLD=0.6
CSV_PATH=twitter_tickets.csv
```

2. **Create the Python modules** (see full code in the repository README)

3. **Run the orchestrator:**

```bash
python step6_orchestrator.py
```

---

## Demo Features

### What the Demo Shows:

1. **Tweet Ingestion** - Reads mock tweet data (or real Twitter API)
2. **PII Redaction** - Automatically redacts card numbers and sensitive info
3. **ML Classification** - Uses zero-shot learning to categorize tweets
4. **Department Routing** - Routes to correct banking department queue
5. **Severity Assignment** - Assigns High/Medium/Low priority
6. **CSV Generation** - Creates importable ticket file

### Sample Output:

```
Processing mock tweets...

Tweet 1/5:
From: @frustrated_customer
Text: My card was declined at the ATM...
Classification: card issue (confidence: 87%)
Ticket Type: issue
Department: QUEUE_CARDS
✓ Ticket created: BANKTW-A3F2D1B8

Tweet 2/5:
From: @happy_user
Text: Thanks @YourBank for the quick resolution...
Classification: praise (confidence: 92%)
Ticket Type: non-issue
Department: QUEUE_SOCIAL
✗ No ticket created (non-issue)
...
```

---

## Troubleshooting

### Model Download Issues

If the model download is slow:
```bash
# Pre-download the model
python -c "from transformers import pipeline; pipeline('zero-shot-classification', model='facebook/bart-large-mnli')"
```

### Import Errors

```bash
pip install --upgrade transformers torch TwitterAPI python-dotenv langdetect
```

### CSV File Issues

If CSV won't open:
- Use UTF-8 encoding
- Try opening in Google Sheets
- Check file permissions

---

## Next Steps

1. **Customize** - Edit CANDIDATE_LABELS in demo.py for your use case
2. **Add Tweets** - Add more mock tweets to MOCK_TWEETS
3. **Connect API** - Get Twitter credentials and build full modules
4. **Visualize** - Create dashboards from the CSV output
5. **Deploy** - Set up as a scheduled job or webhook listener

---

## Questions?

Open an issue on GitHub or check the main README.md for more details.
