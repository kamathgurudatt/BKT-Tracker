from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, normalize_password_for_bcrypt, verify_password
from app.db.session import get_db
from app.models.entities import User
from app.schemas.dto import LoginRequest, Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=201)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    if await db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    try:
        user = User(email=payload.email, hashed_password=hash_password(payload.password), full_name=payload.full_name)
    except ValueError:
        safe_password = normalize_password_for_bcrypt(payload.password)
        user = User(email=payload.email, hashed_password=hash_password(safe_password), full_name=payload.full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == payload.email))
    is_valid = bool(user and verify_password(payload.password, user.hashed_password))
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return Token(access_token=create_access_token(user.email))


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    return user
