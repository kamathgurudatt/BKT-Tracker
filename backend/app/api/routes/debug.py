from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.dto import DebugState, DebugTestModeRequest, DebugTestModeResult
from app.services.tracking import TrackingService

router = APIRouter(prefix="/debug", tags=["debug"])
service = TrackingService()


@router.get("/monitoring", response_model=DebugState)
async def monitoring_debug(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        return await service.latest_debug_state(db, user)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Debug monitoring unavailable: {exc}") from exc


@router.post("/test-mode", response_model=DebugTestModeResult)
async def test_mode(payload: DebugTestModeRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        return await service.run_test_mode(db, user, payload.tracked_product_id, payload.location_id, payload.polls)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Live provider unavailable: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Debug test mode unavailable: {exc}") from exc
