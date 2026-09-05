# AI Global Pulse Dashboard - Technical Context

## Overview
The AI Global Pulse Dashboard is a microservices-based application orchestrated via Docker Compose. It continuously fetches global news headlines, performs sentiment analysis and entity extraction using a Large Language Model (LLM), stores the structured data, and visualizes it in real-time through a web dashboard.

## Architecture & Services

The application consists of three primary services running in isolated Docker containers, communicating over a shared internal Docker network (`global-pulse-dashboard_default`):

### 1. MongoDB Database (`pulse_mongodb`)
- **Image**: `mongo:latest`
- **Port**: `27017`
- **Persistence**: Uses a Docker named volume (`mongodb_data`) mounted to `/data/db` to ensure ingested data survives container restarts.
- **Role**: Acts as the central data store. Stores processed intelligence records in the `global_pulse` database under the `global_sentiment` collection.

### 2. Python Pipeline Worker (`pulse_pipeline_worker`)
- **Environment**: Python 3.12 slim
- **Core Script**: `backend/sentiment_pipeline.py`
- **Role**: A background worker that runs continuously to ingest and process data.
- **Workflow**:
  1. **Data Ingestion**: Fetches recent news headlines via HTTP requests to NewsAPI using `NEWS_API_KEY`.
  2. **LLM Processing**: Sends the unstructured text to Google's Generative Language API (specifically the OpenAI-compatible `/v1beta/openai/chat/completions` endpoint) using `LLM_API_KEY`. It instructs the model (`gemini-3.8-flash` or configurable via `LLM_MODEL`) using a strict prompt template to extract:
     - Event Title
     - Primary Country
     - Key Entities (People/Organizations)
     - Sentiment Score (-1.0 to 1.0)
     - Sentiment Label (positive/neutral/negative)
  3. **Storage**: Parses the LLM's JSON response and inserts the enriched document directly into the MongoDB collection.
- **Resilience**: Features automatic fallback to mock/synthetic data generation if default API keys are detected, and gracefully handles JSON decode errors or LLM service unavailability (e.g. 503 errors during high demand).

### 3. Next.js Dashboard (`pulse_dashboard`)
- **Environment**: Node.js 20 Alpine, Next.js (App Router)
- **Port**: `3000`
- **Role**: The frontend visualization layer.
- **Backend API**: Exposes a Serverless Route (`/api/sentiment`) that uses the native MongoDB Node.js driver to fetch the latest 500 documents sorted by `_id` descending.
- **Frontend UI**:
  - Built with React (Client Components).
  - Automatically polls the `/api/sentiment` endpoint every 30 seconds for live updates.
  - Utilizes `Recharts` for data visualization, rendering a Sentiment Breakdown Donut Chart and a Top Mentions by Country Bar Chart.
  - Styled with TailwindCSS using a modern, dark-themed, glassmorphism aesthetic.

## Execution & Management
- **Startup Script (`run.ps1`)**: A PowerShell wrapper that validates Docker's state and uses `docker compose up --build -d` to launch the environment. It supports a `-Mock` flag to inject synthetic data for testing.
- **State Management**: Stopping the app using `docker compose down` preserves the database volume. Using `docker compose down -v` destroys the volume, effectively resetting the database state for the next run.
