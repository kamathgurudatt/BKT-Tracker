from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password_bcrypt_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer.")
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_bcrypt_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer.")
        return value


class LocationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    pincode: str | None = Field(default=None, max_length=16)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    enabled: bool = True


class LocationRead(LocationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class WishlistCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None


class WishlistRead(WishlistCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProductSearchResult(BaseModel):
    provider: str
    external_product_id: str
    name: str
    image_url: str | None = None
    price: float | None = None
    mrp: float | None = None
    discount_percent: float | None = None
    stock_status: str = "unknown"
    eta_minutes: int | None = None
    category: str | None = None
    location_label: str | None = None


class TrackProductCreate(BaseModel):
    provider: str = "blinkit"
    external_product_id: str
    name: str
    image_url: str | None = None
    category: str | None = None
    wishlist_id: int | None = None
    location_ids: list[int] = Field(default_factory=list)
    target_price: float | None = None
    alert_rules: dict = Field(default_factory=dict)


class TrackedProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    provider: str
    external_product_id: str
    name: str
    image_url: str | None
    category: str | None
    enabled: bool
    target_price: float | None


class InventorySnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tracked_product_id: int
    location_id: int
    status: str
    price: float | None
    mrp: float | None
    discount_percent: float | None
    stock_quantity: int | None
    eta_minutes: int | None
    observed_at: datetime


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    title: str
    body: str
    channel: str
    sent_at: datetime | None
    read_at: datetime | None


class AnalyticsPoint(BaseModel):
    label: str
    value: float
    observed_at: datetime | None = None

class DebugState(BaseModel):
    last_api_response_timestamp: datetime | None = None
    source_endpoint_called: str | None = None
    raw_stock_response: dict | None = None
    response_latency_ms: int | None = None
    location_id: int | None = None
    request_status: str | None = None
    request_headers_used: dict | None = None
    last_detected_inventory_change: dict | None = None
    last_detected_change_type: str | None = None
    failed_requests: list[dict] = Field(default_factory=list)
    live_data_available: bool = False
    live_unavailable_message: str | None = None
    response_headers: dict = Field(default_factory=dict)
    response_timestamp: datetime | None = None
    parsed_stock_fields: dict = Field(default_factory=dict)
    location_context: dict = Field(default_factory=dict)
    polling_proof: dict = Field(default_factory=dict)
    inventory_change_proof: list[dict] = Field(default_factory=list)
    endpoint_audit: list[dict] = Field(default_factory=list)


class DebugTestModeRequest(BaseModel):
    tracked_product_id: int
    location_id: int
    polls: int = Field(default=2, ge=1, le=10)


class DebugTestModeResult(BaseModel):
    tracked_product_id: int
    location_id: int
    poll_interval_seconds: int = 15
    rounds: list[dict] = Field(default_factory=list)
