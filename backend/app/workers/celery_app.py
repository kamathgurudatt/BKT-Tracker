from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("sentinel", broker=settings.redis_url, backend=settings.redis_url, include=["app.workers.tasks"])
celery_app.conf.beat_schedule = {
    "dispatch-due-monitoring-jobs": {"task": "app.workers.tasks.dispatch_due_jobs", "schedule": 60.0},
}
celery_app.conf.timezone = "UTC"
