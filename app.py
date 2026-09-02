import streamlit as st
import pandas as pd
import plotly.express as px  # type: ignore
import pydeck as pdk
from pymongo import MongoClient  # type: ignore
import json
import os

# --- INITIALIZATION ---
st.set_page_config(page_title="AI Global Pulse", page_icon="🌐", layout="wide")

# CSS Injection for Theme
theme_css = """
<style>
/* Stats Cards */
div[data-testid="stMetric"] {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 24px !important;
    height: 160px !important;
    width: 100% !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    margin-bottom: 16px;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(255, 140, 0, 0.2);
    border-color: #FF8C00;
}

div[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: bold;
    color: #FFFFFF;
}

div[data-testid="stMetricLabel"] {
    color: #AAAAAA !important;
    font-size: 1rem !important;
    margin-bottom: 8px;
}
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

# Hardcoded Geocoding Dictionary
GEO_DICT = {
    "USA": (37.09, -95.71), "United States": (37.09, -95.71), 
    "UK": (55.37, -3.43), "United Kingdom": (55.37, -3.43), 
    "France": (46.22, 2.21), "Germany": (51.16, 10.45),
    "India": (20.59, 78.96), "China": (35.86, 104.19),
    "Russia": (61.52, 105.31), "Japan": (36.20, 138.25), 
    "Brazil": (-14.23, -51.92), "Canada": (56.13, -106.34), 
    "Australia": (-25.27, 133.77), "Israel": (31.04, 34.85), 
    "Ukraine": (48.37, 31.16), "Iran": (32.42, 53.68), 
    "Saudi Arabia": (23.88, 45.07), "South Africa": (-30.55, 22.93), 
    "Mexico": (23.63, -102.55), "Italy": (41.87, 12.56), 
    "Spain": (40.46, -3.74), "South Korea": (35.90, 127.76), 
    "North Korea": (40.33, 127.51), "Egypt": (26.82, 30.80),
    "Turkey": (38.96, 35.24), "Pakistan": (30.37, 69.34),
    "Afghanistan": (33.93, 67.70), "Iraq": (33.22, 43.67), 
    "Syria": (34.80, 38.99), "Lebanon": (33.85, 35.86), 
    "Yemen": (15.55, 48.51), "Nigeria": (9.08, 8.67), 
    "Kenya": (-1.29, 36.82), "Argentina": (-38.41, -63.61), 
    "Colombia": (4.57, -74.29), "Venezuela": (6.42, -66.58),
    "Indonesia": (-0.78, 113.92), "Malaysia": (4.21, 101.97), 
    "Singapore": (1.35, 103.81), "Philippines": (12.87, 121.77), 
    "Vietnam": (14.05, 108.27), "Thailand": (15.87, 100.99), 
    "Europe": (54.52, 15.25), "Asia": (34.04, 100.61), "Africa": (-8.78, 34.50),
    "North America": (54.52, -105.25), "South America": (-8.78, -55.49), 
    "Taiwan": (23.69, 120.96), "Ireland": (53.14, -7.69), 
    "Sweden": (60.12, 18.64), "Norway": (60.47, 8.46), "Finland": (61.92, 25.74)
}

# --- DATA FETCHING ---
@st.cache_data(ttl=60)
def fetch_mongodb_data():
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        # Verify connection
        client.admin.command('ping')
        db = client["pulse_db"]
        collection = db["global_sentiment"]
        
        # Fetch latest 500 documents sorted descending by _id (implicit insertion order)
        cursor = collection.find().sort([("_id", -1)]).limit(500)
        docs = list(cursor)
        
        if not docs:
            return pd.DataFrame()
            
        # Convert _id to string for dataframe compatibility
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
                
        df = pd.DataFrame(docs)
        
        # Apply Geocoding transformation for the map
        def map_coords(country_name):
            if not country_name or pd.isna(country_name):
                return None, None
            # case insensitive match
            for k, v in GEO_DICT.items():
                if k.lower() == str(country_name).lower():
                    return v[0], v[1]
            return None, None
            
        if "country" in df.columns:
            df[["Latitude", "Longitude"]] = df["country"].apply(lambda c: pd.Series(map_coords(c)))
            
        return df
    except Exception as e:
        return None

# Sidebar
with st.sidebar:
    st.markdown("## 🌐 Global Pulse Controls")
    
    if st.button("Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()
        
    st.divider()
    st.markdown("### Legend")
    st.markdown("<span style='color: #50dc64;'>■</span> Positive<br><span style='color: #dc3232;'>■</span> Negative<br><span style='color: #FAEB92;'>■</span> Neutral", unsafe_allow_html=True)

# Main Title
st.markdown("<h1 style='color: #F08D39; text-align: center;'>AI Global Pulse Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #FAEB92; font-size: 1.2rem; margin-top: 0px; margin-bottom: 2rem;'>Real-time sentiment intelligence across the world's news cycle</div>", unsafe_allow_html=True)

# Fetch Data
df = fetch_mongodb_data()

# Defensive UI
if df is None:
    st.warning("⚠️ Unable to connect to MongoDB. Is the local instance (localhost:27017) running?")
    st.stop()
elif df.empty:
    st.warning("⚠️ The database is currently empty. The data ingestion pipeline has not populated data yet. Run `python sentiment_pipeline.py` to ingest live news.")
    st.stop()

# --- METRICS LAYER ---
col1, col2, col3, col4, col5 = st.columns(5)
total_articles = len(df)
avg_sentiment = df['sentiment_score'].mean() if 'sentiment_score' in df.columns else 0

pos_count = len(df[df['sentiment_label'] == 'positive']) if 'sentiment_label' in df.columns else 0
neu_count = len(df[df['sentiment_label'] == 'neutral']) if 'sentiment_label' in df.columns else 0
neg_count = len(df[df['sentiment_label'] == 'negative']) if 'sentiment_label' in df.columns else 0

col1.metric("Total Articles", total_articles)
col2.metric("Average Sentiment", f"{avg_sentiment:.2f}")
col3.metric("Positive Count", pos_count)
col4.metric("Neutral Count", neu_count)
col5.metric("Negative Count", neg_count)

st.divider()

# --- VISUALIZATIONS ---
tab1, tab2, tab3 = st.tabs(["Global Map", "Sentiment Analytics", "Data Explorer"])

with tab1:
    st.subheader("Global News Sentiment Map")
    map_df = df.dropna(subset=['Latitude', 'Longitude']).copy()
    
    if not map_df.empty:
        def get_color(label):
            if label == "positive": return [0, 255, 128, 200]
            elif label == "negative": return [255, 69, 0, 200]
            else: return [255, 180, 0, 200]
            
        map_df['Color'] = map_df['sentiment_label'].apply(get_color)
        
        map_data = json.loads(map_df.to_json(orient='records'))
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            map_data,
            get_position=["Longitude", "Latitude"],
            get_color="Color",
            get_radius=80000,
            radius_min_pixels=10,
            radius_max_pixels=30,
            pickable=True,
            filled=True,
            stroked=True,
            get_line_color=[255, 255, 255, 150]
        )
        view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.5)
        st.pydeck_chart(pdk.Deck(
            layers=[layer], 
            initial_view_state=view_state,
            map_style="dark",
            tooltip={"text": "{title}\\nSentiment: {sentiment_score}\\nCountry: {country}"}
        ))
    else:
        st.info("No recognizable country coordinates to display on the map.")

with tab2:
    st.subheader("Sentiment Insights")
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        if 'sentiment_label' in df.columns:
            pie_df = df['sentiment_label'].value_counts().reset_index()
            pie_df.columns = ['Label', 'Count']
            color_map = {'positive': '#48C9B0', 'negative': '#FF6B6B', 'neutral': '#F9E79F'}
            fig_pie = px.pie(
                pie_df, values='Count', names='Label', 
                title="Sentiment Breakdown", 
                color='Label', color_discrete_map=color_map, 
                hole=0.4,
                template="plotly_dark"
            )
            fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with row1_col2:
        if 'country' in df.columns:
            bar_df = df['country'].dropna().value_counts().head(10).reset_index()
            bar_df.columns = ['Country', 'Count']
            bar_df = bar_df.sort_values(by='Count', ascending=True)
            
            fig_bar = px.bar(
                bar_df, x='Count', y='Country', orientation='h', 
                title="Top 10 Mentioned Countries", 
                template="plotly_dark",
                color_discrete_sequence=['#F08D39']
            )
            fig_bar.update_xaxes(showgrid=False)
            fig_bar.update_yaxes(showgrid=False)
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    st.subheader("Interactive Data Table")
    # Clean up the entities array so it displays nicely in the dataframe
    display_df = df.copy()
    if 'entities' in display_df.columns:
        display_df['entities'] = display_df['entities'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        
    cols_to_show = ['title', 'country', 'sentiment_score', 'sentiment_label', 'entities']
    # Filter to only existing columns
    cols_to_show = [c for c in cols_to_show if c in display_df.columns]
    
    st.dataframe(
        display_df[cols_to_show],
        use_container_width=True,
        hide_index=True
    )