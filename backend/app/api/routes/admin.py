from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.entities import JobStatus, MonitoringJob, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def stats(_: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    users = await db.scalar(select(func.count(User.id)))
    jobs = await db.scalar(select(func.count(MonitoringJob.id)))
    return {"users": users, "monitoring_jobs": jobs}


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: int, _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    job = await db.get(MonitoringJob, job_id)
    if job:
        job.status = JobStatus.PAUSED
        await db.commit()
    return {"ok": True}
