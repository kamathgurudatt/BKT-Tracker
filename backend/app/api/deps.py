from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import get_db
from app.models.entities import User, UserRole

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login", auto_error=False)


async def get_current_user(token: str | None = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if settings.bootstrap_mode and not token:
        user = await db.scalar(select(User).where(User.email == "device@local", User.is_active.is_(True)))
        if user is None:
            user = User(email="device@local", full_name="Device User", hashed_password=hash_password("device-bootstrap"), role=UserRole.ADMIN)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc
    user = await db.scalar(select(User).where(User.email == subject, User.is_active.is_(True)))
    if user is None:
        raise credentials_exception
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
