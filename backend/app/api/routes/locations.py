from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Location, User
from app.schemas.dto import LocationCreate, LocationRead

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationRead])
async def list_locations(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(Location).where(Location.user_id == user.id))).all()


@router.post("", response_model=LocationRead, status_code=201)
async def create_location(payload: LocationCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    location = Location(user_id=user.id, **payload.model_dump())
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location
