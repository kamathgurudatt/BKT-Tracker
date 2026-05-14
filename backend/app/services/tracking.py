import asyncio
import difflib
import logging
import json
import random
from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.redis import redis_client
from app.models.entities import (
    InventoryChangeEvent,
    InventorySnapshot,
    Location,
    MonitoringJob,
    PriceHistory,
    ProviderRequestLog,
    RequestStatus,
    StockStatus,
    TrackedProduct,
    User,
)
from app.providers.base import ProviderLocation
from app.providers.registry import get_provider
from app.schemas.dto import TrackProductCreate
from app.services.change_detection import detect_changes
from app.services.notifications import NotificationService
from app.services.state_hash import inventory_hash

settings = get_settings()
logger = logging.getLogger(__name__)


class StaleProviderResponseError(ValueError):
    pass


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
            jitter = random.randint(0, max(30, interval // 5))
            db.add(MonitoringJob(tracked_product_id=product.id, location_id=location_id, interval_seconds=interval, next_run_at=datetime.now(UTC) + timedelta(seconds=jitter)))
        return product

    async def _fetch_live(self, product: TrackedProduct, location: Location) -> dict:
        return await get_provider(product.provider).fetch_product(product.external_product_id, ProviderLocation(location.pincode, location.latitude, location.longitude, location.name))

    def _validate_recent(self, current: dict) -> None:
        fetched_at_raw = current.get("_fetched_at")
        if not fetched_at_raw:
            return
        fetched_at = datetime.fromisoformat(fetched_at_raw)
        age = (datetime.now(UTC) - fetched_at).total_seconds()
        if age > settings.stock_response_max_age_seconds:
            raise StaleProviderResponseError(f"Provider response is stale: {age:.0f}s old")

    async def _record_request_log(self, db: AsyncSession, product: TrackedProduct, location: Location, current: dict | None = None, error: Exception | None = None) -> None:
        db.add(
            ProviderRequestLog(
                provider=product.provider,
                endpoint=(current or {}).get("_source_endpoint", "unavailable"),
                location_id=location.id,
                tracked_product_id=product.id,
                status=RequestStatus.FAILURE if error else RequestStatus.SUCCESS,
                latency_ms=(current or {}).get("_response_latency_ms"),
                request_headers=(current or {}).get("_request_headers", {}),
                response_excerpt=(current or {}).get("_raw_response", {}) if not error else {},
                error=str(error)[:1000] if error else None,
                fetched_at=datetime.now(UTC),
            )
        )

    async def _is_duplicate_alert(self, user_id: int, product_id: int, location_id: int, event_type: str) -> bool:
        key = f"alert:{user_id}:{product_id}:{location_id}:{event_type}"
        inserted = await redis_client.set(key, "1", ex=settings.duplicate_alert_window_seconds, nx=True)
        return not bool(inserted)

    async def poll_once(self, db: AsyncSession, job: MonitoringJob) -> InventorySnapshot | None:
        product = await db.get(TrackedProduct, job.tracked_product_id)
        location = await db.get(Location, job.location_id)
        if product is None or location is None:
            raise ValueError("Monitoring job references missing product or location")
        try:
            current = await self._fetch_live(product, location)
            self._validate_recent(current)
        except RuntimeError as exc:
            if str(exc) == "LIVE_PROVIDER_NOT_CONFIGURED":
                logger.warning(
                    "polling_skipped",
                    extra={"provider": product.provider, "tracked_product_id": product.id, "location_id": location.id, "reason": "LIVE_PROVIDER_NOT_CONFIGURED"},
                )
                await self._record_request_log(db, product, location, error=exc)
                jitter = random.randint(0, max(30, job.interval_seconds // 5))
                job.last_run_at = datetime.now(UTC)
                job.next_run_at = job.last_run_at + timedelta(seconds=job.interval_seconds + jitter)
                job.last_error = "LIVE_PROVIDER_NOT_CONFIGURED"
                return None
            await self._record_request_log(db, product, location, error=exc)
            raise
        except Exception as exc:
            await self._record_request_log(db, product, location, error=exc)
            raise
        await self._record_request_log(db, product, location, current=current)

        previous_snapshot = await db.scalar(
            select(InventorySnapshot)
            .where(
                InventorySnapshot.tracked_product_id == product.id,
                InventorySnapshot.location_id == location.id,
            )
            .order_by(desc(InventorySnapshot.observed_at))
            .limit(1)
        )
        previous = previous_snapshot.raw_payload if previous_snapshot else None
        current_hash = inventory_hash(current)
        previous_hash = await redis_client.get(f"snapshot:{product.id}:{location.id}:hash")
        await redis_client.set(f"snapshot:{product.id}:{location.id}:hash", current_hash, ex=max(settings.default_poll_interval_seconds * 4, 3600))

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
        events = detect_changes(previous, current)
        if events and current.get("stock_status") == StockStatus.IN_STOCK.value:
            await asyncio.sleep(settings.stock_confirmation_delay_seconds)
            confirmation = await self._fetch_live(product, location)
            if confirmation.get("stock_status") != current.get("stock_status"):
                events = []
        for type_, message in events:
            if await self._is_duplicate_alert(user.id, product.id, location.id, type_.value):
                continue
            db.add(
                InventoryChangeEvent(
                    tracked_product_id=product.id,
                    location_id=location.id,
                    change_type=type_.value,
                    previous_hash=previous_hash,
                    latest_hash=current_hash,
                    previous_payload=previous or {},
                    latest_payload=current,
                )
            )
            await notifier.create_and_send(db, user, type_, f"{product.name}: {message}", f"{product.name} in {location.name}: {message}", current)
        jitter = random.randint(0, max(30, job.interval_seconds // 5))
        job.last_run_at = datetime.now(UTC)
        job.next_run_at = job.last_run_at + timedelta(seconds=job.interval_seconds + jitter)
        job.failure_count = 0
        job.last_error = None
        return snapshot

    async def latest_debug_state(self, db: AsyncSession, user: User) -> dict:
        latest_log = await db.scalar(
            select(ProviderRequestLog)
            .join(TrackedProduct, TrackedProduct.id == ProviderRequestLog.tracked_product_id)
            .where(TrackedProduct.user_id == user.id)
            .order_by(desc(ProviderRequestLog.fetched_at))
            .limit(1)
        )
        latest_change = await db.scalar(
            select(InventoryChangeEvent)
            .join(TrackedProduct, TrackedProduct.id == InventoryChangeEvent.tracked_product_id)
            .where(TrackedProduct.user_id == user.id)
            .order_by(desc(InventoryChangeEvent.detected_at))
            .limit(1)
        )
        failed_requests = await db.scalars(
            select(ProviderRequestLog)
            .join(TrackedProduct, TrackedProduct.id == ProviderRequestLog.tracked_product_id)
            .where(TrackedProduct.user_id == user.id, ProviderRequestLog.status == RequestStatus.FAILURE)
            .order_by(desc(ProviderRequestLog.fetched_at))
            .limit(20)
        )
        location = await db.get(Location, latest_log.location_id) if latest_log and latest_log.location_id else None
        recent_success_count = await db.scalar(
            select(func.count(ProviderRequestLog.id))
            .join(TrackedProduct, TrackedProduct.id == ProviderRequestLog.tracked_product_id)
            .where(TrackedProduct.user_id == user.id, ProviderRequestLog.status == RequestStatus.SUCCESS)
        )
        recent_change_events = await db.scalars(
            select(InventoryChangeEvent)
            .join(TrackedProduct, TrackedProduct.id == InventoryChangeEvent.tracked_product_id)
            .where(TrackedProduct.user_id == user.id)
            .order_by(desc(InventoryChangeEvent.detected_at))
            .limit(5)
        )
        parsed_stock_fields = {}
        if latest_log and latest_log.response_excerpt:
            payload = latest_log.response_excerpt
            parsed_stock_fields = {
                "stock_status": payload.get("stock_status"),
                "stock_quantity": payload.get("stock_quantity"),
                "price": payload.get("price"),
                "mrp": payload.get("mrp"),
                "eta_minutes": payload.get("eta_minutes"),
            }

        return {
            "last_api_response_timestamp": latest_log.fetched_at if latest_log else None,
            "source_endpoint_called": latest_log.endpoint if latest_log else None,
            "raw_stock_response": latest_log.response_excerpt if latest_log else None,
            "response_latency_ms": latest_log.latency_ms if latest_log else None,
            "location_id": latest_log.location_id if latest_log else None,
            "request_status": latest_log.status.value if latest_log else None,
            "request_headers_used": latest_log.request_headers if latest_log else None,
            "response_headers": latest_log.request_headers if latest_log else {},
            "response_timestamp": latest_log.fetched_at if latest_log else None,
            "parsed_stock_fields": parsed_stock_fields,
            "location_context": {"id": location.id, "name": location.name, "pincode": location.pincode, "latitude": location.latitude, "longitude": location.longitude} if location else {},
            "live_data_available": bool(latest_log and latest_log.status == RequestStatus.SUCCESS),
            "live_unavailable_message": None if latest_log and latest_log.status == RequestStatus.SUCCESS else "LIVE INVENTORY SOURCE UNAVAILABLE",
            "polling_proof": {
                "successful_polls_recorded": int(recent_success_count or 0),
                "last_poll_time": latest_log.fetched_at if latest_log else None,
                "polling_is_happening": bool(recent_success_count),
            },
            "inventory_change_proof": [
                {"detected_at": ev.detected_at, "change_type": ev.change_type, "previous_hash": ev.previous_hash, "latest_hash": ev.latest_hash}
                for ev in recent_change_events
            ],
            "endpoint_audit": [
                {
                    "purpose": "blinkit_search",
                    "method": "GET",
                    "url_template": settings.blinkit_search_url_template,
                    "location_params": ["pincode", "lat", "lon"],
                    "auth_or_session": "No explicit auth/session handling in client; endpoint template must already be publicly callable/authorized.",
                },
                {
                    "purpose": "blinkit_product",
                    "method": "GET",
                    "url_template": settings.blinkit_product_url_template,
                    "location_params": ["pincode", "lat", "lon"],
                    "auth_or_session": "No explicit auth/session handling in client; endpoint template must already be publicly callable/authorized.",
                },
            ],
            "last_detected_inventory_change": latest_change.latest_payload if latest_change else None,
            "last_detected_change_type": latest_change.change_type if latest_change else None,
            "failed_requests": [{"endpoint": row.endpoint, "error": row.error, "fetched_at": row.fetched_at} for row in failed_requests],
        }

    async def run_test_mode(self, db: AsyncSession, user: User, tracked_product_id: int, location_id: int, polls: int) -> dict:
        product = await db.scalar(select(TrackedProduct).where(TrackedProduct.id == tracked_product_id, TrackedProduct.user_id == user.id))
        if product is None:
            raise ValueError("Tracked product not found for user")
        location = await db.get(Location, location_id)
        if location is None:
            raise ValueError("Location not found")
        rounds: list[dict] = []
        previous_payload: dict | None = None
        for _ in range(polls):
            current = await self._fetch_live(product, location)
            diff = []
            if previous_payload is not None:
                old_text = json.dumps(previous_payload, sort_keys=True, indent=2).splitlines()
                new_text = json.dumps(current, sort_keys=True, indent=2).splitlines()
                diff = list(difflib.unified_diff(old_text, new_text, fromfile="old", tofile="new", lineterm=""))
            rounds.append({"timestamp": datetime.now(UTC).isoformat(), "payload": current, "diff_from_previous": diff})
            previous_payload = current
            if _ < polls - 1:
                await asyncio.sleep(15)
        return {"tracked_product_id": tracked_product_id, "location_id": location_id, "poll_interval_seconds": 15, "rounds": rounds}
