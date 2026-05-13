from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ProviderParseError(ValueError):
    """Raised when a live provider payload cannot be normalized safely."""


@dataclass(slots=True)
class NormalizedProduct:
    provider: str
    external_product_id: str
    name: str
    image_url: str | None
    price: float | None
    mrp: float | None
    discount_percent: float | None
    stock_status: str
    stock_quantity: int | None
    eta_minutes: int | None
    category: str | None
    raw_payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "external_product_id": self.external_product_id,
            "name": self.name,
            "image_url": self.image_url,
            "price": self.price,
            "mrp": self.mrp,
            "discount_percent": self.discount_percent,
            "stock_status": self.stock_status,
            "stock_quantity": self.stock_quantity,
            "eta_minutes": self.eta_minutes,
            "category": self.category,
            "raw_payload": self.raw_payload,
        }


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _first(mapping: dict[str, Any], keys: tuple[str, ...]) -> Any:
    lowered = {str(k).lower(): v for k, v in mapping.items()}
    for key in keys:
        if key in mapping:
            return mapping[key]
        if key.lower() in lowered:
            return lowered[key.lower()]
    return None


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        value = value.replace("₹", "").replace(",", "").strip()
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    number = _to_float(value)
    return int(number) if number is not None else None


def _normalize_status(candidate: dict[str, Any]) -> str:
    raw = _first(candidate, ("stock_status", "availability", "inventory_status", "status", "state", "isAvailable", "available", "in_stock"))
    quantity = _to_int(_first(candidate, ("stock_quantity", "inventory", "quantity", "qty", "available_quantity")))
    text = str(raw).lower() if raw is not None else ""
    if raw is True or text in {"available", "in_stock", "instock", "true", "1"} or (quantity is not None and quantity > 0):
        return "in_stock"
    if raw is False or text in {"unavailable", "out_of_stock", "outofstock", "sold_out", "false", "0"} or quantity == 0:
        return "out_of_stock"
    if text in {"hidden", "unlisted", "removed", "not_found"}:
        return "hidden"
    return "unknown"


def normalize_product(provider: str, payload: dict[str, Any], fallback_id: str | None = None) -> NormalizedProduct:
    candidates = [node for node in _walk(payload) if isinstance(node, dict)]
    selected = None
    for candidate in candidates:
        product_id = _first(candidate, ("id", "product_id", "productId", "item_id", "sku", "external_product_id"))
        name = _first(candidate, ("name", "product_name", "display_name", "title"))
        if name and (product_id or fallback_id):
            selected = candidate
            break
    if selected is None:
        raise ProviderParseError("Live response did not contain a recognizable product object")

    product_id = str(_first(selected, ("id", "product_id", "productId", "item_id", "sku", "external_product_id")) or fallback_id or "")
    name = str(_first(selected, ("name", "product_name", "display_name", "title")) or "").strip()
    if not product_id or not name:
        raise ProviderParseError("Live response is missing product id or name")

    price = _to_float(_first(selected, ("price", "selling_price", "sale_price", "offer_price", "unit_price")))
    mrp = _to_float(_first(selected, ("mrp", "marked_price", "list_price", "maximum_retail_price")))
    discount = _to_float(_first(selected, ("discount_percent", "discount", "discount_percentage")))
    if discount is None and price is not None and mrp:
        discount = round(max(0, (mrp - price) / mrp * 100), 2)

    return NormalizedProduct(
        provider=provider,
        external_product_id=product_id,
        name=name,
        image_url=_first(selected, ("image_url", "image", "imageUrl", "thumbnail", "media_url")),
        price=price,
        mrp=mrp,
        discount_percent=discount,
        stock_status=_normalize_status(selected),
        stock_quantity=_to_int(_first(selected, ("stock_quantity", "inventory", "quantity", "qty", "available_quantity"))),
        eta_minutes=_to_int(_first(selected, ("eta_minutes", "eta", "delivery_eta", "delivery_time", "etaInMinutes"))),
        category=_first(selected, ("category", "category_name", "l1_category", "taxonomy")),
        raw_payload=payload,
    )


def normalize_search_results(provider: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in _walk(payload):
        if not isinstance(node, dict):
            continue
        try:
            product = normalize_product(provider, node)
        except ProviderParseError:
            continue
        if product.external_product_id in seen:
            continue
        seen.add(product.external_product_id)
        results.append(product.as_dict())
    if not results:
        raise ProviderParseError("Live search response did not contain recognizable products")
    return results
