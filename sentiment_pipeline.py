import os
import json
import logging
import requests  # type: ignore
from pymongo import MongoClient  # type: ignore
from pymongo.errors import ConnectionFailure, PyMongoError  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# Configuration
# ==========================================
# It's best practice to use environment variables for keys.
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "your_newsapi_key_here")
LLM_API_KEY = os.getenv("LLM_API_KEY", "your_llm_api_key_here")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "global_pulse"
COLLECTION_NAME = "global_sentiment"

# The prompt template provided, properly escaped for Python's .format() method (using {{ and }})
PROMPT_TEMPLATE = """You are a data extraction assistant for a global sentiment analysis pipeline. Your task is to analyze the following unstructured text and extract the key metrics required for the database.

Strict Output Contract:
Return ONLY valid JSON. Do not include introductory text, conversational prose, markdown formatting, or code fences (e.g., no ```json).

Target Schema:
Your response must strictly match the following JSON structure:
{{
"title": "A short, concise summary of the event (string)",
"country": "The primary country involved (string). If unknown, use null",
"entities": ["array", "of", "strings", "representing key people or organizations"],
"sentiment_score": "A numeric float representing sentiment from -1.0 (highly negative) to 1.0 (highly positive)",
"sentiment_label": "Must be exactly one of: 'positive', 'neutral', 'negative'"
}}

Input Text:
{input_text}
"""

def fetch_headlines():
    """Fetches the latest global headlines using NewsAPI."""
    logging.info("Fetching headlines from NewsAPI...")
    url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        logging.info(f"Successfully fetched {len(articles)} articles.")
        return articles
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching from NewsAPI: {e}")
        return []

def call_llm_api(prompt):
    """
    Sends the prompt to an LLM API. 
    This example uses the requests library to hit a generic OpenAI-compatible completions endpoint.
    You can adjust the URL and payload to match whichever provider you use (e.g., Anthropic, Gemini, OpenAI).
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini", # Replace with your specific LLM model 
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0 # Use temperature 0 for the most deterministic JSON output
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract the text response based on OpenAI schema
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling LLM API: {e}")
        if 'response' in locals() and response.text:
            logging.error(f"LLM API Response details: {response.text}")
        return None
    except (KeyError, IndexError) as e:
        logging.error(f"Error parsing LLM API response structure: {e}")
        return None

def main():
    # 1. Fetch latest headlines
    articles = fetch_headlines()
    if not articles:
        logging.warning("No articles fetched. Exiting pipeline.")
        return

    # 2. Connect to local MongoDB instance
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Verify connection by triggering a server call
        client.admin.command('ping')
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        logging.info("Successfully connected to local MongoDB.")
    except ConnectionFailure as e:
        logging.error(f"Failed to connect to MongoDB at {MONGO_URI}: {e}")
        return

    # Iterate through the fetched articles
    for article in articles:
        headline = article.get("title", "")
        description = article.get("description", "")
        
        # We append description if available to give the LLM more context
        text_to_analyze = f"{headline}. {description}" if description else headline
        
        if not text_to_analyze:
            continue
            
        logging.info(f"Processing headline: {headline}")
        
        # 3. Inject the text into the prompt template
        prompt = PROMPT_TEMPLATE.format(input_text=text_to_analyze)
        
        # Send to LLM
        llm_response = call_llm_api(prompt)
        if not llm_response:
            logging.warning("Received empty response from LLM. Skipping.")
            continue
            
        # 4. Parse the model's response
        try:
            # Defensive clean up: strip any accidental markdown fences if the LLM misbehaves
            clean_response = llm_response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            parsed_data = json.loads(clean_response.strip())
            
            # (Optional) enrich the data with original NewsAPI article metadata
            parsed_data["source_url"] = article.get("url")
            parsed_data["published_at"] = article.get("publishedAt")
            
            # 5. Insert into MongoDB collection
            result = collection.insert_one(parsed_data)
            logging.info(f"Successfully inserted document with _id: {result.inserted_id}")
            
        except json.JSONDecodeError as e:
            # Strict error handling prevents pipeline crashes on malformed responses
            logging.error(f"JSON decode error for headline '{headline}': {e}")
            logging.error(f"Malformed LLM payload skipped: {llm_response}")
            continue
        except PyMongoError as e:
            logging.error(f"MongoDB insertion error: {e}")
            continue

if __name__ == "__main__":
    main()
