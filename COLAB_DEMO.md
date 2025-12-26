# Google Colab Demo - Reading Tweets from Input File

This demo shows how to classify tweets from an input CSV file instead of hardcoded data.

## Setup Instructions

### Step 1: Create Input Tweets CSV File

First, create a CSV file with your tweets:

```python
# Step 1: Create input tweets CSV file
import pandas as pd

# Create sample input tweets
input_tweets_data = [
    {"tweet_id": "1001", "username": "@john_pgh", "text": "@FNBcorp My credit card was declined at the store but I know I have enough credit. This is embarrassing!", "timestamp": "2024-01-15 10:30:00"},
    {"tweet_id": "1002", "username": "@sarah_pitt", "text": "@FNBcorp Can't access my checking account through the mobile app. Getting error messages.", "timestamp": "2024-01-15 11:15:00"},
    {"tweet_id": "1003", "username": "@mike_steel", "text": "@FNBcorp I noticed a suspicious charge on my account for $500 that I didn't make. Need help immediately!", "timestamp": "2024-01-15 12:00:00"},
    {"tweet_id": "1004", "username": "@lisa_downtown", "text": "@FNBcorp What are the current mortgage rates? Looking to refinance my home in Pittsburgh.", "timestamp": "2024-01-15 13:45:00"},
    {"tweet_id": "1005", "username": "@dave_tech", "text": "@FNBcorp Your ATM at Station Square ate my card! Please help, I need it back.", "timestamp": "2024-01-15 14:20:00"},
    {"tweet_id": "1006", "username": "@emma_family", "text": "@FNBcorp Thank you for the excellent customer service today! Your team in Shadyside was amazing.", "timestamp": "2024-01-15 15:00:00"}
]

# Save to CSV
input_df = pd.DataFrame(input_tweets_data)
input_filename = 'input_tweets.csv'
input_df.to_csv(input_filename, index=False)

print(f"✓ Created input file: {input_filename}")
print(f"✓ Number of tweets: {len(input_df)}")
print(f"\nFirst 3 rows:")
print(input_df.head(3))
```

### Step 2: Read from CSV and Classify Tweets

```python
# Step 2: Read from input CSV and classify
from transformers import pipeline
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("Reading tweets from input file...")
# Read tweets from CSV
input_tweets_df = pd.read_csv('input_tweets.csv')
mock_tweets = input_tweets_df.to_dict('records')  # Convert to list of dictionaries

print(f"Loaded {len(mock_tweets)} tweets from input file\n")
print("Loading sentiment analysis model...")
classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Classification keywords
department_keywords = {
    "Cards": ["credit card", "debit card", "card declined", "atm", "card ate"],
    "Accounts": ["checking", "savings", "account", "balance", "deposit"],
    "Loans": ["mortgage", "loan", "refinance", "home loan", "auto loan"],
    "Digital": ["app", "online", "mobile", "website", "login", "error"],
    "Fraud": ["suspicious", "fraud", "unauthorized", "didn't make", "scam"]
}

def classify_department(text):
    text_lower = text.lower()
    for dept, keywords in department_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return dept
    return "General"

def classify_priority(sentiment_score, text):
    urgent_words = ["immediately", "urgent", "help", "fraud", "suspicious"]
    text_lower = text.lower()
    if sentiment_score < 0.3 or any(word in text_lower for word in urgent_words):
        return "High"
    elif sentiment_score < 0.6:
        return "Medium"
    else:
        return "Low"

# Process tweets
tickets = []
print(f"Processing {len(mock_tweets)} tweets...\n")

for tweet in mock_tweets:
    sentiment_result = classifier(tweet["text"][:512])[0]
    sentiment_score = sentiment_result['score'] if sentiment_result['label'] == 'POSITIVE' else 1 - sentiment_result['score']
    department = classify_department(tweet["text"])
    priority = classify_priority(sentiment_score, tweet["text"])
    
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
    print(f"  {tweet['username']} → {department} ({priority})")

# Save results
df = pd.DataFrame(tickets)
output_filename = 'output_tickets.csv'
df.to_csv(output_filename, index=False)

print(f"\n{'='*60}")
print(f"PROCESSING COMPLETE")
print(f"{'='*60}")
print(f"Input file: input_tweets.csv ({len(mock_tweets)} tweets)")
print(f"Output file: {output_filename} ({len(tickets)} tickets)")
print(f"\nDepartment Summary:")
for dept, count in df['Department'].value_counts().items():
    print(f"  {dept}: {count}")
print(f"\nPriority Summary:")
for priority, count in df['Priority'].value_counts().items():
    print(f"  {priority}: {count}")
```

## Key Changes from Original Demo

### Before (Hardcoded):
```python
mock_tweets = [
    {
        "tweet_id": "1001",
        "username": "@john_pgh",
        "text": "@FNBcorp My credit card was declined...",
        "timestamp": "2024-01-15 10:30:00"
    },
    # ... more hardcoded tweets
]
```

### After (File-based):
```python
input_tweets_df = pd.read_csv('input_tweets.csv')
mock_tweets = input_tweets_df.to_dict('records')
```

## Benefits

1. **Separation of Data and Code**: Tweets are now in a separate CSV file
2. **Easy Updates**: Modify tweets without changing code
3. **Real Data Integration**: Easy to replace with real Twitter API data
4. **Scalability**: Can process any number of tweets from the CSV
5. **Testing**: Easy to test with different tweet sets

## Input CSV Format

The `input_tweets.csv` file should have these columns:
- `tweet_id`: Unique identifier for the tweet
- `username`: Twitter username (e.g., @john_pgh)
- `text`: The tweet content
- `timestamp`: When the tweet was posted

## Output

The classifier generates `output_tickets.csv` with:
- Ticket_ID
- Tweet_ID
- Username
- Tweet_Text
- Timestamp
- Department (Cards, Accounts, Loans, Digital, Fraud, General)
- Priority (High, Medium, Low)
- Sentiment (POSITIVE, NEGATIVE)
- Sentiment_Score
- Status
- Created_Date

## Usage with Real Twitter Data

To use with real Twitter data:
1. Fetch tweets using Twitter API
2. Save them to CSV in the same format
3. Run the classification code
4. Process the output tickets
