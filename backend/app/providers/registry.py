from app.providers.base import EthicalProviderClient
from app.providers.blinkit.client import BlinkitProvider
from app.providers.instamart.client import InstamartProvider
from app.providers.zepto.client import ZeptoProvider

PROVIDERS: dict[str, type[EthicalProviderClient]] = {
    "blinkit": BlinkitProvider,
    "zepto": ZeptoProvider,
    "instamart": InstamartProvider,
}


def get_provider(name: str) -> EthicalProviderClient:
    return PROVIDERS.get(name, BlinkitProvider)()
