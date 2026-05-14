from app.providers.browser.client import BrowserProvider
from app.providers.registry import get_provider
from app.providers.blinkit.client import BlinkitProvider


def test_default_provider_is_browser():
    provider = get_provider("unknown-provider")
    assert isinstance(provider, BrowserProvider)


def test_blinkit_templates_validation():
    assert BlinkitProvider._validate_template("https://blinkit.com/search?q=test")
    assert not BlinkitProvider._validate_template("https://authorized.example/search")
    assert not BlinkitProvider._validate_template("http://localhost/search")
