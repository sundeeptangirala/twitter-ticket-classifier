#!/usr/bin/env python3
"""
Create Input Tweets CSV File
Generates a sample input_tweets.csv file with example tweets for testing.
"""

import pandas as pd

def create_sample_tweets():
    """
    Creates a list of sample tweets for demonstration.
    In production, this would be replaced with Twitter API calls.
    """
    sample_tweets = [
        {
            "tweet_id": "1001",
            "username": "@john_pgh",
            "text": "@FNBcorp My credit card was declined at the store but I know I have enough credit. This is embarrassing!",
            "timestamp": "2024-01-15 10:30:00"
        },
        {
            "tweet_id": "1002",
            "username": "@sarah_pitt",
            "text": "@FNBcorp Can't access my checking account through the mobile app. Getting error messages.",
            "timestamp": "2024-01-15 11:15:00"
        },
        {
            "tweet_id": "1003",
            "username": "@mike_steel",
            "text": "@FNBcorp I noticed a suspicious charge on my account for $500 that I didn't make. Need help immediately!",
            "timestamp": "2024-01-15 12:00:00"
        },
        {
            "tweet_id": "1004",
            "username": "@lisa_downtown",
            "text": "@FNBcorp What are the current mortgage rates? Looking to refinance my home in Pittsburgh.",
            "timestamp": "2024-01-15 13:45:00"
        },
        {
            "tweet_id": "1005",
            "username": "@dave_tech",
            "text": "@FNBcorp Your ATM at Station Square ate my card! Please help, I need it back.",
            "timestamp": "2024-01-15 14:20:00"
        },
        {
            "tweet_id": "1006",
            "username": "@emma_family",
            "text": "@FNBcorp Thank you for the excellent customer service today! Your team in Shadyside was amazing.",
            "timestamp": "2024-01-15 15:00:00"
        }
    ]
    return sample_tweets

def main():
    # Create sample tweets
    tweets = create_sample_tweets()
    
    # Convert to DataFrame
    df = pd.DataFrame(tweets)
    
    # Save to CSV
    output_file = 'input_tweets.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\u2713 Created input file: {output_file}")
    print(f"\u2713 Number of tweets: {len(df)}")
    print(f"\nFirst 3 rows:")
    print(df.head(3))
    print(f"\nColumns: {list(df.columns)}")

if __name__ == "__main__":
    main()
