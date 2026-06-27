"""
JWT utilities, password hashing và rate limiting cho login.

Security:
- bcrypt hashing qua passlib
- Access token: 30 phút
- Refresh token: 7 ngày
- Rate limit cơ bản theo IP cho endpoint login
"""

import os
import secrets
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

# --- Cấu hình JWT ---
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Cookie settings
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_HTTPONLY = True
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash mật khẩu bằng bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Xác minh mật khẩu với hash đã lưu."""
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(data: Dict[str, Any], expires_delta: timedelta, token_type: str) -> str:
    """Tạo JWT token với payload và thời hạn."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    """Tạo access token (30 phút mặc định)."""
    return _create_token(
        {"sub": str(user_id)},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(user_id: int) -> str:
    """Tạo refresh token (7 ngày mặc định)."""
    return _create_token(
        {"sub": str(user_id)},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def create_token_pair(user_id: int) -> Tuple[str, str]:
    """Tạo cặp access + refresh token."""
    return create_access_token(user_id), create_refresh_token(user_id)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Giải mã JWT; trả về None nếu token không hợp lệ."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, expected_type: str = "access") -> Optional[int]:
    """
    Xác minh token và trả về user_id.
    Kiểm tra cả loại token (access/refresh).
    """
    payload = decode_token(token)
    if not payload:
        return None
    if payload.get("type") != expected_type:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        return int(sub)
    except (TypeError, ValueError):
        return None


# --- Rate limiting cơ bản cho login ---
class LoginRateLimiter:
    """
    Giới hạn số lần thử đăng nhập theo IP.
    Mặc định: tối đa 5 lần / 15 phút.
    """

    def __init__(self, max_attempts: int = 5, window_seconds: int = 900):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: Dict[str, list] = defaultdict(list)

    def _cleanup(self, ip: str, now: float) -> None:
        """Xóa các attempt cũ ngoài time window."""
        cutoff = now - self.window_seconds
        self._attempts[ip] = [t for t in self._attempts[ip] if t > cutoff]

    def is_allowed(self, ip: str) -> bool:
        """Kiểm tra IP còn được phép thử đăng nhập không."""
        now = time.time()
        self._cleanup(ip, now)
        return len(self._attempts[ip]) < self.max_attempts

    def record_failure(self, ip: str) -> None:
        """Ghi nhận một lần đăng nhập thất bại."""
        self._attempts[ip].append(time.time())

    def reset(self, ip: str) -> None:
        """Reset counter sau khi đăng nhập thành công."""
        self._attempts.pop(ip, None)


login_rate_limiter = LoginRateLimiter()


def authenticate_user(db, login_data) -> Optional[Any]:
    """
    Xác thực user bằng email hoặc username + password.
    Trả về User nếu hợp lệ, None nếu không.
    """
    from webtesterpro.auth import crud

    user = None
    if login_data.email:
        user = crud.get_user_by_email(db, login_data.email.lower())
    elif login_data.username:
        user = crud.get_user_by_username(db, login_data.username)

    if not user or not verify_password(login_data.password, user.hashed_password):
        return None
    return user


def set_auth_cookies(response, access_token: str, refresh_token: str) -> None:
    """Đặt JWT vào HttpOnly cookies an toàn."""
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/",
    )


def clear_auth_cookies(response) -> None:
    """Xóa auth cookies khi logout."""
    response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/")
    response.delete_cookie(REFRESH_TOKEN_COOKIE, path="/")
