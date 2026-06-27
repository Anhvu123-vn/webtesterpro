"""
Compare Service - So sánh 2 reports với nhau.
"""

import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from webtesterpro.auth.models import Report
from webtesterpro.dashboard.services.test_runner import load_report_results

logger = logging.getLogger(__name__)


class CompareService:
    """Service để so sánh 2 reports."""

    @staticmethod
    def _get_scores(results: dict) -> dict:
        """Extract scores from results - handle different data structures."""
        # Try common keys
        scores = results.get("scores", {})
        if not scores and isinstance(scores, dict):
            # Maybe scores are nested differently
            for key in ["module_scores", "results", "data"]:
                nested = results.get(key, {})
                if isinstance(nested, dict) and "scores" in nested:
                    scores = nested["scores"]
                    break
        return scores if isinstance(scores, dict) else {}

    @staticmethod
    def _get_issues(results: dict) -> list:
        """Extract issues from results - handle different data structures."""
        issues = results.get("issues", [])
        
        # Try other common keys
        if not issues:
            issues = results.get("findings", [])
        if not issues:
            issues = results.get("problems", [])
        if not issues:
            # Check nested structure
            for key in ["security_results", "scan_results", "results"]:
                nested = results.get(key, {})
                if isinstance(nested, dict):
                    if "issues" in nested:
                        issues = nested["issues"]
                        break
                    if "findings" in nested:
                        issues = nested["findings"]
                        break
        
        return issues if isinstance(issues, list) else []

    @staticmethod
    def _get_performance(results: dict) -> dict:
        """Extract performance data from results."""
        perf = results.get("performance_results", {})
        if not perf:
            perf = results.get("performance", {})
        if not perf:
            for key in ["results", "data"]:
                nested = results.get(key, {})
                if isinstance(nested, dict) and "performance" in nested:
                    perf = nested["performance"]
                    break
        return perf if isinstance(perf, dict) else {}

    @staticmethod
    def compare_reports(report1: Report, report2: Report) -> dict:
        """
        So sánh 2 reports và trả về diff.
        
        Args:
            report1: Report đầu tiên (thường là cũ hơn)
            report2: Report thứ hai (thường là mới hơn)
        
        Returns:
            Dict chứa comparison data
        """
        results1 = load_report_results(report1) or {}
        results2 = load_report_results(report2) or {}
        
        # Get scores with fallback handling
        scores1 = CompareService._get_scores(results1)
        scores2 = CompareService._get_scores(results2)
        
        # Calculate score changes
        score_changes = {}
        all_modules = set(list(scores1.keys()) + list(scores2.keys()))
        
        for module in all_modules:
            s1 = scores1.get(module, 0) or 0
            s2 = scores2.get(module, 0) or 0
            change = s2 - s1
            score_changes[module] = {
                "before": s1 if s1 else None,
                "after": s2 if s2 else None,
                "change": change,
                "improved": change > 0,
                "declined": change < 0,
            }
        
        # Overall score change
        score1 = report1.overall_score or 0
        score2 = report2.overall_score or 0
        overall_change = score2 - score1
        
        # Get issues
        issues1 = CompareService._get_issues(results1)
        issues2 = CompareService._get_issues(results2)
        
        # Count by severity
        def count_issues(issues):
            counts = {"critical": 0, "warning": 0, "info": 0, "error": 0}
            for issue in issues:
                if isinstance(issue, dict):
                    sev = issue.get("severity", "").lower()
                    if sev in counts:
                        counts[sev] += 1
                    elif sev == "high" or sev == "high-priority":
                        counts["critical"] += 1
                    elif sev == "medium" or sev == "medium-priority":
                        counts["warning"] += 1
                    elif sev == "low":
                        counts["info"] += 1
                elif isinstance(issue, str):
                    counts["info"] += 1
            return counts
        
        issues_before = count_issues(issues1)
        issues_after = count_issues(issues2)
        
        # Count total issues
        total_before = len(issues1)
        total_after = len(issues2)
        
        # Performance comparison
        perf1 = CompareService._get_performance(results1)
        perf2 = CompareService._get_performance(results2)
        
        perf_changes = {}
        for key in ["load_time", "total_time", "dom_size", "dom_nodes", "request_count", "response_time"]:
            v1 = perf1.get(key)
            v2 = perf2.get(key)
            if v1 is not None and v2 is not None:
                perf_changes[key] = {
                    "before": v1,
                    "after": v2,
                    "change": v2 - v1,
                    "improved": key in ["load_time", "total_time", "response_time"] and v2 < v1,
                }
        
        return {
            "report1": {
                "id": report1.id,
                "title": report1.title,
                "url": report1.url,
                "score": score1 if score1 else None,
                "created_at": report1.created_at.isoformat() if report1.created_at else None,
            },
            "report2": {
                "id": report2.id,
                "title": report2.title,
                "url": report2.url,
                "score": score2 if score2 else None,
                "created_at": report2.created_at.isoformat() if report2.created_at else None,
            },
            "overall_change": overall_change,
            "score_changes": score_changes,
            "issues_comparison": {
                "before": issues_before,
                "after": issues_after,
                "total_before": total_before,
                "total_after": total_after,
                "critical_change": issues_after["critical"] - issues_before["critical"],
                "warning_change": issues_after["warning"] - issues_before["warning"],
                "info_change": issues_after["info"] - issues_before["info"],
                "new_count": total_after - total_before if total_after > total_before else 0,
                "resolved_count": total_before - total_after if total_before > total_after else 0,
            },
            "performance_changes": perf_changes,
            "improved": overall_change > 0,
            "declined": overall_change < 0,
            "unchanged": overall_change == 0,
        }

    @staticmethod
    def get_comparable_reports(db: Session, user_id: int, url: str = None, limit: int = 10) -> list[Report]:
        """
        Lấy danh sách reports có thể so sánh.
        
        Args:
            db: Database session
            user_id: ID của user
            url: Filter theo URL (optional)
            limit: Số lượng tối đa
        
        Returns:
            List of Report objects
        """
        query = db.query(Report).filter(
            Report.user_id == user_id,
            Report.status == "completed",
            Report.overall_score.isnot(None),
        )
        
        if url:
            query = query.filter(Report.url == url)
        
        return query.order_by(Report.created_at.desc()).limit(limit).all()


# Singleton instance
compare_service = CompareService()
