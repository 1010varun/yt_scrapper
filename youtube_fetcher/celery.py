from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
import logging

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youtube_fetcher.settings')
app = Celery('youtube_fetcher')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks(['videos'])

@app.on_after_finalize.connect

def setup_periodic_tasks(sender, **kwargs):
    from videos.tasks import ensure_periodic_task
    from videos.models import Video

    unique_queries = Video.objects.values_list('search_query', flat=True).distinct()
    for query in unique_queries:
        ensure_periodic_task(query)

    logger.info("Celery Beat configured with initial tasks")