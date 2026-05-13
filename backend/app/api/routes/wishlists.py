from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import User, Wishlist
from app.schemas.dto import WishlistCreate, WishlistRead

router = APIRouter(prefix="/wishlists", tags=["wishlists"])


@router.get("", response_model=list[WishlistRead])
async def list_wishlists(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(Wishlist).where(Wishlist.user_id == user.id))).all()


@router.post("", response_model=WishlistRead, status_code=201)
async def create_wishlist(payload: WishlistCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    wishlist = Wishlist(user_id=user.id, **payload.model_dump())
    db.add(wishlist)
    await db.commit()
    await db.refresh(wishlist)
    return wishlist
