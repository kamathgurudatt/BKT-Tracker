import logging
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

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


def _celery_redis_url(url: str) -> str:
    if not url.startswith("rediss://"):
        return url

    parsed = urlsplit(url)
    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query_params["ssl_cert_reqs"] = "required"
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query_params), parsed.fragment))


if not settings.redis_url:
    raise RuntimeError("REDIS_URL is required for Celery worker startup.")

celery_redis_url = _celery_redis_url(settings.redis_url)
celery_app = Celery("sentinel", broker=celery_redis_url, backend=celery_redis_url, include=["app.workers.tasks"])
celery_app.conf.beat_schedule = {
    "dispatch-due-monitoring-jobs": {"task": "app.workers.tasks.dispatch_due_jobs", "schedule": 60.0},
}
celery_app.conf.timezone = "UTC"
celery_app.conf.broker_connection_retry_on_startup = True

logger.info("Celery initialized.")
logger.info("Celery broker configured: %s", _mask_redis_url(celery_redis_url))
logger.info("Celery result backend configured: %s", _mask_redis_url(celery_redis_url))
