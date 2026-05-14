from app.providers.base import EthicalProviderClient
from app.providers.blinkit.client import BlinkitProvider
from app.providers.browser.client import BrowserProvider
from app.providers.instamart.client import InstamartProvider
from app.providers.zepto.client import ZeptoProvider

PROVIDERS: dict[str, type[EthicalProviderClient]] = {
    "blinkit": BrowserProvider,
    "blinkit_api": BlinkitProvider,
    "browser": BrowserProvider,
    "zepto": ZeptoProvider,
    "instamart": InstamartProvider,
}


def get_provider(name: str) -> EthicalProviderClient:
    return PROVIDERS.get(name, BrowserProvider)()
