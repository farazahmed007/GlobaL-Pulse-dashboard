import streamlit as st
import pandas as pd
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import spacy
import plotly.express as px
import pydeck as pdk
import requests
import datetime
import json
import time

# --- INITIALIZATION ---
st.set_page_config(page_title="AI Global Pulse", page_icon="🌐", layout="wide")

# CSS Injection for Theme
theme_css = """
<style>


/* Cards & Surfaces */
div[data-testid="stMetric"], div.stChatFloatingInputContainer {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 8px;
    padding: 10px;
}
/* Chat bubbles */
div[data-testid="stChatMessage"] {
    background-color: #0d0d0d;
    border: 1px solid #9929EA;
    border-radius: 8px;
}
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

# Spacy Load
@st.cache_resource
def load_spacy():
    try:
        return spacy.load("en_core_web_sm")
    except Exception as e:
        st.error("spaCy model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
        return None

nlp = load_spacy()
analyzer = SentimentIntensityAnalyzer()

# Hardcoded Geocoding Dictionary
GEO_DICT = {
    "USA": (37.09, -95.71), "United States": (37.09, -95.71), "Washington": (38.90, -77.03), "New York": (40.71, -74.00), "London": (51.50, -0.12),
    "UK": (55.37, -3.43), "United Kingdom": (55.37, -3.43), "France": (46.22, 2.21), "Paris": (48.85, 2.35), "Germany": (51.16, 10.45),
    "Berlin": (52.52, 13.40), "India": (20.59, 78.96), "New Delhi": (28.61, 77.20), "Mumbai": (19.07, 72.87), "China": (35.86, 104.19),
    "Beijing": (39.90, 116.40), "Russia": (61.52, 105.31), "Moscow": (55.75, 37.61), "Japan": (36.20, 138.25), "Tokyo": (35.67, 139.65),
    "Brazil": (-14.23, -51.92), "Brasilia": (-15.82, -47.92), "Canada": (56.13, -106.34), "Ottawa": (45.42, -75.69), "Australia": (-25.27, 133.77),
    "Canberra": (-35.28, 149.13), "Sydney": (-33.86, 151.20), "Israel": (31.04, 34.85), "Jerusalem": (31.76, 35.21), "Gaza": (31.50, 34.46),
    "Ukraine": (48.37, 31.16), "Kyiv": (50.45, 30.52), "Iran": (32.42, 53.68), "Tehran": (35.68, 51.38), "Saudi Arabia": (23.88, 45.07),
    "Riyadh": (24.71, 46.67), "South Africa": (-30.55, 22.93), "Pretoria": (-25.74, 28.18), "Cape Town": (-33.92, 18.42), "Mexico": (23.63, -102.55),
    "Mexico City": (19.43, -99.13), "Italy": (41.87, 12.56), "Rome": (41.90, 12.49), "Spain": (40.46, -3.74), "Madrid": (40.41, -3.70),
    "South Korea": (35.90, 127.76), "Seoul": (37.56, 126.97), "North Korea": (40.33, 127.51), "Pyongyang": (39.03, 125.76), "Egypt": (26.82, 30.80),
    "Cairo": (30.04, 31.23), "Turkey": (38.96, 35.24), "Ankara": (39.93, 32.85), "Istanbul": (41.00, 28.97), "Pakistan": (30.37, 69.34),
    "Islamabad": (33.68, 73.04), "Afghanistan": (33.93, 67.70), "Kabul": (34.55, 69.20), "Iraq": (33.22, 43.67), "Baghdad": (33.31, 44.36),
    "Syria": (34.80, 38.99), "Damascus": (33.51, 36.29), "Lebanon": (33.85, 35.86), "Beirut": (33.89, 35.50), "Yemen": (15.55, 48.51),
    "Sanaa": (15.36, 44.19), "Nigeria": (9.08, 8.67), "Abuja": (9.07, 7.39), "Kenya": (-1.29, 36.82), "Nairobi": (-1.29, 36.82),
    "Argentina": (-38.41, -63.61), "Buenos Aires": (-34.60, -58.38), "Colombia": (4.57, -74.29), "Bogota": (4.71, -74.07), "Venezuela": (6.42, -66.58),
    "Caracas": (10.48, -66.90), "Indonesia": (-0.78, 113.92), "Jakarta": (-6.20, 106.81), "Malaysia": (4.21, 101.97), "Kuala Lumpur": (3.13, 101.68),
    "Singapore": (1.35, 103.81), "Philippines": (12.87, 121.77), "Manila": (14.59, 120.98), "Vietnam": (14.05, 108.27), "Hanoi": (21.02, 105.83),
    "Thailand": (15.87, 100.99), "Bangkok": (13.75, 100.50), "Europe": (54.52, 15.25), "Asia": (34.04, 100.61), "Africa": (-8.78, 34.50),
    "North America": (54.52, -105.25), "South America": (-8.78, -55.49), "Taiwan": (23.69, 120.96), "Taipei": (25.03, 121.56),
    "Hong Kong": (22.31, 114.16), "Dublin": (53.34, -6.26), "Ireland": (53.14, -7.69), "Scotland": (56.49, -4.20), "Wales": (52.13, -3.78),
    "Sweden": (60.12, 18.64), "Stockholm": (59.32, 18.06), "Norway": (60.47, 8.46), "Oslo": (59.91, 10.75), "Finland": (61.92, 25.74), "Helsinki": (60.16, 24.93)
}

# --- PHASE 1: DATA ENGINE ---
@st.cache_data(ttl=3600)
def fetch_data():
    feeds = {
        "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "Reuters": "https://feeds.reuters.com/reuters/topNews",
        "CNN": "http://rss.cnn.com/rss/edition_world.rss",
        "Times of India": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    }
    
    articles = []
    
    progress_bar = st.progress(0, text="Fetching Live News Feeds...")
    
    for i, (source, url) in enumerate(feeds.items()):
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]: # 20 * 5 = 100
                articles.append({
                    "Date": entry.get("published", datetime.datetime.now().isoformat()),
                    "Title": entry.get("title", ""),
                    "Summary": entry.get("summary", ""),
                    "URL": entry.get("link", ""),
                    "Source": source
                })
        except Exception as e:
            continue
        progress_bar.progress((i + 1) / len(feeds), text=f"Fetched {source}...")
            
    progress_bar.progress(1.0, text="Processing Data...")
    df = pd.DataFrame(articles)
    
    # Handle dates
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Date'] = df['Date'].dt.date
    
    # Sentiment & NLP
    def analyze_row(row):
        text = row['Title'] + ". " + row['Summary']
        
        # VADER Sentiment
        vs = analyzer.polarity_scores(text)
        sentiment_score = vs['compound']
        
        if sentiment_score >= 0.05:
            sentiment_label = "Positive"
        elif sentiment_score <= -0.05:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"
            
        # Subjectivity
        blob = TextBlob(text)
        subjectivity_score = blob.sentiment.subjectivity
        
        # NER for Region
        region = None
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "GPE":
                    region = ent.text
                    break
                    
        word_count = len(row['Summary'].split())
        
        lat, lon = None, None
        if region and region in GEO_DICT:
            lat, lon = GEO_DICT[region]
        else:
            # Try to find any known region in the text as a fallback
            for k in GEO_DICT.keys():
                if k in text:
                    lat, lon = GEO_DICT[k]
                    region = k
                    break
        
        return pd.Series([sentiment_score, subjectivity_score, sentiment_label, region, lat, lon, word_count])

    if not df.empty:
        df[['Sentiment_Score', 'Subjectivity_Score', 'Sentiment_Label', 'Region', 'Latitude', 'Longitude', 'Word_Count']] = df.apply(analyze_row, axis=1)
        df = df.dropna(subset=['Latitude', 'Longitude'])
    
    progress_bar.empty()
    return df

# Fetch data and show toast
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

df_raw = fetch_data()

if not st.session_state.data_loaded:
    st.toast("✅ Data refreshed!", icon="✅")
    st.session_state.data_loaded = True

# --- PHASE 2: STREAMLIT SHELL ---
st.markdown("<h1 style='color: #F08D39; text-align: center;'>AI Global Pulse Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #FAEB92; font-size: 1.2rem; margin-top: 0px; margin-bottom: 2rem;'>Real-time sentiment intelligence across the world's news cycle</div>", unsafe_allow_html=True)

# Top Metrics
col1, col2, col3, col4, col5 = st.columns(5)
total_articles = len(df_raw)
avg_sentiment = df_raw['Sentiment_Score'].mean() if total_articles > 0 else 0
region_sentiment = df_raw.groupby('Region')['Sentiment_Score'].mean().reset_index()

most_negative_region = region_sentiment.loc[region_sentiment['Sentiment_Score'].idxmin()]['Region'] if not region_sentiment.empty else "N/A"
most_positive_region = region_sentiment.loc[region_sentiment['Sentiment_Score'].idxmax()]['Region'] if not region_sentiment.empty else "N/A"
most_active_source = df_raw['Source'].mode()[0] if not df_raw.empty else "N/A"

col1.metric("Total Articles Analyzed", total_articles)
col2.metric("Average Global Sentiment", f"{avg_sentiment:.2f}", delta=f"{avg_sentiment:.2f}", delta_color="normal")
col3.metric("Most Negative Region", most_negative_region)
col4.metric("Most Positive Region", most_positive_region)
col5.metric("Most Active Source", most_active_source)

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("## 🌐 Global Pulse Filters")
    st.status("🟢 Live Data", state="complete")
    
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()
        
    st.divider()
    
    sentiment_range = st.slider("Sentiment Range", -1.0, 1.0, (-1.0, 1.0))
    
    sources = df_raw['Source'].unique().tolist()
    selected_sources = st.multiselect("Source Filter", sources, default=sources)
    
    regions = df_raw['Region'].dropna().unique().tolist()
    selected_regions = st.multiselect("Region Filter", regions, default=regions)
    
    sentiment_focus = st.radio("Sentiment Focus", ["All", "Positive Only", "Negative Only", "Neutral Only"])
    
    valid_dates = df_raw['Date'].dropna()
    min_date = valid_dates.min() if not valid_dates.empty else datetime.date.today()
    max_date = valid_dates.max() if not valid_dates.empty else datetime.date.today()
    date_range = st.date_input("Date Range", [min_date, max_date])
    
    st.divider()
    st.markdown("### Legend")
    st.markdown("<span style='color: #50dc64;'>■</span> Positive<br><span style='color: #dc3232;'>■</span> Negative<br><span style='color: #FAEB92;'>■</span> Neutral", unsafe_allow_html=True)
    
    st.divider()
    st.write("Is this data accurate?")
    st.feedback("thumbs")

# Filtering Logic
df_filtered = df_raw.copy()

if not df_filtered.empty:
    df_filtered = df_filtered[
        (df_filtered['Sentiment_Score'] >= sentiment_range[0]) & 
        (df_filtered['Sentiment_Score'] <= sentiment_range[1]) &
        (df_filtered['Source'].isin(selected_sources)) &
        (df_filtered['Region'].isin(selected_regions))
    ]
    
    if len(date_range) == 2:
        df_filtered = df_filtered[(df_filtered['Date'] >= date_range[0]) & (df_filtered['Date'] <= date_range[1])]
        
    if sentiment_focus == "Positive Only":
        df_filtered = df_filtered[df_filtered['Sentiment_Label'] == "Positive"]
    elif sentiment_focus == "Negative Only":
        df_filtered = df_filtered[df_filtered['Sentiment_Label'] == "Negative"]
    elif sentiment_focus == "Neutral Only":
        df_filtered = df_filtered[df_filtered['Sentiment_Label'] == "Neutral"]

# --- PHASE 3: VISUALIZATIONS ---
tab1, tab2, tab3 = st.tabs(["Global Map", "Analytics", "Raw Data & Chat"])

with tab1:
    st.subheader("Live Sentiment Map")
    if not df_filtered.empty:
        # PyDeck ScatterplotLayer
        def get_color(label):
            if label == "Positive": return [80, 220, 100, 200]
            elif label == "Negative": return [220, 50, 50, 200]
            else: return [250, 235, 146, 200]
            
        map_df = df_filtered.copy()
        map_df['Color'] = map_df['Sentiment_Label'].apply(get_color)
        map_df['Radius'] = map_df['Word_Count'] * 80
        
        # Convert to native python types to avoid pydeck serialization error with numpy types
        import json
        map_data = json.loads(map_df.to_json(orient='records'))
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            map_data,
            get_position=["Longitude", "Latitude"],
            get_color="Color",
            get_radius="Radius",
            pickable=True
        )
        view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.5)
        st.pydeck_chart(pdk.Deck(
            layers=[layer], 
            initial_view_state=view_state,
            map_style="dark",
            tooltip={"text": "{Title}\nSource: {Source}\nSentiment: {Sentiment_Score}\nRegion: {Region}"}
        ))
        
        with st.expander("Top Headlines by Region"):
            for region in selected_regions:
                reg_df = df_filtered[df_filtered['Region'] == region].head(5)
                if not reg_df.empty:
                    st.markdown(f"**{region}**")
                    st.dataframe(reg_df[['Title', 'Source', 'Sentiment_Label']], hide_index=True)
    else:
        st.warning("No data matches current filters.")

with tab2:
    if not df_filtered.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("2D Analytics")
            # Bar Chart
            bar_df = df_filtered.groupby('Source')['Sentiment_Score'].mean().reset_index()
            fig_bar = px.bar(bar_df, x='Sentiment_Score', y='Source', orientation='h', title="Average Sentiment by Source", color='Sentiment_Score', color_continuous_scale="Purpor")
            fig_bar.update_layout(plot_bgcolor='#000000', paper_bgcolor='#000000', font_color='#FFFFFF')
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Line Chart
            line_df = df_filtered.groupby('Date').size().reset_index(name='Count')
            fig_line = px.line(line_df, x='Date', y='Count', title="Articles over Time", markers=True)
            fig_line.update_traces(line_color='#9929EA', fill='tozeroy')
            fig_line.update_layout(plot_bgcolor='#000000', paper_bgcolor='#000000', font_color='#FFFFFF')
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Pie Chart
            pie_df = df_filtered['Sentiment_Label'].value_counts().reset_index()
            pie_df.columns = ['Label', 'Count']
            color_map = {'Positive': '#50dc64', 'Negative': '#dc3232', 'Neutral': '#FAEB92'}
            fig_pie = px.pie(pie_df, values='Count', names='Label', title="Sentiment Distribution", color='Label', color_discrete_map=color_map, hole=0.4)
            fig_pie.update_layout(plot_bgcolor='#000000', paper_bgcolor='#000000', font_color='#FFFFFF')
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            st.subheader("3D News Intelligence Cluster")
            fig_3d = px.scatter_3d(
                df_filtered,
                x='Sentiment_Score',
                y='Subjectivity_Score',
                z='Word_Count',
                color='Sentiment_Label',
                size='Word_Count',
                hover_name='Title',
                hover_data=['Source', 'Region'],
                color_discrete_map={'Positive': '#50dc64', 'Negative': '#dc3232', 'Neutral': '#FAEB92'},
                title="3D News Intelligence Cluster"
            )
            fig_3d.update_layout(plot_bgcolor='#000000', paper_bgcolor='#000000', font_color='#FFFFFF')
            st.plotly_chart(fig_3d, use_container_width=True)
            
        st.subheader("Sentiment Heatmap by Region")
        # Bin sentiments
        bins = [-1.0, -0.6, -0.2, 0.2, 0.6, 1.0]
        labels = ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
        hm_df = df_filtered.copy()
        hm_df['Sentiment_Bin'] = pd.cut(hm_df['Sentiment_Score'], bins=bins, labels=labels, include_lowest=True)
        heatmap_data = hm_df.groupby(['Region', 'Sentiment_Bin']).size().unstack(fill_value=0)
        
        fig_hm = px.imshow(heatmap_data, text_auto=True, aspect="auto", color_continuous_scale="Purpor", title="Region vs Sentiment Heatmap")
        fig_hm.update_layout(plot_bgcolor='#000000', paper_bgcolor='#000000', font_color='#FFFFFF')
        st.plotly_chart(fig_hm, use_container_width=True)

with tab3:
    st.subheader("Raw Data Explorer")
    if not df_filtered.empty:
        st.data_editor(
            df_filtered[['Date', 'Title', 'Region', 'Source', 'Sentiment_Score', 'Sentiment_Label', 'URL']],
            use_container_width=True,
            column_config={
                "URL": st.column_config.LinkColumn("Article Link"),
                "Sentiment_Score": st.column_config.ProgressColumn(
                    "Sentiment",
                    help="Sentiment Score",
                    format="%f",
                    min_value=-1.0,
                    max_value=1.0,
                )
            },
            hide_index=True
        )
        
        st.markdown("### Top 10 Articles")
        for idx, row in df_filtered.head(10).iterrows():
            with st.expander(f"{row['Title']} ({row['Source']})"):
                st.write(row['Summary'])
                st.markdown(f"[Read full article]({row['URL']})")
                
        with st.popover("⬇Download Options"):
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="ai_global_pulse.csv", mime="text/csv")
            
            json_data = df_filtered.to_json(orient="records")
            st.download_button("Download JSON", data=json_data, file_name="ai_global_pulse.json", mime="application/json")
            
        st.divider()
        st.subheader("💬 Ask the Data")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        chat_query = st.chat_input("Ask about the news... e.g. 'Show me Europe' or 'Most negative today'")
        
        if chat_query:
            st.session_state.chat_history.append({"role": "user", "content": chat_query})
            with st.chat_message("user"):
                st.markdown(chat_query)
                
            with st.chat_message("assistant"):
                q = chat_query.lower()
                response = ""
                if "show me" in q:
                    region_req = q.replace("show me", "").strip()
                    res = df_filtered[df_filtered['Region'].str.lower() == region_req]
                    if not res.empty:
                        response = f"Top 3 headlines from {region_req.title()}:\n"
                        for _, r in res.head(3).iterrows():
                            response += f"- [{r['Title']}]({r['URL']})\n"
                    else:
                        response = f"No news found for region: {region_req.title()}"
                elif "most negative" in q:
                    res = df_filtered.sort_values(by="Sentiment_Score").head(3)
                    response = "Top 3 Most Negative Articles:\n"
                    for _, r in res.iterrows():
                        response += f"- [{r['Title']}]({r['URL']}) (Score: {r['Sentiment_Score']:.2f})\n"
                elif "most positive" in q:
                    res = df_filtered.sort_values(by="Sentiment_Score", ascending=False).head(3)
                    response = "Top 3 Most Positive Articles:\n"
                    for _, r in res.iterrows():
                        response += f"- [{r['Title']}]({r['URL']}) (Score: {r['Sentiment_Score']:.2f})\n"
                elif "summary" in q:
                    response = f"**Summary:**\n- Total Articles: {len(df_filtered)}\n- Average Sentiment: {df_filtered['Sentiment_Score'].mean():.2f}"
                else:
                    response = "Try: 'show me [Region]', 'most negative', 'most positive', 'summary'"
                    
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})