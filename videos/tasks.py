from celery import shared_task
import requests
from django.conf import settings
from .models import Video
from datetime import datetime
from django.core.cache import cache
import logging
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

logger = logging.getLogger(__name__)

@shared_task
def fetch_youtube_videos(search_query=None):
    query = search_query or settings.SEARCH_QUERY
    logger.info(f"Running fetch for query: {query}")
    
    ensure_periodic_task(query)
    
    cache_key = f"youtube_page_token_{query}"
    page_token = cache.get(cache_key, None)

    print(settings.YOUTUBE_API_KEY)
    
    url = (
        f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}"
        f"&maxResults=10&order=date&type=video&key=AIzaSyBAO-9nVB40Fl146SzLDywXUZ_e9KuE9u0"
    )
    if page_token:
        url += f"&pageToken={page_token}"

    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }

    try:
        logger.info(f"Fetching videos for query: {query}, pageToken: {page_token}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        items = data.get('items', [])
        logger.info(f"Fetched {len(items)} videos for query: {query}")
        
        new_videos = []
        for video in items:
            video_id = video['id']['videoId']
            if not Video.objects.filter(video_id=video_id).exists():
                try:
                    published_at = datetime.strptime(
                        video['snippet']['publishedAt'], 
                        '%Y-%m-%dT%H:%M:%SZ'
                    )
                    new_videos.append(Video(
                        video_id=video_id,
                        title=video['snippet']['title'],
                        description=video['snippet']['description'],
                        published_at=published_at,
                        thumbnail_url=video['snippet']['thumbnails']['default']['url'],
                        search_query=query
                    ))
                except (KeyError, ValueError) as e:
                    logger.error(f"Error processing video {video_id}: {e}")
        if new_videos:
            Video.objects.bulk_create(new_videos)
            logger.info(f"Added {len(new_videos)} new videos for query: {query}")
        
        next_page_token = data.get('nextPageToken')
        if next_page_token:
            cache.set(cache_key, next_page_token, timeout=None)
            logger.info(f"Stored nextPageToken: {next_page_token} for query: {query}")
        else:
            cache.delete(cache_key)
            logger.info(f"No more pages for query: {query}, cleared cache")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching YouTube videos for {query}: {e}")

def ensure_periodic_task(query):
    task_name = f'fetch_videos_{query}'
    if not PeriodicTask.objects.filter(name=task_name).exists():
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=10,
            period=IntervalSchedule.SECONDS
        )
        PeriodicTask.objects.create(
            interval=schedule,
            name=task_name,
            task='videos.tasks.fetch_youtube_videos',
            args=json.dumps([query])
        )
        logger.info(f"Added new periodic task for query: {query}")