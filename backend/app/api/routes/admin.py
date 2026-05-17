from fastapi import APIRouter, Depends, HTTPException
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


# FIX: return 404 when job not found instead of silent 200
@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: int, _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    job = await db.get(MonitoringJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Monitoring job {job_id} not found")
    job.status = JobStatus.PAUSED
    await db.commit()
    return {"ok": True, "job_id": job_id, "status": "paused"}


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: int, _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    job = await db.get(MonitoringJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Monitoring job {job_id} not found")
    job.status = JobStatus.ACTIVE
    await db.commit()
    return {"ok": True, "job_id": job_id, "status": "active"}
