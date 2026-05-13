import logging

from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
try:
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True) if settings.redis_url else None
except Exception:
    logger.warning("Redis client initialization failed; running without Redis connectivity until configured.", exc_info=True)
    redis_client = None
