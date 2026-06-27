"""
Analytics Service - Tính toán metrics và statistics cho dashboard.

Cung cấp:
- Score trends
- Module usage statistics
- Test frequency
- Performance metrics
"""

import json
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from webtesterpro.auth.models import AuditLog, Report, ScheduledTest, User
from webtesterpro.database import SessionLocal

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service để tính toán analytics metrics."""

    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> dict:
        """
        Lấy statistics tổng quan của user.
        
        Returns:
            Dict chứa:
            - total_tests: Tổng số tests
            - completed_tests: Tests đã hoàn thành
            - failed_tests: Tests thất bại
            - running_tests: Tests đang chạy
            - avg_score: Điểm trung bình
            - best_score: Điểm cao nhất
            - worst_score: Điểm thấp nhất
            - total_duration: Tổng thời gian test (giây)
        """
        reports = db.query(Report).filter(Report.user_id == user_id).all()
        
        if not reports:
            return {
                "total_tests": 0,
                "completed_tests": 0,
                "failed_tests": 0,
                "running_tests": 0,
                "avg_score": 0,
                "best_score": 0,
                "worst_score": 0,
                "total_duration": 0,
                "total_pages_crawled": 0,
            }
        
        scored = [r for r in reports if r.overall_score is not None]
        completed = [r for r in reports if r.status == "completed"]
        failed = [r for r in reports if r.status == "failed"]
        running = [r for r in reports if r.status == "running"]
        
        # Calculate duration from results if available
        total_duration = 0
        total_pages = 0
        for r in reports:
            if r.results_json:
                try:
                    data = json.loads(r.results_json)
                    total_duration += data.get("test_duration", 0)
                    crawl_results = data.get("crawl_results", {})
                    if isinstance(crawl_results, dict):
                        total_pages += crawl_results.get("pages_crawled", 0) or len(crawl_results.get("pages", []))
                except (json.JSONDecodeError, TypeError):
                    pass
        
        return {
            "total_tests": len(reports),
            "completed_tests": len(completed),
            "failed_tests": len(failed),
            "running_tests": len(running),
            "avg_score": int(sum(r.overall_score for r in scored) / len(scored)) if scored else 0,
            "best_score": max((r.overall_score for r in scored), default=0),
            "worst_score": min((r.overall_score for r in scored), default=0),
            "total_duration": int(total_duration),
            "total_pages_crawled": total_pages,
        }

    @staticmethod
    def get_score_trend(
        db: Session,
        user_id: Optional[int] = None,
        days: int = 30,
        limit: int = 50,
    ) -> list[dict]:
        """
        Lấy trend điểm số theo thời gian.
        
        Returns:
            List of {date, score, report_id} sorted by date
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = db.query(Report).filter(
            Report.created_at >= cutoff,
            Report.overall_score.isnot(None),
        )
        
        if user_id:
            query = query.filter(Report.user_id == user_id)
        
        reports = (
            query.order_by(Report.created_at.asc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "date": r.created_at.strftime("%Y-%m-%d"),
                "score": r.overall_score,
                "report_id": r.id,
                "url": r.url,
            }
            for r in reports
        ]

    @staticmethod
    def get_module_usage(
        db: Session,
        user_id: Optional[int] = None,
        days: int = 30,
    ) -> list[dict]:
        """
        Lấy statistics về việc sử dụng modules.
        
        Returns:
            List of {module_id, module_name, count, percentage}
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = db.query(Report.modules_run).filter(
            Report.created_at >= cutoff,
            Report.modules_run.isnot(None),
        )
        
        if user_id:
            query = query.filter(Report.user_id == user_id)
        
        reports = query.all()
        
        # Count modules
        module_counts = Counter()
        total_runs = 0
        for r in reports:
            if r.modules_run:
                try:
                    modules = json.loads(r.modules_run)
                    if isinstance(modules, list):
                        for m in modules:
                            module_counts[m] += 1
                            total_runs += 1
                except json.JSONDecodeError:
                    pass
        
        # Module display names
        module_names = {
            "crawler": "Crawler",
            "scanner": "Scanner",
            "analyzer": "Analyzer",
            "performance": "Performance",
            "security": "Security",
            "accessibility": "Accessibility",
            "seo": "SEO",
            "visual": "Visual",
            "monitor": "Monitor",
        }
        
        return [
            {
                "module_id": module_id,
                "module_name": module_names.get(module_id, module_id.title()),
                "count": count,
                "percentage": round(count / total_runs * 100, 1) if total_runs > 0 else 0,
            }
            for module_id, count in module_counts.most_common()
        ]

    @staticmethod
    def get_test_frequency(
        db: Session,
        user_id: Optional[int] = None,
        days: int = 30,
    ) -> list[dict]:
        """
        Lấy số lượng tests theo ngày.
        
        Returns:
            List of {date, count, avg_score}
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = db.query(
            func.date(Report.created_at).label("date"),
            func.count(Report.id).label("count"),
            func.avg(Report.overall_score).label("avg_score"),
        ).filter(Report.created_at >= cutoff)
        
        if user_id:
            query = query.filter(Report.user_id == user_id)
        
        results = (
            query.group_by(func.date(Report.created_at))
            .order_by("date")
            .all()
        )
        
        return [
            {
                "date": str(r.date),
                "count": r.count,
                "avg_score": int(r.avg_score) if r.avg_score else None,
            }
            for r in results
        ]

    @staticmethod
    def get_score_distribution(
        db: Session,
        user_id: Optional[int] = None,
        days: int = 30,
    ) -> dict:
        """
        Lấy phân bố điểm số.
        
        Returns:
            Dict với ranges: {excellent: 80-100, good: 60-79, fair: 40-59, poor: 0-39}
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = db.query(Report).filter(
            Report.created_at >= cutoff,
            Report.overall_score.isnot(None),
        )
        
        if user_id:
            query = query.filter(Report.user_id == user_id)
        
        reports = query.all()
        
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        for r in reports:
            score = r.overall_score
            if score >= 80:
                distribution["excellent"] += 1
            elif score >= 60:
                distribution["good"] += 1
            elif score >= 40:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1
        
        return distribution

    @staticmethod
    def get_performance_stats(
        db: Session,
        user_id: Optional[int] = None,
        days: int = 30,
    ) -> dict:
        """
        Lấy performance metrics từ test results.
        
        Returns:
            Dict với avg_load_time, avg_dom_size, v.v.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = db.query(Report.results_json).filter(
            Report.created_at >= cutoff,
            Report.results_json.isnot(None),
        )
        
        if user_id:
            query = query.filter(Report.user_id == user_id)
        
        results = query.all()
        
        load_times = []
        dom_sizes = []
        page_counts = []
        
        for r in results:
            if r.results_json:
                try:
                    data = json.loads(r.results_json)
                    
                    # Performance results
                    perf = data.get("performance_results", {})
                    if perf:
                        load_time = perf.get("load_time") or perf.get("total_time")
                        if load_time:
                            load_times.append(float(load_time))
                        
                        dom_size = perf.get("dom_size") or perf.get("dom_nodes")
                        if dom_size:
                            dom_sizes.append(int(dom_size))
                    
                    # Crawl results
                    crawl = data.get("crawl_results", {})
                    if crawl:
                        pages = crawl.get("pages_crawled") or len(crawl.get("pages", []))
                        if pages:
                            page_counts.append(pages)
                            
                except (json.JSONDecodeError, TypeError, ValueError):
                    pass
        
        def avg(lst):
            return int(sum(lst) / len(lst)) if lst else 0
        
        return {
            "avg_load_time_ms": avg(load_times),
            "avg_dom_size": avg(dom_sizes),
            "avg_pages_crawled": avg(page_counts),
            "max_pages_crawled": max(page_counts) if page_counts else 0,
        }

    @staticmethod
    def get_recent_tests(
        db: Session,
        user_id: Optional[int] = None,
        limit: int = 10,
    ) -> list[Report]:
        """Lấy tests gần đây nhất."""
        query = db.query(Report)
        if user_id:
            query = query.filter(Report.user_id == user_id)
        return query.order_by(Report.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_top_urls(
        db: Session,
        user_id: Optional[int] = None,
        limit: int = 5,
    ) -> list[dict]:
        """Lấy top URLs được test nhiều nhất."""
        from urllib.parse import urlparse
        
        query = db.query(
            Report.url,
            func.count(Report.id).label("count"),
            func.avg(Report.overall_score).label("avg_score"),
        )
        
        if user_id:
            query = query.filter(Report.user_id == user_id)
        
        results = (
            query.group_by(Report.url)
            .order_by(func.count(Report.id).desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "url": r.url,
                "domain": urlparse(r.url).netloc or r.url,
                "count": r.count,
                "avg_score": int(r.avg_score) if r.avg_score else 0,
            }
            for r in results
        ]


# Singleton instance
analytics_service = AnalyticsService()
