"""
FastAPI dependencies cho authentication.

Cung cấp get_current_user, get_current_active_user và kiểm tra quyền Admin.
"""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from webtesterpro.auth import auth as auth_utils
from webtesterpro.auth import crud
from webtesterpro.auth.models import User
from webtesterpro.database import get_db

# Bearer token cho API requests
bearer_scheme = HTTPBearer(auto_error=False)


def _extract_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials],
) -> Optional[str]:
    """
    Lấy token từ Authorization header hoặc cookie.
    Ưu tiên Bearer header, fallback sang cookie (cho web UI).
    """
    if credentials and credentials.credentials:
        return credentials.credentials
    return request.cookies.get(auth_utils.ACCESS_TOKEN_COOKIE)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> User:
    """
    Dependency lấy user hiện tại từ JWT.
    Raise 401 nếu token không hợp lệ hoặc user không tồn tại.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực. Vui lòng đăng nhập lại.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = _extract_token(request, credentials)
    if not token:
        raise credentials_exception

    user_id = auth_utils.verify_token(token, expected_type="access")
    if user_id is None:
        raise credentials_exception

    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency yêu cầu user đang active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa.",
        )
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency yêu cầu quyền Admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập tài nguyên này.",
        )
    return current_user


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[User]:
    """Lấy user nếu đã đăng nhập; trả về None nếu chưa."""
    token = _extract_token(request, credentials)
    if not token:
        return None

    user_id = auth_utils.verify_token(token, expected_type="access")
    if user_id is None:
        return None

    return crud.get_user_by_id(db, user_id)
