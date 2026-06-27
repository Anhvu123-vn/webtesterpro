"""
Auth API routes: register, login, logout, refresh token.

Hỗ trợ cả JSON API và form-based login cho Jinja2 templates.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from webtesterpro.auth import auth as auth_utils
from webtesterpro.auth import crud
from webtesterpro.auth.dependencies import (
    get_current_active_user,
    get_current_admin_user,
)
from webtesterpro.auth.models import User
from webtesterpro.auth.schemas import MessageResponse, Token, UserCreate, UserLogin, UserResponse
from webtesterpro.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Đăng ký tài khoản mới.
    Email và username phải unique.
    """
    if crud.get_user_by_email(db, user_in.email.lower()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng.",
        )
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username đã được sử dụng.",
        )

    return crud.create_user(db, user_in)


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> Token:
    """
    Đăng nhập và nhận JWT tokens.
    Tokens cũng được set vào HttpOnly cookies cho web UI.
    """
    client_ip = request.client.host if request.client else "unknown"

    if not auth_utils.login_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quá nhiều lần thử đăng nhập. Vui lòng thử lại sau 15 phút.",
        )

    if not login_data.email and not login_data.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng cung cấp email hoặc username.",
        )

    user = auth_utils.authenticate_user(db, login_data)
    if not user:
        auth_utils.login_rate_limiter.record_failure(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/username hoặc mật khẩu không đúng.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa.",
        )

    auth_utils.login_rate_limiter.reset(client_ip)
    crud.update_last_login(db, user)

    access_token, refresh_token = auth_utils.create_token_pair(user.id)
    auth_utils.set_auth_cookies(response, access_token, refresh_token)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response) -> MessageResponse:
    """
    Đăng xuất — xóa tokens phía client (cookies).
    JWT stateless nên không cần blacklist server-side (có thể mở rộng sau).
    """
    auth_utils.clear_auth_cookies(response)
    return MessageResponse(message="Đăng xuất thành công.")


@router.post("/refresh", response_model=Token)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)) -> Token:
    """Làm mới access token bằng refresh token."""
    refresh = request.cookies.get(auth_utils.REFRESH_TOKEN_COOKIE)
    if not refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn.",
        )

    user_id = auth_utils.verify_token(refresh, expected_type="refresh")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn.",
        )

    user = crud.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại hoặc đã bị vô hiệu hóa.",
        )

    access_token, new_refresh = auth_utils.create_token_pair(user.id)
    auth_utils.set_auth_cookies(response, access_token, new_refresh)

    return Token(access_token=access_token, refresh_token=new_refresh)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Lấy thông tin user hiện tại."""
    return current_user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
) -> list[User]:
    """Admin: xem danh sách tất cả users."""
    return crud.get_users(db, skip=skip, limit=limit)
