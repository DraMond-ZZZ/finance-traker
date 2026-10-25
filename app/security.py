from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import JWT_EXPIRES_MINUTES, JWT_SECRET

ALGORITHM = "HS256"


def _pw(password: str) -> bytes:
    return password.encode("utf-8")[:72]  # batas bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_pw(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_pw(password), hashed.encode("utf-8"))
    except ValueError:
        return False


# Hash palsu agar waktu respons login relatif sama saat email tidak terdaftar
DUMMY_HASH = hash_password("dummy-password")


def _secret() -> str:
    if len(JWT_SECRET) < 16:
        raise RuntimeError("JWT_SECRET belum diatur atau terlalu pendek (minimal 16 karakter)")
    return JWT_SECRET


def create_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=JWT_EXPIRES_MINUTES)}
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> int | None:
    """Mengembalikan id user, atau None jika token tidak valid / kedaluwarsa."""
    secret = _secret()
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM], options={"require": ["exp", "sub"]})
        return int(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError):
        return None
