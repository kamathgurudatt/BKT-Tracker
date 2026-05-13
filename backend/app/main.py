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

app = FastAPI(title=settings.app_name, version="1.0.0", description="Educational quick-commerce inventory monitoring API with safe provider throttling.")
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
    return {"status": "ok"}


@app.get("/ready")
async def ready():
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

    all_ok = all(value == "ok" for value in checks.values())
    body = {"status": "ready" if all_ok else "degraded", **checks}
    return JSONResponse(content=body, status_code=200 if all_ok else 503)
