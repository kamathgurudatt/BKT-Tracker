import enum

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class StockStatus(str, enum.Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    HIDDEN = "hidden"
    UNKNOWN = "unknown"


class NotificationType(str, enum.Enum):
    RESTOCK = "restock"
    PRICE_DROP = "price_drop"
    STOCK_INCREASE = "stock_increase"
    ETA_IMPROVED = "eta_improved"
    SYSTEM = "system"


class JobStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"


class RequestStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    fcm_token: Mapped[str] = mapped_column(Text, nullable=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)


class Location(Base, TimestampMixin):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    pincode: Mapped[str] = mapped_column(String(16), nullable=True, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    user: Mapped[User] = relationship()
    __table_args__ = (Index("ix_locations_user_enabled", "user_id", "enabled"),)


class Wishlist(Base, TimestampMixin):
    __tablename__ = "wishlists"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user: Mapped[User] = relationship()


class TrackedProduct(Base, TimestampMixin):
    __tablename__ = "tracked_products"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlists.id", ondelete="SET NULL"), nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(40), default="blinkit", index=True)
    external_product_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(120), nullable=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    target_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    alert_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    __table_args__ = (UniqueConstraint("user_id", "provider", "external_product_id", name="uq_user_provider_product"),)


class InventorySnapshot(Base, TimestampMixin):
    __tablename__ = "inventory_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    tracked_product_id: Mapped[int] = mapped_column(ForeignKey("tracked_products.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), index=True)
    status: Mapped[StockStatus] = mapped_column(Enum(StockStatus), default=StockStatus.UNKNOWN, index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    mrp: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    discount_percent: Mapped[float] = mapped_column(Float, nullable=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=True)
    eta_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    observed_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    __table_args__ = (Index("ix_snapshots_product_location_time", "tracked_product_id", "location_id", "observed_at"),)


class PriceHistory(Base, TimestampMixin):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    tracked_product_id: Mapped[int] = mapped_column(ForeignKey("tracked_products.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    mrp: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    observed_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    tracked_product_id: Mapped[int] = mapped_column(ForeignKey("tracked_products.id", ondelete="SET NULL"), nullable=True, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), index=True)
    title: Mapped[str] = mapped_column(String(180))
    body: Mapped[str] = mapped_column(Text)
    channel: Mapped[str] = mapped_column(String(40), default="fcm")
    sent_at = mapped_column(DateTime(timezone=True), nullable=True)
    read_at = mapped_column(DateTime(timezone=True), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


class MonitoringJob(Base, TimestampMixin):
    __tablename__ = "monitoring_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    tracked_product_id: Mapped[int] = mapped_column(ForeignKey("tracked_products.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), index=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.ACTIVE, index=True)
    interval_seconds: Mapped[int] = mapped_column(Integer, default=900)
    last_run_at = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str] = mapped_column(Text, nullable=True)
    __table_args__ = (UniqueConstraint("tracked_product_id", "location_id", name="uq_monitoring_product_location"),)


class ProviderRequestLog(Base, TimestampMixin):
    __tablename__ = "provider_request_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(40), index=True)
    endpoint: Mapped[str] = mapped_column(Text)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    tracked_product_id: Mapped[int] = mapped_column(ForeignKey("tracked_products.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), index=True)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    request_headers: Mapped[dict] = mapped_column(JSON, default=dict)
    response_excerpt: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    fetched_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    __table_args__ = (Index("ix_provider_logs_product_location_time", "tracked_product_id", "location_id", "fetched_at"),)


class InventoryChangeEvent(Base, TimestampMixin):
    __tablename__ = "inventory_change_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    tracked_product_id: Mapped[int] = mapped_column(ForeignKey("tracked_products.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), index=True)
    change_type: Mapped[str] = mapped_column(String(60), index=True)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    latest_hash: Mapped[str] = mapped_column(String(64), index=True)
    previous_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    latest_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    detected_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    __table_args__ = (Index("ix_change_events_product_location_time", "tracked_product_id", "location_id", "detected_at"),)
