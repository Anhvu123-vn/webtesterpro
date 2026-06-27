"""
Cấu hình database SQLAlchemy cho WebTesterPro.

Sử dụng SQLite làm database mặc định, có thể thay đổi qua biến môi trường DATABASE_URL.
"""

import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Tải biến môi trường từ file .env (nếu có)
load_dotenv()

# Thư mục lưu database — tạo tự động nếu chưa tồn tại
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATABASE_URL = f"sqlite:///{DATA_DIR / 'webtesterpro.db'}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# SQLite cần check_same_thread=False khi dùng với FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class cho tất cả SQLAlchemy models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependency cung cấp database session.
    Tự động đóng session sau khi request hoàn tất.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Khởi tạo tất cả bảng trong database (dùng cho dev hoặc fallback)."""
    # Import models để SQLAlchemy đăng ký metadata
    from webtesterpro.auth import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
