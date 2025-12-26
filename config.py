"""Configuration settings for Twitter Ticket Classifier."""
import os
from dotenv import load_dotenv

load_dotenv()

# Twitter API Configuration
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TARGET_HANDLE = os.getenv("TARGET_HANDLE", "YourBankSupport")
MAX_TWEETS_PER_FETCH = int(os.getenv("MAX_TWEETS_PER_FETCH", "20"))

# Classification Configuration
CANDIDATE_LABELS = [
    "card issue",
    "account issue",
    "loan issue",
    "digital banking issue",
    "fraud or security issue",
    "general inquiry",
    "praise"
]

# Department Queue Mapping
DEPT_MAP = {
    "card issue": "QUEUE_CARDS",
    "account issue": "QUEUE_ACCOUNTS",
    "loan issue": "QUEUE_LOANS",
    "digital banking issue": "QUEUE_DIGITAL",
    "fraud or security issue": "QUEUE_FRAUD",
    "general inquiry": "QUEUE_GENERAL",
    "praise": "QUEUE_SOCIAL"
}

# Issue-like labels that create tickets
ISSUE_LABELS = [
    "card issue",
    "account issue",
    "loan issue",
    "digital banking issue",
    "fraud or security issue"
]

# Thresholds
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))

# CSV Output Configuration
CSV_PATH = os.getenv("CSV_PATH", "twitter_tickets.csv")
PROCESSED_TWEETS_FILE = os.getenv("PROCESSED_TWEETS_FILE", "processed_tweets.json")

# CSV Header
CSV_HEADER = [
    "ticket_id", "tweet_id", "tweet_url", "handle", "created_at",
    "issue_flag", "model_label", "department_queue", "severity",
    "confidence", "language", "tweet_text_redacted", "source_channel"
]
