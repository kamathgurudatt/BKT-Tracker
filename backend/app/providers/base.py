import asyncio
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings


@dataclass(slots=True)
class ProviderLocation:
    pincode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    label: str | None = None


class EthicalProviderClient(ABC):
    """Base client that enforces safe throttling and avoids auth/captcha bypasses."""

    provider_name: str = "base"
    user_agents = [
        "BlinkitStockSentinel/1.0 EducationalResearch",
        "Mozilla/5.0 (compatible; BlinkitStockSentinel/1.0; +https://example.invalid/robots)",
    ]

    def __init__(self) -> None:
        self.settings = get_settings()
        self._semaphore = asyncio.Semaphore(max(1, self.settings.provider_max_requests_per_minute // 6))

    def _headers(self) -> dict[str, str]:
        return {"User-Agent": random.choice(self.user_agents), "Accept": "application/json,text/plain,*/*"}

    async def _get_json(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        async with self._semaphore:
            await asyncio.sleep(self.settings.provider_base_delay_seconds)
            async with httpx.AsyncClient(timeout=self.settings.provider_timeout_seconds, headers=self._headers()) as client:
                for attempt in range(3):
                    try:
                        response = await client.get(url, params=params)
                        response.raise_for_status()
                        return response.json()
                    except (httpx.HTTPError, ValueError):
                        if attempt == 2:
                            raise
                        await asyncio.sleep(2**attempt + random.random())
        return {}

    @abstractmethod
    async def search(self, keyword: str, location: ProviderLocation) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def fetch_product(self, external_product_id: str, location: ProviderLocation) -> dict[str, Any]: ...
