# 🌍 AI Global Pulse Dashboard

A real-time global intelligence dashboard that scrapes live news feeds, processes the text through a Natural Language Processing (NLP) pipeline, and visualizes global sentiment across 2D, 3D, and interactive map formats.

## 🏗️ System Architecture

The end-to-end data flow operates through a robust ETL (Extract, Transform, Load) pipeline, pulling live unstructured data and structuring it for immediate analytical presentation.

```text
+----------------+      +--------------------------+      +----------------+      +--------------------+
|                |      |                          |      |                |      |                    |
|  NewsAPI /     | ---> |   Agentic NLP Pipeline   | ---> |   MongoDB      | ---> |  Streamlit App     |
|  Live Feeds    |      |   (LLM Extraction)       |      |   (Storage)    |      |  (Presentation)    |
|  (Ingestion)   |      |   (Transformation)       |      |                |      |                    |
+----------------+      +--------------------------+      +----------------+      +--------------------+
                              |                                ^                           |
                              |   Extracts Title, Country,     |                           |
                              |   Sentiment, and Entities      |                           v
                              +--------------------------------+                  Interactive Analytics
                                                                                  & Geo-Spatial Views
```

## 🧠 Data Engineering Concepts Demonstrated

This project is built around modern data engineering best practices:

* **ETL Design & Agentic Transformation**: Demonstrates an advanced extraction layer where an LLM is used as a data transformer. It takes unstructured article text and rigidly coerces it into a predefined, strictly-typed JSON schema.
* **Schema-Free Document Modeling (NoSQL)**: Utilizes MongoDB for storage, capitalizing on its flexibility for storing nested JSON (like arrays of extracted entities) and its ability to rapidly handle incoming unstructured or semi-structured data without rigid migrations.
* **Error Handling & Defensive Loading**: The pipeline implements strict validation for both HTTP requests (timeouts, retries) and LLM outputs. It strips bad markdown, gracefully catches JSON decode errors, and prevents malformed data from crashing the ingestion loop. 
* **Containerization**: Fully containerized using Docker and Docker Compose. This encapsulates the backend pipeline, the presentation layer, and the database into a unified, easily reproducible environment.
* **Mock/Simulation Capabilities**: Provides a `--mock` CLI flag to simulate API calls and data ingestion, ensuring reliable presentation and testing even when network constraints or rate limits apply.

## 🚀 Quickstart Guide

You can launch the complete end-to-end system (MongoDB database, data pipeline, and interactive dashboard) using Docker Compose.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/YourRepoName.git
   cd YourRepoName
   ```

2. **Configure Environment (Optional for Live Mode):**
   If you intend to run the live extraction pipeline, provide your API keys in a `.env` file or directly inside `docker-compose.yml`:
   ```env
   NEWS_API_KEY=your_newsapi_key_here
   LLM_API_KEY=your_llm_api_key_here
   ```

3. **Start the System:**
   Build and start the containers using Docker Compose:
   ```bash
   docker compose up --build
   ```

4. **Populate Mock Data (Recommended for Demos):**
   Once the containers are running, you can populate the database without needing live API keys or internet access by using the `--mock` flag. Open a new terminal and run:
   ```bash
   docker compose exec pulse_pipeline_worker python sentiment_pipeline.py --mock
   ```
   *(Alternatively, if you modified `docker-compose.yml` to include the `--mock` flag in the command, this step is handled automatically).*

5. **View the Dashboard:**
   Navigate to [http://localhost:8501](http://localhost:8501) in your browser to view the live dashboard rendering the data.

## 📂 Project Structure
* `app.py`: The main Streamlit application containing the UI, visualizations, and analytics logic.
* `sentiment_pipeline.py`: The background ETL script that handles data ingestion, LLM interaction, and database insertion.
* `Dockerfile` / `docker-compose.yml`: Containerization instructions for a reproducible environment.
* `requirements.txt`: Python package dependencies.
