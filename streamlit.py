import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import altair as alt

st.set_page_config(
    page_title="YouTube Videos Dashboard",
    page_icon="🎥",
    layout="wide",
)

API_URL = "http://localhost:8000/api/videos"

@st.cache_data(ttl=60)
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

def prepare_data(videos):
    if not videos:
        return pd.DataFrame()
    
    df = pd.DataFrame(videos)
    df['published_at'] = pd.to_datetime(df['published_at'])
    df['published_date'] = df['published_at'].dt.date
    return df

st.title("🎥 YouTube Videos Dashboard")

st.sidebar.header("Filters")

default_query = 'bgmi'
search_query = st.sidebar.text_input("Search Query", value=default_query)

today = datetime.now().date()
max_date = today
min_date = today - timedelta(days=30)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

sort_options = st.sidebar.radio(
    "Sort By",
    ["Latest First", "Oldest First"]
)

with st.spinner("Fetching videos..."):
    videos_data = fetch_videos(search_query)
    videos = videos_data.get('results', [])
    total_count = videos_data.get('count', 0)
    
    if not videos:
        st.info(f"No videos found for query: {search_query}")
    else:
        st.success(f"Found {total_count} videos for query: {search_query}")

df = prepare_data(videos)

if not df.empty:
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['published_date'] >= start_date) & (df['published_date'] <= end_date)]
    
    if sort_options == "Latest First":
        df = df.sort_values('published_at', ascending=False)
    else:
        df = df.sort_values('published_at', ascending=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Videos", len(df))
    with col2:
        st.metric("Date Range", f"{df['published_date'].min()} to {df['published_date'].max()}")
    with col3:
        st.metric("Unique Channels", len(df['title'].unique()))
    
    if len(df) > 0:
        st.subheader("Videos by Date")
        chart_data = df.groupby('published_date').size().reset_index(name='count')
        chart = alt.Chart(chart_data).mark_bar().encode(
            x='published_date:T',
            y='count:Q',
            tooltip=['published_date', 'count']
        ).properties(height=200)
        st.altair_chart(chart, use_container_width=True)
    
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