# 🌍 AI Global Pulse Dashboard

A real-time global intelligence dashboard that scrapes live news feeds, processes the text through a Natural Language Processing (NLP) pipeline, and visualizes global sentiment across 2D, 3D, and interactive map formats. 

## 🚀 Features
* **Live News Ingestion:** Dynamically scrapes the latest articles from major global RSS feeds (BBC, CNN, Al Jazeera, etc.).
* **NLP Pipeline:** * **Sentiment Analysis:** Utilizes TextBlob to calculate `Sentiment_Score` (-1.0 to 1.0) and `Subjectivity_Score` (0.0 to 1.0) for every article summary.
  * **Named Entity Recognition (NER):** Uses spaCy (`en_core_web_sm`) to extract geopolitical entities (GPE), People, and Organizations from the text.
* **Geocoding:** Maps extracted locations to exact Latitude/Longitude coordinates.
* **Advanced Visualizations:** * Interactive 3D Scatter Clustering (Sentiment vs. Subjectivity vs. Word Count).
  * Real-time Sentiment Area Charts and Objectivity Quadrants.
  * Global PyDeck Map plotting news intensity and mood by region.
* **Custom Dark UI:** Built with a fully customized, high-contrast dark theme optimized for data readability.

## 🛠️ Tech Stack
* **Core:** Python, Pandas
* **Frontend:** Streamlit
* **NLP:** spaCy, TextBlob
* **Geocoding:** Geopy
* **Data Visualization:** Plotly Express, PyDeck

## 💻 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YourUsername/YourRepoName.git](https://github.com/YourUsername/YourRepoName.git)
   cd YourRepoName
