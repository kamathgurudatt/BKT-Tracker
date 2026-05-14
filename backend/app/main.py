import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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
logger = logging.getLogger(__name__)
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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled request error: %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
@app.middleware("http")
async def conditional_https_redirect(request: Request, call_next):
    if settings.force_https and request.url.scheme == "http" and not request.url.path.startswith("/health/"):
        https_url = request.url.replace(scheme="https")
        return JSONResponse(status_code=307, content={"detail": "Use HTTPS", "redirect_to": str(https_url)})
    return await call_next(request)

for router in (auth.router, locations.router, wishlists.router, tracking.router, debug.router, admin.router):
    app.include_router(router, prefix=settings.api_v1_prefix)


@app.get("/health/live")
async def health_live():
    return {"status": "ok", "service": "alive"}


@app.get("/health/ready")
async def health_ready():
    checks: dict[str, str] = {}
    try:
        if AsyncSessionLocal is None:
            raise RuntimeError("Database session factory unavailable")
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as exc:
        checks["db"] = str(exc)

    try:
        if redis_client is None:
            raise RuntimeError("Redis client unavailable")
        await redis_client.ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = str(exc)

    providers_ok = bool(settings.blinkit_search_url_template and settings.blinkit_product_url_template)
    checks["providers"] = "ok" if providers_ok else "not_configured"

    required_ok = checks.get("db") == "ok" and checks.get("redis") == "ok"
    overall = "ready" if (required_ok and providers_ok) else "degraded"
    body = {"status": overall, "dependencies": checks}
    return JSONResponse(content=body, status_code=200 if required_ok else 503)
