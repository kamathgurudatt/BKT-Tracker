import logging
from typing import Any
from urllib.parse import urlparse

from app.providers.base import EthicalProviderClient, ProviderLocation
from app.providers.parser import normalize_product, normalize_search_results


logger = logging.getLogger(__name__)


class BlinkitProvider(EthicalProviderClient):
    """Live Blinkit adapter.

    This adapter intentionally has no mock/demo fallback. Operators must configure
    public, ToS-compliant endpoint templates captured from their own legitimate
    Blinkit app/web traffic. If templates are absent, requests fail closed instead
    of fabricating inventory.
    """

    provider_name = "blinkit"

    @staticmethod
    def _validate_template(template: str) -> bool:
        parsed = urlparse(template)
        if parsed.scheme not in {"http", "https"}:
            return False
        if not parsed.netloc:
            return False
        blocked_hosts = {"authorized.example", "localhost", "127.0.0.1", "0.0.0.0"}
        host = (parsed.hostname or "").lower()
        if host in blocked_hosts or host.endswith(".example") or host.endswith(".invalid"):
            return False
        return True

    def _format_url(self, template: str | None, *, keyword: str | None = None, external_product_id: str | None = None, location: ProviderLocation) -> str:
        if not template:
            logger.warning("LIVE_PROVIDER_NOT_CONFIGURED", extra={"provider": self.provider_name, "reason": "missing_template"})
            raise RuntimeError("LIVE_PROVIDER_NOT_CONFIGURED")
        if not self._validate_template(template):
            logger.warning("LIVE_PROVIDER_NOT_CONFIGURED", extra={"provider": self.provider_name, "reason": "invalid_template"})
            raise RuntimeError("LIVE_PROVIDER_NOT_CONFIGURED")
        return template.format(
            query=keyword or "",
            product_id=external_product_id or "",
            pincode=location.pincode or "",
            lat=location.latitude or "",
            lon=location.longitude or "",
        )

    async def search(self, keyword: str, location: ProviderLocation) -> list[dict[str, Any]]:
        endpoint = self._format_url(self.settings.blinkit_search_url_template, keyword=keyword, location=location)
        response = await self._get_json(endpoint)
        results = normalize_search_results(self.provider_name, response.payload)
        for result in results:
            result.update({
                "location_label": location.label or location.pincode,
                "_source_endpoint": response.url,
                "_response_latency_ms": response.latency_ms,
                "_request_headers": response.request_headers,
                "_raw_response": response.payload,
            })
        return results

    async def fetch_product(self, external_product_id: str, location: ProviderLocation) -> dict[str, Any]:
        endpoint = self._format_url(self.settings.blinkit_product_url_template, external_product_id=external_product_id, location=location)
        response = await self._get_json(endpoint)
        product = normalize_product(self.provider_name, response.payload, fallback_id=external_product_id).as_dict()
        product.update({
            "location_label": location.label or location.pincode,
            "_source_endpoint": response.url,
            "_response_latency_ms": response.latency_ms,
            "_request_headers": response.request_headers,
            "_raw_response": response.payload,
            "_fetched_at": response.fetched_at.isoformat(),
        })
        return product
