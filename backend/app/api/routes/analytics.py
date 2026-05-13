from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import InventorySnapshot, Notification, PriceHistory, StockStatus, TrackedProduct, User
from app.schemas.dto import AnalyticsPoint, NotificationRead

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/availability", response_model=list[AnalyticsPoint])
async def availability(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(TrackedProduct.name, func.count(InventorySnapshot.id)).join(InventorySnapshot).where(TrackedProduct.user_id == user.id, InventorySnapshot.status == StockStatus.IN_STOCK).group_by(TrackedProduct.name).limit(20))).all()
    return [AnalyticsPoint(label=name, value=float(count)) for name, count in rows]


@router.get("/prices/{item_id}", response_model=list[AnalyticsPoint])
async def price_graph(item_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(PriceHistory.price, PriceHistory.observed_at).join(TrackedProduct).where(TrackedProduct.id == item_id, TrackedProduct.user_id == user.id).order_by(PriceHistory.observed_at))).all()
    return [AnalyticsPoint(label="price", value=float(price), observed_at=observed_at) for price, observed_at in rows]


@router.get("/notifications", response_model=list[NotificationRead])
async def notifications(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(100))).all()
