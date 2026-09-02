# AI Global Pulse Dashboard

A real-time global intelligence dashboard that collects live news feeds, processes text through a Natural Language Processing (NLP) pipeline, and visualizes global sentiment using interactive map and chart formats.

## System Architecture

The data flow operates through an ETL (Extract, Transform, Load) pipeline, pulling unstructured data and structuring it for analytical presentation.

```text
+----------------+      +--------------------------+      +----------------+      +--------------------+
|                |      |                          |      |                |      |                    |
|  NewsAPI /     | ---> |   Agentic NLP Pipeline   | ---> |   MongoDB      | ---> |  Next.js App       |
|  Live Feeds    |      |   (LLM Extraction)       |      |   (Storage)    |      |  (Presentation)    |
|  (Ingestion)   |      |   (Transformation)       |      |                |      |                    |
+----------------+      +--------------------------+      +----------------+      +--------------------+
                              |                                ^                           |
                              |   Extracts Title, Country,     |                           |
                              |   Sentiment, and Entities      |                           v
                              +--------------------------------+                  Interactive Analytics
                                                                                  & Geo-Spatial Views
```

## Data Engineering Concepts Demonstrated

* **ETL Design and Transformation**: Uses a Large Language Model (LLM) as a data transformer to convert unstructured text into a predefined JSON schema.
* **Schema-Free Document Modeling (NoSQL)**: Uses MongoDB for flexible storage of nested JSON data, such as arrays of extracted entities.
* **Error Handling**: Includes validation for HTTP requests and LLM outputs to prevent malformed data from stopping the pipeline.
* **Containerization**: Fully containerized using Docker and Docker Compose for a consistent environment.
* **Simulation Capabilities**: Includes a `--mock` command line flag to simulate API calls, allowing for testing and presentation without network dependencies or rate limits.

---

## Getting Started

The project uses Docker for a simplified setup process. Automation scripts are included for Windows users.

### Prerequisites
* **Docker Desktop**: Ensure Docker is installed and running on your system.
* **API Keys (Optional)**: To use live data instead of mock data, you need a [NewsAPI Key](https://newsapi.org/) and an OpenAI-compatible LLM API Key.

### 1. Project Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/YourRepoName.git
   cd YourRepoName
   ```

2. **Configure Environment Variables (Live Mode Only):**
   If you plan to use live data extraction, create a `.env` file in the root directory (or edit `docker-compose.yml`) and add your keys:
   ```env
   NEWS_API_KEY=your_newsapi_key_here
   LLM_API_KEY=your_llm_api_key_here
   ```
   *Note: If you only want to test the application, you can skip this step and use Mock mode during execution.*

### 2. Running the Application

For Windows users, use the provided automation scripts (`run.bat` or `run.ps1`) to build, start, and run the data pipeline.

**Option A: Automated Start (Windows)**
1. Open PowerShell in the project directory.
2. To run with **synthetic mock data** (Recommended for quick testing):
   ```powershell
   .\run.ps1 -Mock
   ```
3. To run in **live mode** (Requires API keys):
   ```powershell
   .\run.ps1
   ```
*(Alternatively, you can double-click `run.bat` to launch the live mode interactively).*

**Option B: Manual Docker Start (Any OS)**
1. Build and start the containers in detached mode:
   ```bash
   docker compose up --build -d
   ```
2. (Optional) Run the pipeline in mock mode to inject synthetic data:
   ```bash
   docker compose exec pulse_pipeline_worker python sentiment_pipeline.py --mock
   ```

### 3. Viewing the Dashboard
Once the containers are running, open your web browser and navigate to:
**[http://localhost:3000](http://localhost:3000)**

To stop the application, run:
```bash
docker compose down
```

---

## Project Structure
* `frontend/`: Next.js application UI, visualizations, and analytics logic.
* `backend/`: Background ETL scripts, Dockerfile, and Python dependencies.
* `docker-compose.yml`: Containerization configuration.
* `run.ps1` & `run.bat`: Helper scripts for automated setup and execution.
