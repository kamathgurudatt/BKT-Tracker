"""Internal-user helpers.

Password-based authentication has intentionally been removed from this internal
VPN-only application. Request-scoped user resolution now creates or reuses a
single service user so API routes can continue to scope data by ``user_id``
without accepting, validating, or hashing passwords.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.entities import User, UserRole

settings = get_settings()


async def get_or_create_internal_user(db: AsyncSession) -> User:
    """Return the configured internal user, creating it on first use."""
    user = await db.scalar(select(User).where(User.email == settings.internal_device_email, User.is_active.is_(True)))
    desired_role = UserRole.ADMIN if settings.internal_device_is_admin else UserRole.USER
    if user is None:
        user = User(
            email=settings.internal_device_email,
            full_name=settings.internal_device_full_name,
            role=desired_role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    changed = False
    if user.full_name != settings.internal_device_full_name:
        user.full_name = settings.internal_device_full_name
        changed = True
    if user.role != desired_role:
        user.role = desired_role
        changed = True
    if changed:
        await db.commit()
        await db.refresh(user)
    return user
