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


@celery_app.task
async def _noop():
    return True


@celery_app.task(name="app.workers.tasks.dispatch_due_jobs")
def dispatch_due_jobs():
    try:
        return asyncio.run(_dispatch())
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
    return asyncio.run(_poll(job_id))


async def _poll(job_id: int) -> int:
    async with AsyncSessionLocal() as db:
        job = await db.get(MonitoringJob, job_id)
        if not job:
            return 0
        try:
            await TrackingService().poll_once(db, job)
        except Exception as exc:  # worker boundary logs and persists failures
            job.failure_count += 1
            job.last_error = str(exc)[:1000]
        await db.commit()
        return 1
