"""
Auth dependencies cho Dashboard (Jinja2 + HTMX).

Khác với auth/dependencies.py: redirect về trang login thay vì trả JSON 401
khi user chưa đăng nhập trên web UI.
"""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from webtesterpro.auth import auth as auth_utils
from webtesterpro.auth import crud
from webtesterpro.auth.dependencies import get_current_active_user, get_current_admin_user
from webtesterpro.auth.models import User
from webtesterpro.database import get_db

LOGIN_URL = "/login"


def get_current_user_for_page(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency cho trang web: redirect về login nếu chưa xác thực.
    Dùng cho các route dashboard cần bảo vệ.
    """
    token = request.cookies.get(auth_utils.ACCESS_TOKEN_COOKIE)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": f"{LOGIN_URL}?next={request.url.path}"},
        )

    user_id = auth_utils.verify_token(token, expected_type="access")
    if user_id is None:
        # Thử refresh token tự động — client sẽ gọi /auth/refresh qua HTMX nếu cần
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": f"{LOGIN_URL}?next={request.url.path}"},
        )

    user = crud.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": LOGIN_URL},
        )

    return user


def require_admin_for_page(
    current_user: User = Depends(get_current_user_for_page),
) -> User:
    """Yêu cầu quyền Admin trên dashboard."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập trang này.",
        )
    return current_user


def get_optional_user_for_page(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Lấy user cho navbar — không redirect nếu chưa login."""
    token = request.cookies.get(auth_utils.ACCESS_TOKEN_COOKIE)
    if not token:
        return None

    user_id = auth_utils.verify_token(token, expected_type="access")
    if user_id is None:
        return None

    user = crud.get_user_by_id(db, user_id)
    if user and user.is_active:
        return user
    return None
