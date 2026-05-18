from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.entities import User
from app.schemas.dto import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    """Return the internal application user.

    The app is intended to run behind a VPN/private network, so password signup,
    login, and token issuance have been removed.
    """
    return user


@router.post("/signup", status_code=status.HTTP_410_GONE, include_in_schema=False)
@router.post("/login", status_code=status.HTTP_410_GONE, include_in_schema=False)
@router.post("/token", status_code=status.HTTP_410_GONE, include_in_schema=False)
async def password_auth_removed():
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Password authentication has been removed. Use /auth/me behind the private network.",
    )
