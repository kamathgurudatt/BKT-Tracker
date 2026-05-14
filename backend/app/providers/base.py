import asyncio
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import get_settings


@dataclass(slots=True)
class ProviderLocation:
    pincode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    label: str | None = None


@dataclass(slots=True)
class ProviderHTTPResponse:
    url: str
    payload: dict[str, Any]
    status_code: int
    latency_ms: int
    request_headers: dict[str, str]
    fetched_at: datetime


class EthicalProviderClient(ABC):
    """Base client that enforces safe throttling and avoids auth/captcha bypasses."""

    provider_name: str = "base"
    user_agents = [
        "BlinkitStockSentinel/1.0 EducationalResearch",
        "Mozilla/5.0 (compatible; BlinkitStockSentinel/1.0; +https://web-production-bd4d.up.railway.app)",
    ]

    def __init__(self) -> None:
        self.settings = get_settings()
        self._semaphore = asyncio.Semaphore(max(1, self.settings.provider_max_requests_per_minute // 6))

    def _headers(self) -> dict[str, str]:
        return {"User-Agent": random.choice(self.user_agents), "Accept": "application/json,text/plain,*/*"}

    async def _get_json(self, url: str, params: dict[str, Any] | None = None) -> ProviderHTTPResponse:
        headers = self._headers()
        async with self._semaphore:
            await asyncio.sleep(self.settings.provider_base_delay_seconds + random.uniform(0, 0.75))
            async with httpx.AsyncClient(timeout=self.settings.provider_timeout_seconds, headers=headers) as client:
                for attempt in range(3):
                    started = time.perf_counter()
                    try:
                        response = await client.get(url, params=params)
                        latency_ms = int((time.perf_counter() - started) * 1000)
                        response.raise_for_status()
                        payload = response.json()
                        if not isinstance(payload, dict):
                            raise ValueError("Provider returned non-object JSON payload")
                        return ProviderHTTPResponse(str(response.url), payload, response.status_code, latency_ms, headers, datetime.now(UTC))
                    except (httpx.HTTPError, ValueError):
                        if attempt == 2:
                            raise
                        await asyncio.sleep(2**attempt + random.random())
        raise RuntimeError("Provider request failed unexpectedly")

    @abstractmethod
    async def search(self, keyword: str, location: ProviderLocation) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def fetch_product(self, external_product_id: str, location: ProviderLocation) -> dict[str, Any]: ...

    async def search_products(self, keyword: str, location: ProviderLocation) -> list[dict[str, Any]]:
        return await self.search(keyword, location)

    async def check_inventory(self, external_product_id: str, location: ProviderLocation) -> dict[str, Any]:
        return await self.fetch_product(external_product_id, location)

    def normalize_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload
