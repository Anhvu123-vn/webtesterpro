"""
Parser kết quả test — trích xuất issues, recommendations cho UI.

Tách logic khỏi template Jinja2 để dễ test và mở rộng.
"""

from typing import Any


def score_color(score: int | None) -> str:
    """Tailwind text color class theo điểm."""
    if score is None:
        return "text-slate-400"
    if score >= 80:
        return "text-emerald-400"
    if score >= 50:
        return "text-amber-400"
    return "text-red-400"


def score_ring_color(score: int | None) -> str:
    """Màu SVG ring theo điểm."""
    if score is None:
        return "#64748b"
    if score >= 80:
        return "#34d399"
    if score >= 50:
        return "#fbbf24"
    return "#f87171"


def severity_badge(severity: str) -> str:
    """Tailwind classes cho badge severity."""
    mapping = {
        "critical": "bg-red-500/15 text-red-400 border-red-500/30",
        "high": "bg-orange-500/15 text-orange-400 border-orange-500/30",
        "serious": "bg-orange-500/15 text-orange-400 border-orange-500/30",
        "medium": "bg-amber-500/15 text-amber-400 border-amber-500/30",
        "moderate": "bg-amber-500/15 text-amber-400 border-amber-500/30",
        "low": "bg-blue-500/15 text-blue-400 border-blue-500/30",
        "minor": "bg-slate-500/15 text-slate-400 border-slate-500/30",
        "info": "bg-slate-500/15 text-slate-400 border-slate-500/30",
    }
    return mapping.get(severity.lower(), "bg-slate-500/15 text-slate-400 border-slate-500/30")


def parse_issues(results: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Gom tất cả issues từ các module thành một danh sách thống nhất."""
    if not results:
        return []

    issues: list[dict[str, Any]] = []

    # Security issues
    sec = results.get("security_results") or {}
    for item in sec.get("issues") or []:
        if isinstance(item, dict):
            issues.append({
                "module": "Security",
                "severity": (item.get("risk_level") or item.get("severity") or "medium").lower(),
                "title": item.get("title") or item.get("type") or "Security Issue",
                "description": item.get("description") or item.get("detail") or "",
            })
        elif isinstance(item, str):
            issues.append({"module": "Security", "severity": "medium", "title": item, "description": ""})

    # SEO issues
    seo = results.get("seo_results") or {}
    for item in seo.get("issues") or []:
        text = item if isinstance(item, str) else str(item)
        issues.append({"module": "SEO", "severity": "medium", "title": text, "description": ""})

    # Accessibility issues
    a11y = results.get("accessibility_results") or {}
    for item in a11y.get("issues") or []:
        if isinstance(item, dict):
            issues.append({
                "module": "Accessibility",
                "severity": (item.get("impact") or "moderate").lower(),
                "title": item.get("description") or item.get("id") or "A11y violation",
                "description": item.get("help") or "",
            })

    # Performance issues
    perf = results.get("performance_results") or {}
    for item in perf.get("issues") or []:
        text = item if isinstance(item, str) else str(item)
        issues.append({"module": "Performance", "severity": "medium", "title": text, "description": ""})

    # Engine errors
    for err in results.get("errors") or []:
        issues.append({"module": "System", "severity": "high", "title": str(err), "description": ""})

    # Sắp xếp theo severity
    order = {"critical": 0, "high": 1, "serious": 1, "medium": 2, "moderate": 2, "low": 3, "minor": 4, "info": 5}
    issues.sort(key=lambda x: order.get(x["severity"], 9))
    return issues


def build_recommendations(results: dict[str, Any] | None) -> list[str]:
    """Sinh danh sách khuyến nghị dựa trên kết quả test."""
    if not results:
        return []

    recs: list[str] = []
    score = results.get("overall_score") or 0

    if score < 50:
        recs.append("Website cần cải thiện khẩn cấp — ưu tiên fix các lỗi Critical và High trước.")
    elif score < 80:
        recs.append("Website ở mức trung bình — tập trung tối ưu Performance và Security headers.")

    sec = results.get("security_results", {}).get("summary", {})
    if sec.get("critical", 0) > 0:
        recs.append(f"Phát hiện {sec['critical']} lỗi bảo mật Critical — patch ngay lập tức.")
    if sec.get("high", 0) > 0:
        recs.append("Rà soát và vá các lỗ hổng High severity trong Security Scan.")

    a11y = results.get("accessibility_results", {}).get("summary", {})
    if a11y.get("total_violations", 0) > 0:
        recs.append("Thêm alt text cho images và cải thiện contrast ratio để đạt WCAG 2.1 AA.")

    seo = results.get("seo_results") or {}
    if seo.get("issues"):
        recs.append("Bổ sung meta description, canonical URL và structured data cho SEO.")

    perf = results.get("performance_results", {}).get("scores", {})
    if perf.get("overall", 100) < 70:
        recs.append("Tối ưu bundle JS/CSS, enable compression và lazy-load images.")

    if not recs:
        recs.append("Website đạt điểm tốt — duy trì monitoring định kỳ với Full Test.")

    return recs
