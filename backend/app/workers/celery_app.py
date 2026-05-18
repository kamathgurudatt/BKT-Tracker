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

# Railway worker hardening: native dependencies used by Playwright/Chromium and
# async database drivers are safer when worker memory/concurrency is bounded and
# child processes are periodically recycled.
celery_app.conf.worker_pool = settings.celery_worker_pool
celery_app.conf.worker_concurrency = settings.celery_worker_concurrency
celery_app.conf.worker_max_tasks_per_child = settings.celery_worker_max_tasks_per_child
celery_app.conf.worker_prefetch_multiplier = settings.celery_worker_prefetch_multiplier
celery_app.conf.task_time_limit = settings.celery_task_time_limit_seconds
celery_app.conf.task_soft_time_limit = settings.celery_task_soft_time_limit_seconds
celery_app.conf.task_acks_late = True
celery_app.conf.task_reject_on_worker_lost = True

logger.info(
    "Celery initialized pool=%s concurrency=%s max_tasks_per_child=%s prefetch=%s time_limit=%s",
    settings.celery_worker_pool,
    settings.celery_worker_concurrency,
    settings.celery_worker_max_tasks_per_child,
    settings.celery_worker_prefetch_multiplier,
    settings.celery_task_time_limit_seconds,
)
logger.info("Celery broker configured: %s", _mask_redis_url(settings.redis_url))
logger.info("Celery result backend configured: %s", _mask_redis_url(settings.redis_url))
