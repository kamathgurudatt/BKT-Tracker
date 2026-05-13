import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlalchemy import text

from app.api.routes import admin, auth, debug, locations, tracking, wishlists
from app.core.config import get_settings
from app.db.redis import redis_client
from app.db.session import AsyncSessionLocal

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])


async def _probe_dependencies() -> dict:
    db_ok = False
    redis_ok = False
    try:
        if AsyncSessionLocal is not None:
            async with AsyncSessionLocal() as db:
                await db.execute(text("SELECT 1"))
                db_ok = True
    except Exception:
        db_ok = False
    try:
        if redis_client is not None:
            await redis_client.ping()
            redis_ok = True
    except Exception:
        redis_ok = False
    return {
        "database": "ok" if db_ok else "unavailable",
        "redis": "ok" if redis_ok else "unavailable",
        "status": "ok" if db_ok and redis_ok else "degraded",
    }


async def _dependency_probe_loop(app: FastAPI) -> None:
    while True:
        app.state.dependency_status = await _probe_dependencies()
        await asyncio.sleep(max(5, settings.dependency_retry_interval_seconds))


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.dependency_status = {"database": "unavailable", "redis": "unavailable", "status": "degraded"}
    monitor_task = asyncio.create_task(_dependency_probe_loop(app))
    try:
        yield
    finally:
        monitor_task.cancel()
        with suppress(asyncio.CancelledError):
            await monitor_task


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Educational quick-commerce inventory monitoring API with safe provider throttling.",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
if settings.force_https:
    app.add_middleware(HTTPSRedirectMiddleware)

for router in (auth.router, locations.router, wishlists.router, tracking.router, debug.router, admin.router):
    app.include_router(router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health():
    status = getattr(app.state, "dependency_status", {"database": "unavailable", "redis": "unavailable", "status": "degraded"})
    body = {
        "status": status["status"],
        "service": settings.app_name,
        "bootstrap_mode": settings.bootstrap_mode,
        "database": status["database"],
        "redis": status["redis"],
    }
    return JSONResponse(status_code=200, content=body)
