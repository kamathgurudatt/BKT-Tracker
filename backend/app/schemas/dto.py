from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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
