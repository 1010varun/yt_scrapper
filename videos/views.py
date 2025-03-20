from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import Video
from .serializers import VideoSerializer
from django.conf import settings
import logging
from videos.tasks import fetch_youtube_videos, ensure_periodic_task

logger = logging.getLogger(__name__)

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class VideoListView(generics.ListAPIView):
    serializer_class = VideoSerializer
    pagination_class = StandardPagination
    
    def get_queryset(self):
        query = self.request.query_params.get('q', settings.SEARCH_QUERY)
        logger.info(f"Processing request for videos with query: {query}")

        queryset = Video.objects.filter(search_query=query).order_by('-published_at')

        if not queryset.exists():
            logger.info(f"No videos found for query: {query}, triggering immediate fetch")
            fetch_youtube_videos(query)
            ensure_periodic_task(query)

            queryset = Video.objects.filter(search_query=query).order_by('-published_at')

        return queryset