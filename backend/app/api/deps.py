from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_or_create_internal_user
from app.db.session import get_db
from app.models.entities import User, UserRole


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    """Resolve the internal service user for this application."""
    return await get_or_create_internal_user(db)


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
