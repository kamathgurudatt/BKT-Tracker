import logging
from urllib.parse import urlsplit, urlunsplit

from celery import Celery

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def _mask_redis_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.password:
        netloc = parsed.netloc.replace(parsed.password, "***")
    else:
        netloc = parsed.netloc
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


if not settings.redis_url:
    raise RuntimeError("REDIS_URL is required for Celery worker startup.")

celery_app = Celery("sentinel", broker=settings.redis_url, backend=settings.redis_url, include=["app.workers.tasks"])
celery_app.conf.beat_schedule = {
    "dispatch-due-monitoring-jobs": {"task": "app.workers.tasks.dispatch_due_jobs", "schedule": 60.0},
}
celery_app.conf.timezone = "UTC"
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.worker_pool = "solo"

logger.info("Celery initialized.")
logger.info("Celery broker configured: %s", _mask_redis_url(settings.redis_url))
logger.info("Celery result backend configured: %s", _mask_redis_url(settings.redis_url))
