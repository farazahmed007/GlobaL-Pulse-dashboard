import os
import time
import json
import logging
from datetime import datetime, timedelta, timezone
import requests
from pymongo import MongoClient  # type: ignore
from pymongo.errors import BulkWriteError, PyMongoError  # type: ignore

# Reusing the existing pipeline components
from sentiment_pipeline import PROMPT_TEMPLATE, call_llm_api, NEWS_API_KEY, LLM_API_KEY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Defaulting to Docker network URI per requirements, but allowing override
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
DB_NAME = "global_pulse"
COLLECTION_NAME = "global_sentiment"

def fetch_historical_headlines(date_str):
    """Fetches historical headlines for a specific date using NewsAPI."""
    logging.info(f"Fetching historical headlines from NewsAPI for {date_str}...")
    url = "https://newsapi.org/v2/everything"
    
    # "q" is often required by /v2/everything if sources/domains aren't specified.
    # Using a broad query "news" or just omitting if allowed.
    # Actually, NewsAPI requires at least one of q, qInTitle, sources, or domains for /everything.
    # Let's use q="world OR technology OR business OR politics" as a broad query.
    params = {
        "q": "world OR technology OR business OR politics",
        "language": "en",
        "apiKey": NEWS_API_KEY,
        "from": date_str,
        "to": date_str,
        "pageSize": 20
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        return articles
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching from NewsAPI for {date_str}: {e}")
        return []

def main():
    if NEWS_API_KEY in ["your_newsapi_key_here", "your_newsapi_key", ""] or \
       LLM_API_KEY in ["your_llm_api_key_here", "your_llm_api_key", ""]:
        logging.warning("Default or missing API keys detected. API calls may fail.")

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Verify connection
        client.admin.command('ping')
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        logging.info(f"Successfully connected to MongoDB at {MONGO_URI}.")
    except PyMongoError as e:
        logging.error(f"Failed to connect to MongoDB at {MONGO_URI}: {e}")
        return

    # Iterate through the last 14 days, up to current date
    today = datetime.now(timezone.utc).date()
    
    for i in range(14):
        day_index = i + 1
        # 13 days ago up to today (0 days ago)
        target_date = today - timedelta(days=13 - i)
        date_str = target_date.isoformat()
        
        articles = fetch_historical_headlines(date_str)
        
        if not articles:
            print(f"Ingested Day {day_index}/14: {date_str} [0 records]")
            time.sleep(1)
            continue
            
        processed_docs = []
        for article in articles:
            headline = article.get("title", "")
            description = article.get("description", "")
            
            text_to_analyze = f"{headline}. {description}" if description else headline
            if not text_to_analyze:
                continue
                
            prompt = PROMPT_TEMPLATE.format(input_text=text_to_analyze)
            
            # Send to LLM
            llm_response = call_llm_api(prompt, mock=False)
            if not llm_response:
                continue
                
            try:
                # Clean up LLM response
                clean_response = llm_response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.startswith("```"):
                    clean_response = clean_response[3:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                
                parsed_data = json.loads(clean_response.strip())
                
                # Attach published_at matching the historical article date
                published_at_str = article.get("publishedAt")
                if published_at_str:
                    try:
                        # Convert ISO string from NewsAPI to BSON-compatible datetime
                        parsed_data["published_at"] = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                    except ValueError:
                        parsed_data["published_at"] = published_at_str
                else:
                    # Fallback to the target date of the backfill
                    parsed_data["published_at"] = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
                
                processed_docs.append(parsed_data)
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error for headline '{headline}': {e}")
                continue
                
        # Batch insert
        if processed_docs:
            try:
                collection.insert_many(processed_docs, ordered=False)
            except BulkWriteError as e:
                logging.warning(f"Some documents failed to insert on {date_str}: {e.details}")
            except PyMongoError as e:
                logging.error(f"MongoDB insertion error on {date_str}: {e}")
                
        # Progress log
        print(f"Ingested Day {day_index}/14: {date_str} [{len(processed_docs)} records]")
        
        # 1-second delay between daily processing (avoids rate limits on NewsAPI)
        time.sleep(1)

if __name__ == "__main__":
    main()
