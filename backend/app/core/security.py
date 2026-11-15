from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from app.core.config import get_settings

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, password)
    except (VerificationError, InvalidHashError):
        return False


def _secret() -> str:
    secret = get_settings().jwt_secret
    if secret is None or len(secret.get_secret_value()) < 32:
        raise RuntimeError('JWT_SECRET must contain at least 32 characters.')
    return secret.get_secret_value()


def create_access_token(user) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': str(user.id), 'ver': user.auth_version, 'iat': now, 'exp': now + timedelta(minutes=get_settings().access_token_minutes)}, _secret(), algorithm='HS256')


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=['HS256'], options={'require': ['sub','ver','exp','iat']})
