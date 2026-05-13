from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import InventorySnapshot, Location, TrackedProduct, User
from app.schemas.dto import InventorySnapshotRead, ProductSearchResult, TrackedProductRead, TrackProductCreate
from app.services.tracking import TrackingService

router = APIRouter(prefix="/tracking", tags=["tracking"])
service = TrackingService()


@router.get("/search", response_model=list[ProductSearchResult])
async def search_products(q: str = Query(min_length=2), provider: str = "blinkit", location_id: int | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    location = await db.get(Location, location_id) if location_id else None
    try:
        results = await service.search_products(provider, q, location)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return results


@router.post("/items", response_model=TrackedProductRead, status_code=201)
async def add_item(payload: TrackProductCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    product = await service.add_tracking(db, user, payload)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/items", response_model=list[TrackedProductRead])
async def list_items(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(TrackedProduct).where(TrackedProduct.user_id == user.id))).all()


@router.delete("/items/{item_id}", status_code=204)
async def remove_item(item_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    product = await db.scalar(select(TrackedProduct).where(TrackedProduct.id == item_id, TrackedProduct.user_id == user.id))
    if product:
        await db.delete(product)
        await db.commit()


@router.get("/items/{item_id}/history", response_model=list[InventorySnapshotRead])
async def history(item_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(InventorySnapshot).join(TrackedProduct).where(TrackedProduct.id == item_id, TrackedProduct.user_id == user.id).order_by(desc(InventorySnapshot.observed_at)).limit(200))).all()
