"""
Service chạy kiểm thử website qua WebTesterEngine.

Tích hợp với Report model — lưu kết quả JSON và cập nhật trạng thái.
Hỗ trợ SSE real-time events qua sse_manager.
"""

import asyncio
import json
import logging
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from webtesterpro.core.config import Config
from webtesterpro.core.engine import WebTesterEngine
from webtesterpro.database import SessionLocal
from webtesterpro.modules.reporting.report_generator import ReportData, ReportGenerator

logger = logging.getLogger(__name__)

# Thư mục lưu report JSON/HTML của dashboard
REPORTS_DIR = Path(__file__).resolve().parents[2] / "reports" / "dashboard"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _serialize_datetime(obj: Any) -> Any:
    """Convert datetime objects to ISO format strings for JSON serialization."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _serialize_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_datetime(item) for item in obj]
    return obj


def _run_test_in_thread(report_id: int, url: str, modules: list[str], options: dict[str, Any] | None) -> None:
    """
    Chạy test trong thread riêng biệt để tránh conflict với event loop của uvicorn.
    Đây là cách an toàn nhất cho Python 3.13 + Windows + Playwright.
    """
    # Import và setup asyncio policy cho Windows
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Chạy async code trong thread riêng
    asyncio.run(_run_test_async(report_id, url, modules, options))


async def run_website_test(
    report_id: int,
    url: str,
    modules: list[str],
    options: dict[str, Any] | None = None,
) -> None:
    """
    Chạy test trong background task bằng threading.
    Cách này tránh hoàn toàn event loop conflict với uvicorn.
    """
    loop = asyncio.get_event_loop()
    
    # Chạy trong thread riêng với asyncio.run()
    await asyncio.to_thread(_run_test_in_thread, report_id, url, modules, options)


async def _run_test_async(
    report_id: int,
    url: str,
    modules: list[str],
    options: dict[str, Any] | None = None,
) -> None:
    """
    Chạy test async thực tế trong thread riêng.
    """
    options = options or {}
    max_depth = int(options.get("max_depth", 2))
    max_pages = int(options.get("max_pages", 20))
    viewport = options.get("viewport", "desktop")
    monitor_duration = int(options.get("monitor_duration", 30))

    config = Config.load_default()
    report_data = ReportData(
        url=url,
        test_name=f"Dashboard Test — {url}",
        timestamp=datetime.now(),
        modules_run=modules,
    )
    start = time.time()
    errors: list[str] = []

    try:
        # Import SSE manager here to avoid circular imports
        from webtesterpro.dashboard.services.sse_manager import queue_emit, start_emit_worker
        
        # Start emit worker nếu chưa chạy
        start_emit_worker()
        
        # Initialize progress
        _update_report_db(report_id, status="running", progress=0, current_module="Khởi tạo...")
        queue_emit(report_id, "progress", {
            "progress": 0,
            "current_module": "Khởi tạo...",
            "status": "running",
        })

        async with WebTesterEngine(config) as engine:
            total_modules = len(modules)
            for idx, module_id in enumerate(modules):
                try:
                    # Update progress: 10% base + (index / total) * 80%
                    progress = int(10 + (idx / total_modules) * 80)
                    module_name = _module_display_name(module_id)
                    _update_report_db(report_id, progress=progress, current_module=module_name)
                    queue_emit(report_id, "progress", {
                        "progress": progress,
                        "current_module": module_name,
                        "status": "running",
                    })
                    
                    if module_id == "crawler":
                        report_data.crawl_results = await engine.crawl_site(
                            url, max_depth=max_depth, max_pages=max_pages
                        )
                    elif module_id == "scanner":
                        report_data.scan_results = await engine.scan_site(url)
                    elif module_id == "analyzer":
                        analyze = await engine.analyze_site(url)
                        report_data.scan_results = {
                            **(report_data.scan_results or {}),
                            "analyzer": analyze,
                        }
                    elif module_id == "performance":
                        report_data.performance_results = await engine.test_performance(url)
                    elif module_id == "security":
                        report_data.security_results = await engine.scan_security(url)
                    elif module_id == "accessibility":
                        report_data.accessibility_results = await engine.check_accessibility(url)
                    elif module_id == "seo":
                        report_data.seo_results = await engine.analyze_seo(url)
                    elif module_id == "visual":
                        report_data.visual_results = await engine.capture_screenshot(
                            url, viewport_name=viewport
                        )
                    elif module_id == "monitor":
                        report_data.scan_results = {
                            **(report_data.scan_results or {}),
                            "monitor": await engine.monitor_site(url, duration=monitor_duration),
                        }
                except Exception as exc:
                    msg = f"Lỗi module {module_id}: {exc}"
                    logger.exception(msg)
                    errors.append(msg)
            
            # Final progress: 90% -> 100%
            _update_report_db(report_id, progress=95, current_module="Hoàn tất...")
            queue_emit(report_id, "progress", {
                "progress": 95,
                "current_module": "Hoàn tất...",
                "status": "running",
            })

        report_data.test_duration = time.time() - start
        report_data.errors = errors

        generator = ReportGenerator(config)
        report_data.overall_score = generator._calculate_overall_score(report_data)
        report_data.scores = generator._extract_scores(report_data)

        # Serialize report data, converting datetime objects to strings
        report_dict = _serialize_datetime(report_data.to_dict())

        # Lưu JSON ra disk
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_url = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50]
        json_filename = f"report_{safe_url}_{timestamp}.json"
        json_path = REPORTS_DIR / json_filename

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        summary = _build_summary(report_data)
        _update_report_db(
            report_id,
            status="completed",
            progress=100,
            current_module="Hoàn tất!",
            overall_score=report_data.overall_score,
            summary=summary,
            json_path=str(json_path),
            modules_run=json.dumps(modules),
            results_json=json.dumps(report_dict, ensure_ascii=False),
        )
        
        # Emit completion event
        queue_emit(report_id, "complete", {
            "score": report_data.overall_score,
            "url": url,
            "message": "Test hoàn thành!",
            "report_id": report_id,
        })

    except Exception as exc:
        logger.exception("Test run failed for report %s", report_id)
        _update_report_db(
            report_id,
            status="failed",
            progress=-1,
            current_module="Lỗi!",
            summary=f"Test thất bại: {exc}",
            modules_run=json.dumps(modules),
        )
        # Emit error event
        from webtesterpro.dashboard.services.sse_manager import start_emit_worker, queue_emit
        start_emit_worker()
        queue_emit(report_id, "error", {
            "error": str(exc),
            "message": "Test thất bại",
        })


def _module_display_name(module_id: str) -> str:
    """Map module ID to display name."""
    names = {
        "crawler": "Crawler - Đang quét trang...",
        "scanner": "Scanner - Đang quét...",
        "analyzer": "Analyzer - Đang phân tích...",
        "performance": "Performance - Đang test...",
        "security": "Security - Đang quét bảo mật...",
        "accessibility": "Accessibility - Đang kiểm tra...",
        "seo": "SEO - Đang phân tích...",
        "visual": "Visual - Đang chụp ảnh...",
        "monitor": "Monitor - Đang giám sát...",
    }
    return names.get(module_id, f"Module: {module_id}")


def _build_summary(data: ReportData) -> str:
    """Tạo summary ngắn gọn cho DB."""
    parts = [f"Score: {data.overall_score}/100"]
    if data.scores:
        parts.append(" | ".join(f"{k}: {v}" for k, v in data.scores.items()))
    if data.errors:
        parts.append(f"Lỗi: {len(data.errors)}")
    return " — ".join(parts)


def _update_report_db(report_id: int, **fields: Any) -> None:
    """Cập nhật report trong DB (session riêng cho background task)."""
    from webtesterpro.auth.models import Report

    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            for key, value in fields.items():
                setattr(report, key, value)
            db.commit()
    finally:
        db.close()


def load_report_results(report) -> dict | None:
    """Đọc kết quả test từ DB hoặc file JSON."""
    if report.results_json:
        try:
            return json.loads(report.results_json)
        except json.JSONDecodeError:
            pass

    if report.json_path and Path(report.json_path).exists():
        with open(report.json_path, encoding="utf-8") as f:
            return json.load(f)

    return None
