import asyncio
import logging
import random
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from app.providers.base import EthicalProviderClient, ProviderLocation

logger = logging.getLogger(__name__)


class BrowserProviderUnavailable(RuntimeError):
    pass


class BrowserManager:
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self, settings):
        self.settings = settings
        self._playwright = None
        self._browser = None

    @classmethod
    async def get(cls, settings):
        async with cls._lock:
            if cls._instance is None:
                cls._instance = BrowserManager(settings)
            return cls._instance

    async def ensure_browser(self):
        if self._browser is not None:
            return self._browser
        try:
            from playwright.async_api import async_playwright
        except Exception as exc:
            raise BrowserProviderUnavailable("BROWSER_PROVIDER_UNAVAILABLE") from exc

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.settings.playwright_headless,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        logger.info("browser_provider_configured", extra={"headless": self.settings.playwright_headless})
        return self._browser

    @asynccontextmanager
    async def page(self):
        browser = await self.ensure_browser()
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            viewport={"width": 390, "height": 844},
        )
        page = await context.new_page()
        page.set_default_timeout(self.settings.playwright_timeout_seconds * 1000)
        try:
            yield page
        finally:
            await page.close()
            await context.close()


class BrowserProvider(EthicalProviderClient):
    provider_name = "browser"

    async def _set_location(self, page, location: ProviderLocation) -> None:
        # Best-effort educational flow; selectors may evolve over time.
        if not location.pincode:
            return
        await page.goto("https://blinkit.com", wait_until="domcontentloaded")
        await asyncio.sleep(1.0 + random.uniform(0, 0.5))

    async def search(self, keyword: str, location: ProviderLocation) -> list[dict[str, Any]]:
        manager = await BrowserManager.get(self.settings)
        try:
            async with manager.page() as page:
                await self._set_location(page, location)
                await page.goto(f"https://blinkit.com/s/?q={keyword}", wait_until="domcontentloaded")
                await asyncio.sleep(self.settings.provider_base_delay_seconds + random.uniform(0, 0.5))
                cards = page.locator("[data-testid='product-card'], a[href*='/prn/']")
                count = min(await cards.count(), 12)
                results: list[dict[str, Any]] = []
                for i in range(count):
                    card = cards.nth(i)
                    name = await card.inner_text()
                    results.append({
                        "provider": "blinkit",
                        "external_product_id": f"browser-{i}-{abs(hash(name))}",
                        "name": name.strip().split("\n")[0][:180],
                        "stock_status": "unknown",
                        "_fetched_at": datetime.now(UTC).isoformat(),
                    })
                if not results:
                    logger.warning("BROWSER_PROVIDER_UNAVAILABLE", extra={"reason": "no_results", "query": keyword})
                return results
        except BrowserProviderUnavailable as exc:
            logger.warning("BROWSER_PROVIDER_UNAVAILABLE")
            raise RuntimeError("LIVE_PROVIDER_NOT_CONFIGURED") from exc
        except Exception as exc:
            logger.warning("BROWSER_PROVIDER_UNAVAILABLE", exc_info=True)
            raise RuntimeError("LIVE_PROVIDER_NOT_CONFIGURED") from exc

    async def fetch_product(self, external_product_id: str, location: ProviderLocation) -> dict[str, Any]:
        """
        FIX: Navigate to the actual product page (not the homepage) and attempt
        to extract real stock/price data from the DOM. Falls back to unknown
        gracefully when selectors don't match.
        """
        manager = await BrowserManager.get(self.settings)
        try:
            async with manager.page() as page:
                await self._set_location(page, location)
                # Navigate to the product page using the slug-style URL
                product_url = f"https://blinkit.com/prn/{external_product_id}/prid/{external_product_id}"
                await page.goto(product_url, wait_until="domcontentloaded")
                await asyncio.sleep(self.settings.provider_base_delay_seconds + random.uniform(0, 0.5))

                # Attempt to extract stock/price from common selectors (educational best-effort)
                name = external_product_id
                stock_status = "unknown"
                price = None
                mrp = None

                try:
                    name_el = page.locator("h1").first
                    if await name_el.count():
                        name = (await name_el.inner_text()).strip()[:255] or external_product_id
                except Exception:
                    pass

                try:
                    add_btn = page.locator("[data-testid='add-to-cart'], button:has-text('Add')")
                    if await add_btn.count():
                        stock_status = "in_stock"
                    oos = page.locator(":text('Out of stock'), :text('Notify me')")
                    if await oos.count():
                        stock_status = "out_of_stock"
                except Exception:
                    pass

                try:
                    price_el = page.locator("[data-testid='product-price'], .Product__UpdatedPrice-sc")
                    if await price_el.count():
                        raw = (await price_el.first.inner_text()).replace("₹", "").replace(",", "").strip()
                        price = float(raw) if raw else None
                except Exception:
                    pass

                return {
                    "provider": "blinkit",
                    "external_product_id": external_product_id,
                    "name": name,
                    "stock_status": stock_status,
                    "price": price,
                    "mrp": mrp,
                    "_fetched_at": datetime.now(UTC).isoformat(),
                }
        except BrowserProviderUnavailable as exc:
            logger.warning("BROWSER_PROVIDER_UNAVAILABLE")
            raise RuntimeError("LIVE_PROVIDER_NOT_CONFIGURED") from exc
        except Exception as exc:
            logger.warning("BROWSER_PROVIDER_UNAVAILABLE", exc_info=True)
            raise RuntimeError("LIVE_PROVIDER_NOT_CONFIGURED") from exc
