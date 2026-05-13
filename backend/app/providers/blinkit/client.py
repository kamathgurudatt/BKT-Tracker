from typing import Any

from app.providers.base import EthicalProviderClient, ProviderLocation


class BlinkitProvider(EthicalProviderClient):
    provider_name = "blinkit"

    async def search(self, keyword: str, location: ProviderLocation) -> list[dict[str, Any]]:
        # Educational adapter: configure public, ToS-compliant endpoints with BLINKIT_SEARCH_URL.
        # The default returns deterministic sample data so tests and demos never scrape aggressively.
        sample_id = keyword.lower().replace(" ", "-")[:48] or "sample-product"
        return [{
            "provider": self.provider_name,
            "external_product_id": f"demo-{sample_id}",
            "name": keyword.title(),
            "image_url": "https://placehold.co/400x400?text=Product",
            "price": 99.0,
            "mrp": 120.0,
            "discount_percent": 17.5,
            "stock_status": "in_stock",
            "eta_minutes": 10,
            "category": "Demo",
            "location_label": location.label or location.pincode,
        }]

    async def fetch_product(self, external_product_id: str, location: ProviderLocation) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "external_product_id": external_product_id,
            "name": external_product_id.replace("-", " ").title(),
            "price": 99.0,
            "mrp": 120.0,
            "discount_percent": 17.5,
            "stock_status": "in_stock",
            "stock_quantity": 8,
            "eta_minutes": 10,
            "raw_payload": {"source": "demo-safe-provider"},
        }
