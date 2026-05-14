import logging
from urllib.parse import urlsplit, urlunsplit

from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def _mask_redis_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.password:
        netloc = parsed.netloc.replace(parsed.password, "***")
    else:
        netloc = parsed.netloc
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


try:
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True) if settings.redis_url else None
    if redis_client is None:
        logger.warning("Redis URL is not configured; running without Redis connectivity.")
    else:
        logger.info("Redis client initialized for %s", _mask_redis_url(settings.redis_url))
except Exception:
    logger.warning("Redis client initialization failed; running without Redis connectivity until configured.", exc_info=True)
    redis_client = None
