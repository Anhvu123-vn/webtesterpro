"""
Audit Service - Ghi log hoạt động của người dùng.

Sử dụng để track:
- Ai đã làm gì (login, logout, tạo test, xem report...)
- Thời gian
- IP address
- User agent
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from webtesterpro.auth.models import AuditLog, Report, User
from webtesterpro.database import SessionLocal

logger = logging.getLogger(__name__)


class AuditService:
    """Service để ghi và truy vấn audit logs."""

    # Action types
    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_LOGIN_FAILED = "login_failed"
    ACTION_REGISTER = "register"
    
    ACTION_TEST_START = "test_start"
    ACTION_TEST_COMPLETE = "test_complete"
    ACTION_TEST_FAILED = "test_failed"
    ACTION_TEST_VIEW = "test_view"
    ACTION_TEST_DELETE = "test_delete"
    ACTION_TEST_SHARE = "test_share"
    
    ACTION_USER_CREATE = "user_create"
    ACTION_USER_UPDATE = "user_update"
    ACTION_USER_DELETE = "user_delete"
    
    RESOURCE_USER = "user"
    RESOURCE_REPORT = "report"
    RESOURCE_SYSTEM = "system"

    @staticmethod
    def log(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Ghi một audit log entry.
        
        Args:
            db: Database session
            action: Loại hành động (xem constants bên trên)
            user_id: ID của user thực hiện (None nếu anonymous)
            resource_type: Loại resource (user, report, system...)
            resource_id: ID của resource bị tác động
            details: Dict chứa thông tin bổ sung
            ip_address: IP của client
            user_agent: User agent string
        
        Returns:
            AuditLog object đã được tạo
        """
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=json.dumps(details, ensure_ascii=False) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            return audit_log
        except Exception as exc:
            logger.error(f"Failed to write audit log: {exc}")
            db.rollback()
            return None

    @staticmethod
    def log_user_action(
        action: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Ghi audit log với session riêng (cho background tasks).
        """
        db = SessionLocal()
        try:
            AuditService.log(
                db, action, user_id, resource_type, resource_id,
                details, ip_address, user_agent
            )
        finally:
            db.close()

    @staticmethod
    def get_user_activity(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        """Lấy lịch sử hoạt động của một user."""
        return (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_recent_activity(
        db: Session,
        days: int = 7,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Lấy hoạt động gần đây trong N ngày."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return (
            db.query(AuditLog)
            .filter(AuditLog.created_at >= cutoff)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_activity_stats(
        db: Session,
        user_id: Optional[int] = None,
        days: int = 30,
    ) -> dict:
        """
        Lấy statistics về hoạt động.
        
        Returns:
            Dict chứa:
            - total_actions: Tổng số hành động
            - actions_by_type: Dict count theo action type
            - daily_counts: List {date, count} trong 30 ngày
            - hourly_counts: List count theo giờ trong ngày
        """
        from sqlalchemy import func
        from collections import Counter
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = db.query(AuditLog).filter(AuditLog.created_at >= cutoff)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        logs = query.order_by(AuditLog.created_at.desc()).all()
        
        # Count by type
        action_counts = Counter(log.action for log in logs)
        
        # Daily counts
        daily_counts = {}
        for log in logs:
            date_key = log.created_at.strftime("%Y-%m-%d")
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
        
        # Hourly counts
        hourly_counts = [0] * 24
        for log in logs:
            hourly_counts[log.created_at.hour] += 1
        
        return {
            "total_actions": len(logs),
            "actions_by_type": dict(action_counts),
            "daily_counts": [
                {"date": date, "count": count}
                for date, count in sorted(daily_counts.items())
            ],
            "hourly_counts": hourly_counts,
        }


# Singleton instance
audit_service = AuditService()
