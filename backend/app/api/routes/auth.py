from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.entities import User
from app.schemas.dto import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    """Return the internal application user resolved by private-network access."""
    return user
