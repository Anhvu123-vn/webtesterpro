"""
Export Service - Export reports to PDF, CSV, and other formats.
"""

import csv
import io
import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from webtesterpro.auth.models import Report, ShareToken
from webtesterpro.database import SessionLocal

logger = logging.getLogger(__name__)


class ExportService:
    """Service để export reports ra các format khác nhau."""

    @staticmethod
    def generate_csv(report: Report, results: dict) -> str:
        """
        Generate CSV export từ report results.
        
        Args:
            report: Report model instance
            results: Full results dict
        
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "WebTesterPro Report",
            "",
            "",
            "",
        ])
        writer.writerow(["URL", report.url])
        writer.writerow(["Title", report.title])
        writer.writerow(["Score", f"{report.overall_score}/100" if report.overall_score else "N/A"])
        writer.writerow(["Date", report.created_at.strftime("%Y-%m-%d %H:%M:%S") if report.created_at else "N/A"])
        writer.writerow(["Modules", report.modules_run or "N/A"])
        writer.writerow([])
        
        # Scores
        writer.writerow(["Module Scores"])
        scores = results.get("scores", {})
        if isinstance(scores, dict):
            for module, score in scores.items():
                writer.writerow([module.title(), score])
        
        writer.writerow([])
        
        # Issues
        writer.writerow(["Issues Found"])
        issues = results.get("issues", [])
        if issues:
            writer.writerow(["Severity", "Category", "Title", "Description"])
            for issue in issues:
                if isinstance(issue, dict):
                    writer.writerow([
                        issue.get("severity", "unknown"),
                        issue.get("category", "unknown"),
                        issue.get("title", ""),
                        issue.get("description", ""),
                    ])
        
        writer.writerow([])
        
        # Performance metrics
        perf = results.get("performance_results", {})
        if perf:
            writer.writerow(["Performance Metrics"])
            for key, value in perf.items():
                if isinstance(value, (int, float, str)):
                    writer.writerow([key.title(), value])
        
        return output.getvalue()

    @staticmethod
    def generate_html_report(report: Report, results: dict) -> str:
        """
        Generate HTML report (standalone, không cần server).
        
        Args:
            report: Report model instance
            results: Full results dict
        
        Returns:
            HTML string
        """
        scores = results.get("scores", {})
        issues = results.get("issues", [])
        
        # Calculate score color
        def get_score_color(score):
            if score >= 80:
                return "#10b981"  # emerald
            elif score >= 50:
                return "#f59e0b"  # amber
            else:
                return "#ef4444"  # red
        
        score_color = get_score_color(report.overall_score or 0)
        
        html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report - {report.title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #f1f5f9;
            padding: 2rem;
            line-height: 1.6;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border: 1px solid #334155;
            border-radius: 1rem;
            padding: 2rem;
            margin-bottom: 2rem;
        }}
        .score-circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 4px solid {score_color};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            font-weight: bold;
            margin: 1rem 0;
        }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0; }}
        .card {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 0.75rem;
            padding: 1rem;
        }}
        .card h3 {{ color: #94a3b8; font-size: 0.875rem; margin-bottom: 0.5rem; }}
        .card p {{ font-size: 1.25rem; font-weight: bold; }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge-critical {{ background: #ef444420; color: #ef4444; border: 1px solid #ef444440; }}
        .badge-warning {{ background: #f59e0b20; color: #f59e0b; border: 1px solid #f59e0b40; }}
        .badge-info {{ background: #3b82f620; color: #3b82f6; border: 1px solid #3b82f640; }}
        .issues li {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 0.5rem;
        }}
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-size: 0.875rem;
        }}
        @media print {{
            body {{ background: white; color: black; }}
            .card, .header, .issues li {{ border-color: #ddd; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="font-size: 1.5rem; margin-bottom: 0.5rem;">{report.title}</h1>
            <p style="color: #64748b; margin-bottom: 1rem;">{report.url}</p>
            <div style="display: flex; align-items: center; gap: 2rem; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <div class="score-circle">{report.overall_score or '—'}</div>
                    <p style="color: #64748b;">Overall Score</p>
                </div>
                <div>
                    <p><strong>Modules:</strong> {report.modules_run or 'N/A'}</p>
                    <p><strong>Date:</strong> {report.created_at.strftime('%Y-%m-%d %H:%M') if report.created_at else 'N/A'}</p>
                </div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Security</h3>
                <p style="color: {get_score_color(scores.get('security', 0))}">{scores.get('security', 'N/A')}</p>
            </div>
            <div class="card">
                <h3>Performance</h3>
                <p style="color: {get_score_color(scores.get('performance', 0))}">{scores.get('performance', 'N/A')}</p>
            </div>
            <div class="card">
                <h3>Accessibility</h3>
                <p style="color: {get_score_color(scores.get('accessibility', 0))}">{scores.get('accessibility', 'N/A')}</p>
            </div>
            <div class="card">
                <h3>SEO</h3>
                <p style="color: {get_score_color(scores.get('seo', 0))}">{scores.get('seo', 'N/A')}</p>
            </div>
        </div>
        
        <div style="margin: 2rem 0;">
            <h2 style="font-size: 1.25rem; margin-bottom: 1rem;">Issues Found ({len(issues)})</h2>
            <ul class="issues">
"""
        
        for issue in issues[:20]:  # Limit to 20 issues
            if isinstance(issue, dict):
                severity = issue.get("severity", "info")
                badge_class = f"badge-{severity}" if severity in ["critical", "warning", "info"] else "badge-info"
                html += f"""
                <li>
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <strong>{issue.get('title', 'Unknown')}</strong>
                        <span class="badge {badge_class}">{severity.upper()}</span>
                    </div>
                    <p style="color: #94a3b8; font-size: 0.875rem;">{issue.get('description', '')}</p>
                </li>
"""
        
        html += """
            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by WebTesterPro</p>
            <p>""" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    @staticmethod
    def generate_share_token(report_id: int, user_id: int, expires_days: int = 30) -> str:
        """
        Tạo share token cho report.
        
        Args:
            report_id: ID của report
            user_id: ID của user tạo token
            expires_days: Số ngày token hết hạn
        
        Returns:
            Share token string
        """
        import secrets
        import hashlib
        
        db = SessionLocal()
        try:
            # Generate secure token
            token = secrets.token_urlsafe(32)
            
            # Calculate expiry
            from datetime import timedelta
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
            
            # Create share token record
            share_token = ShareToken(
                report_id=report_id,
                token=token,
                expires_at=expires_at,
                created_by=user_id,
            )
            db.add(share_token)
            db.commit()
            
            return token
        finally:
            db.close()

    @staticmethod
    def validate_share_token(token: str) -> Optional[dict]:
        """
        Validate share token và trả về report data nếu hợp lệ.
        
        Args:
            token: Share token string
        
        Returns:
            Dict với report info hoặc None nếu invalid
        """
        db = SessionLocal()
        try:
            share_token = (
                db.query(ShareToken)
                .filter(ShareToken.token == token)
                .first()
            )
            
            if not share_token:
                return None
            
            # Check expiry
            if share_token.expires_at and share_token.expires_at < datetime.utcnow():
                return None
            
            # Increment view count
            share_token.view_count += 1
            db.commit()
            
            # Get report
            report = share_token.report
            
            return {
                "report_id": report.id,
                "title": report.title,
                "url": report.url,
                "score": report.overall_score,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "view_count": share_token.view_count,
            }
        finally:
            db.close()


# Singleton instance
export_service = ExportService()
