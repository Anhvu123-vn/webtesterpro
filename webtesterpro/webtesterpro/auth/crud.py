"""
CRUD operations cho User và Report.

Tách logic database khỏi router để dễ test và mở rộng.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from webtesterpro.auth import auth as auth_utils
from webtesterpro.auth.models import Report, User
from webtesterpro.auth.schemas import ReportCreate, UserCreate


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Lấy user theo ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Lấy user theo email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Lấy user theo username."""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Lấy danh sách users (Admin only)."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_in: UserCreate, is_admin: bool = False) -> User:
    """Tạo user mới với password đã hash."""
    db_user = User(
        email=user_in.email.lower(),
        username=user_in.username,
        hashed_password=auth_utils.hash_password(user_in.password),
        is_admin=is_admin,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_last_login(db: Session, user: User) -> User:
    """Cập nhật thời gian đăng nhập gần nhất."""
    user.last_login = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_report(db: Session, report_in: ReportCreate, user_id: int) -> Report:
    """Tạo report mới gắn với user."""
    db_report = Report(**report_in.model_dump(), user_id=user_id)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_reports_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[Report]:
    """Lấy reports của một user."""
    return (
        db.query(Report)
        .filter(Report.user_id == user_id)
        .order_by(Report.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_reports(db: Session, skip: int = 0, limit: int = 100) -> List[Report]:
    """Lấy tất cả reports (Admin only)."""
    return db.query(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()


def get_report_by_id(db: Session, report_id: int) -> Optional[Report]:
    """Lấy report theo ID."""
    return db.query(Report).filter(Report.id == report_id).first()


def update_report(db: Session, report: Report, **fields) -> Report:
    """Cập nhật các field của report."""
    for key, value in fields.items():
        setattr(report, key, value)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def user_can_view_report(user: User, report: Report) -> bool:
    """Kiểm tra user có quyền xem report không."""
    return user.is_admin or report.user_id == user.id
