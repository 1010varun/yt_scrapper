import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import altair as alt
import os
# import environ

# Load environment variables
# env = environ.Env()
# env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
# environ.Env.read_env(env_file)

# Set page config
st.set_page_config(
    page_title="YouTube Videos Dashboard",
    page_icon="🎥",
    layout="wide",
)

# API URL
API_URL = "http://localhost:8000/api/videos"

# Function to fetch videos
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_videos(query=None, page=1, page_size=100):
    params = {'page': page, 'page_size': page_size}
    if query:
        params['q'] = query
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching videos: {e}")
        return {"results": [], "count": 0}

# Function to prepare data for visualization
def prepare_data(videos):
    if not videos:
        return pd.DataFrame()
    
    df = pd.DataFrame(videos)
    df['published_at'] = pd.to_datetime(df['published_at'])
    df['published_date'] = df['published_at'].dt.date
    return df

# Title
st.title("🎥 YouTube Videos Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

# Search query filter
default_query = 'bgmi'
# default_query = env('SEARCH_QUERY', default='bgmi')
search_query = st.sidebar.text_input("Search Query", value=default_query)

# Date range filter
today = datetime.now().date()
max_date = today
min_date = today - timedelta(days=30)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Sort options
sort_options = st.sidebar.radio(
    "Sort By",
    ["Latest First", "Oldest First"]
)

# Fetch videos
with st.spinner("Fetching videos..."):
    videos_data = fetch_videos(search_query)
    videos = videos_data.get('results', [])
    total_count = videos_data.get('count', 0)
    
    if not videos:
        st.info(f"No videos found for query: {search_query}")
    else:
        st.success(f"Found {total_count} videos for query: {search_query}")

# Prepare data
df = prepare_data(videos)

if not df.empty:
    # Apply date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['published_date'] >= start_date) & (df['published_date'] <= end_date)]
    
    # Apply sorting
    if sort_options == "Latest First":
        df = df.sort_values('published_at', ascending=False)
    else:
        df = df.sort_values('published_at', ascending=True)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Videos", len(df))
    with col2:
        st.metric("Date Range", f"{df['published_date'].min()} to {df['published_date'].max()}")
    with col3:
        st.metric("Unique Channels", len(df['title'].unique()))
    
    # Create a chart of videos by date
    if len(df) > 0:
        st.subheader("Videos by Date")
        chart_data = df.groupby('published_date').size().reset_index(name='count')
        chart = alt.Chart(chart_data).mark_bar().encode(
            x='published_date:T',
            y='count:Q',
            tooltip=['published_date', 'count']
        ).properties(height=200)
        st.altair_chart(chart, use_container_width=True)
    
    # Display videos
    st.subheader("Video List")
    for index, video in df.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(video['thumbnail_url'], width=120)
            with col2:
                st.markdown(f"**{video['title']}**")
                st.caption(f"Published: {video['published_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                with st.expander("Description"):
                    st.write(video['description'])
                st.markdown(f"[Watch on YouTube](https://www.youtube.com/watch?v={video['video_id']})")
            st.divider()
else:
    st.info("No videos found with the current filters.")