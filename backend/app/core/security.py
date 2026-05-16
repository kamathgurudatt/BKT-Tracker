from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False,
)
settings = get_settings()


def normalize_password_for_bcrypt(password: str) -> str:
    encoded = password.encode("utf-8")
    if len(encoded) <= 72:
        return password
    return encoded[:72].decode("utf-8", errors="ignore")


def hash_password(password: str) -> str:
    normalized = normalize_password_for_bcrypt(password)
    try:
        return pwd_context.hash(normalized)
    except ValueError:
        return pwd_context.hash(normalized[:72])


def verify_password(password: str, hashed_password: str) -> bool:
    normalized = normalize_password_for_bcrypt(password)
    try:
        return pwd_context.verify(normalized, hashed_password)
    except ValueError:
        try:
            return pwd_context.verify(normalized[:72], hashed_password)
        except ValueError:
            return False


def create_access_token(subject: str) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "exp": expires}, settings.secret_key, algorithm=settings.jwt_algorithm)
