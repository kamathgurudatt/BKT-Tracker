from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import get_or_create_internal_user
from app.db.session import get_db
from app.models.entities import User, UserRole

settings = get_settings()


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    """Resolve the internal service user for this VPN/private-network app.

    App-level credential authentication is intentionally disabled. Keep
    this service behind Railway private networking, a corporate VPN, or another
    trusted ingress layer.
    """
    if not settings.internal_auth_enabled:
        raise HTTPException(status_code=503, detail="Internal authentication is disabled")
    return await get_or_create_internal_user(db)


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
