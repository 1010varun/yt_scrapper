from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class VideosConfig(AppConfig):
    name = 'videos'

    def ready(self):
        from django.conf import settings
        logger.info(f"Initialized beat schedule for default query: {settings.SEARCH_QUERY}")