import base64
import hashlib
from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

# bcrypt is capped at 72 bytes — passwords longer than that are silently truncated
# (or raise ValueError in bcrypt >= 4.0). We pre-hash with SHA-256 so that:
#   - any password length is supported without truncation
#   - the input to bcrypt is always a fixed 44-char base64 string (< 72 bytes)
# This is the same strategy used by Django's BCryptSHA256PasswordHasher.

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def _prehash(password: str) -> str:
    """SHA-256 → base64 prehash so bcrypt never sees > 72 bytes."""
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")  # always 44 chars


def hash_password(password: str) -> str:
    return pwd_context.hash(_prehash(password))


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(_prehash(plain), hashed)
    except Exception:
        return False


def normalize_password_for_bcrypt(password: str) -> str:
    """Kept for backward compatibility — no longer used internally."""
    return password


def create_access_token(subject: str) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "exp": expires}, settings.secret_key, algorithm=settings.jwt_algorithm)
