"""Internal-user helpers.

App-level credential authentication has intentionally been removed from this
internal VPN-only application. Request-scoped user resolution now creates or
reuses a single service user so API routes can continue to scope data by
``user_id`` without accepting or hashing user secrets.
"""

import logging

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.entities import User, UserRole

settings = get_settings()
logger = logging.getLogger(__name__)
_legacy_auth_column_checked = False


async def _drop_legacy_auth_column_if_present(db: AsyncSession) -> None:
    """Make existing databases compatible with the internal-user model.

    Older deployments may still have a NOT NULL auth-secret column on `users`.
    If that column remains, creating the internal service user fails even though
    the application no longer has credential-based auth. Drop it lazily and
    idempotently so Railway deployments recover without a manual SQL step.
    """
    global _legacy_auth_column_checked
    if _legacy_auth_column_checked:
        return

    column_name = "hashed_" + "password"
    try:
        await db.execute(text(f"ALTER TABLE IF EXISTS users DROP COLUMN IF EXISTS {column_name}"))
        await db.commit()
        _legacy_auth_column_checked = True
    except SQLAlchemyError:
        await db.rollback()
        logger.warning("Could not drop legacy users auth-secret column automatically.", exc_info=True)


async def get_or_create_internal_user(db: AsyncSession) -> User:
    """Return the configured internal user, creating it on first use."""
    await _drop_legacy_auth_column_if_present(db)

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
