from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.entities import InventorySnapshot, Location, MonitoringJob, PriceHistory, StockStatus, TrackedProduct, User
from app.providers.base import ProviderLocation
from app.providers.registry import get_provider
from app.schemas.dto import TrackProductCreate
from app.services.change_detection import detect_changes
from app.services.notifications import NotificationService

settings = get_settings()


class TrackingService:
    async def search_products(self, provider: str, keyword: str, location: Location | None) -> list[dict]:
        provider_location = ProviderLocation(
            pincode=location.pincode if location else None,
            latitude=location.latitude if location else None,
            longitude=location.longitude if location else None,
            label=location.name if location else None,
        )
        return await get_provider(provider).search(keyword, provider_location)

    async def add_tracking(self, db: AsyncSession, user: User, payload: TrackProductCreate) -> TrackedProduct:
        product = TrackedProduct(user_id=user.id, **payload.model_dump(exclude={"location_ids"}))
        db.add(product)
        await db.flush()
        interval = max(settings.min_poll_interval_seconds, settings.default_poll_interval_seconds)
        for location_id in payload.location_ids:
            db.add(MonitoringJob(tracked_product_id=product.id, location_id=location_id, interval_seconds=interval, next_run_at=datetime.now(UTC)))
        return product

    async def poll_once(self, db: AsyncSession, job: MonitoringJob) -> InventorySnapshot:
        product = await db.get(TrackedProduct, job.tracked_product_id)
        location = await db.get(Location, job.location_id)
        if product is None or location is None:
            raise ValueError("Monitoring job references missing product or location")
        current = await get_provider(product.provider).fetch_product(
            product.external_product_id,
            ProviderLocation(location.pincode, location.latitude, location.longitude, location.name),
        )
        previous_snapshot = await db.scalar(
            select(InventorySnapshot).where(
                InventorySnapshot.tracked_product_id == product.id,
                InventorySnapshot.location_id == location.id,
            ).order_by(desc(InventorySnapshot.observed_at)).limit(1)
        )
        previous = previous_snapshot.raw_payload if previous_snapshot else None
        snapshot = InventorySnapshot(
            tracked_product_id=product.id,
            location_id=location.id,
            status=StockStatus(current.get("stock_status", "unknown")),
            price=current.get("price"),
            mrp=current.get("mrp"),
            discount_percent=current.get("discount_percent"),
            stock_quantity=current.get("stock_quantity"),
            eta_minutes=current.get("eta_minutes"),
            raw_payload=current,
        )
        db.add(snapshot)
        if current.get("price") is not None:
            db.add(PriceHistory(tracked_product_id=product.id, location_id=location.id, price=current["price"], mrp=current.get("mrp")))
        notifier = NotificationService()
        user = await db.get(User, product.user_id)
        for type_, message in detect_changes(previous, current):
            await notifier.create_and_send(db, user, type_, f"{product.name}: {message}", f"{product.name} in {location.name}: {message}", current)
        job.last_run_at = datetime.now(UTC)
        job.next_run_at = job.last_run_at + timedelta(seconds=job.interval_seconds)
        job.failure_count = 0
        job.last_error = None
        return snapshot
