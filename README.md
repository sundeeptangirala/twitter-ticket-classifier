# Twitter Ticket Classifier

Automated Twitter feed monitoring and ticket classification system for banking customer service. Multi-step pipeline for ingesting tweets, classifying issues by department, and generating CSV tickets.

## Architecture Overview

This system implements a **6-step modular pipeline**:

```
┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│  Step 1:     │───▶│  Step 2:      │───▶│  Step 3:     │
│  Twitter     │    │  Preprocess   │    │  Classify    │
│  Ingestion   │    │  & Redact PII │    │  Issues      │
└──────────────┘    └───────────────┘    └──────────────┘
                                                │
        ┌───────────────────────────────────────┘
        │
        ▼
┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│  Step 4:     │───▶│  Step 5:      │───▶│  Step 6:     │
│  Severity &  │    │  Write CSV    │    │  Orchestrate │
│  Metadata    │    │  Tickets      │    │  Pipeline    │
└──────────────┘    └───────────────┘    └──────────────┘
```

## Project Structure

```
twitter-ticket-classifier/
├── config.py                 # Configuration and constants
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── step1_twitter_ingestion.py
├── step2_preprocessing.py
├── step3_classification.py
├── step4_severity.py
├── step5_csv_writer.py
├── step6_orchestrator.py    # Main entry point
├── twitter_tickets.csv      # Generated tickets (output)
└── processed_tweets.json    # Tweet ID tracking
```

## Quick Start

### Installation

```bash
git clone https://github.com/sundeeptangirala/twitter-ticket-classifier.git
cd twitter-ticket-classifier
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```bash
TWITTER_BEARER_TOKEN=your_twitter_api_v2_bearer_token
TARGET_HANDLE=YourBankSupport
MAX_TWEETS_PER_FETCH=20
CONFIDENCE_THRESHOLD=0.6
CSV_PATH=twitter_tickets.csv
```

### Run

```bash
python step6_orchestrator.py
```

## Module Documentation

### Already Created:
- `config.py` - Configuration module  
- `requirements.txt` - Dependencies

### To Create:

#### step1_twitter_ingestion.py

Handles Twitter API v2 connection and tweet fetching.

**Key functions:**
- `get_user_id(username)` - Resolve handle to user ID
- `get_recent_tweets(user_id, max_results)` - Fetch recent tweets

#### step2_preprocessing.py

Cleans text and redacts sensitive banking information.

**Key functions:**
- `clean_text(text)` - Remove noise
- `redact_pii(text)` - Mask card numbers, accounts
- `detect_language(text)` - Language detection

#### step3_classification.py

ML-based classification using transformers.

**Key functions:**
- `init_classifier()` - Load zero-shot model
- `classify_tweet_for_bank(text, threshold)` - Returns issue type and queue

#### step4_severity.py

Determines ticket priority based on keywords and context.

**Key functions:**
- `compute_severity(model_label, text)` - Returns High/Medium/Low

#### step5_csv_writer.py

Writes classified tickets to CSV with idempotency.

**Key functions:**
- `ensure_csv()` - Initialize CSV file
- `append_ticket_row(tweet, clf_result, language)` - Add ticket
- `is_tweet_processed(tweet_id)` - Check duplicates

#### step6_orchestrator.py

Main pipeline orchestration.

**Flow:**
1. Fetch tweets (Step 1)
2. For each tweet:
   - Preprocess (Step 2)
   - Classify (Step 3)
   - If issue: compute severity (Step 4)
   - Write to CSV (Step 5)

## CSV Output Format

| Field | Description |
|-------|-------------|
| ticket_id | Unique ID (BANKTW-xxxxxx) |
| tweet_id | X/Twitter post ID |
| tweet_url | Direct link to tweet |
| handle | @username |
| created_at | Tweet timestamp |
| issue_flag | "issue" or "non-issue" |
| model_label | e.g., "card issue" |
| department_queue | e.g., "QUEUE_CARDS" |
| severity | High / Medium / Low |
| confidence | Model confidence 0-1 |
| language | Detected language code |
| tweet_text_redacted | PII-scrubbed text |
| source_channel | "Twitter" |

## Banking Use Cases

### Department Routing

- **QUEUE_CARDS** - Card declined, stolen card, fraud
- **QUEUE_ACCOUNTS** - Balance issues, transfers
- **QUEUE_LOANS** - EMI, disbursement issues
- **QUEUE_DIGITAL** - App down, login problems
- **QUEUE_FRAUD** - Suspicious activity, phishing
- **QUEUE_GENERAL** - Generic inquiries
- **QUEUE_SOCIAL** - Praise, general feedback

### Severity Rules

**High Priority:**
- Keywords: "fraud", "stolen", "can't access money", "salary not credited"
- SLA: < 30 minutes

**Medium Priority:**
- Keywords: "charge", "fee", "emi issue"
- SLA: < 2 hours

**Low Priority:**
- General complaints, minor issues
- SLA: < 24 hours

## Security and Safety

### PII Redaction

Before storage, the system redacts:
- 16-digit card numbers
- 10-12 digit account numbers
- IBAN patterns
- CVV patterns

### Scam Detection

Flags tweets with:
- Phishing keywords
- Suspicious external links
- Impersonation patterns

## Scaling Considerations

For production deployment:

1. **Streaming** - Replace polling with Twitter Filtered Stream API
2. **Database** - Move from CSV to PostgreSQL/MongoDB
3. **Message Queue** - Add RabbitMQ/Kafka for async processing
4. **Monitoring** - Add Prometheus/Grafana dashboards
5. **Alerting** - PagerDuty for high-severity tickets

## Testing

Run tests:
```bash
pytest tests/
```

## License

MIT License - See LICENSE file

## Contributing

Pull requests welcome! Please:
1. Fork the repo
2. Create feature branch
3. Add tests
4. Submit PR

## Known Issues and Roadmap

- [ ] Add support for tweet threads (link related tweets)
- [ ] Implement incident grouping (many users report same outage)
- [ ] Multi-language support beyond English
- [ ] Fine-tune classifier on banking-specific training data
- [ ] Add web dashboard for ticket review

## Support

For issues, please open a GitHub issue or contact the maintainer.

---

**Next Steps:** Create the six Python modules listed above. Each module is self-contained and testable independently.
