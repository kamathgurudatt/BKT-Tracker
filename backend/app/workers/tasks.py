import asyncio
import logging
import socket
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import AsyncSessionLocal
from app.models.entities import JobStatus, MonitoringJob
from app.services.tracking import TrackingService
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run a coroutine safely regardless of whether an event loop is already running."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# FIX: _noop must be a regular sync task — Celery 5.x does not support native coroutine tasks
@celery_app.task
def _noop():
    return True


@celery_app.task(name="app.workers.tasks.dispatch_due_jobs")
def dispatch_due_jobs():
    try:
        return _run_async(_dispatch())
    except (socket.gaierror, SQLAlchemyError) as exc:
        logger.warning("dispatch_skipped_database_unavailable: %s", exc)
        return 0
    except Exception as exc:
        logger.warning("dispatch_skipped_runtime_error: %s", exc)
        return 0


async def _dispatch() -> int:
    count = 0
    async with AsyncSessionLocal() as db:
        jobs = (
            await db.scalars(
                select(MonitoringJob)
                .where(MonitoringJob.status == JobStatus.ACTIVE, MonitoringJob.next_run_at <= datetime.now(UTC))
                .limit(100)
            )
        ).all()
        for job in jobs:
            poll_job.delay(job.id)
            count += 1
    return count


@celery_app.task(name="app.workers.tasks.poll_job")
def poll_job(job_id: int):
    return _run_async(_poll(job_id))


async def _poll(job_id: int) -> int:
    async with AsyncSessionLocal() as db:
        job = await db.get(MonitoringJob, job_id)
        if not job:
            return 0
        try:
            await TrackingService().poll_once(db, job)
        except Exception as exc:
            job.failure_count += 1
            job.last_error = str(exc)[:1000]
            if job.failure_count >= 5:
                job.status = JobStatus.FAILED
                logger.error("job_auto_failed job_id=%s after %s failures", job_id, job.failure_count)
        await db.commit()
        return 1
