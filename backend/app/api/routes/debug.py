from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.dto import DebugState
from app.services.tracking import TrackingService

router = APIRouter(prefix="/debug", tags=["debug"])
service = TrackingService()


@router.get("/monitoring", response_model=DebugState)
async def monitoring_debug(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await service.latest_debug_state(db, user)
