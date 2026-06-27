"""
WebTesterPro Dashboard — FastAPI application.

Giao diện dark theme + tích hợp WebTesterEngine.
Chạy: uvicorn webtesterpro.dashboard.main:app --reload
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from fastapi import BackgroundTasks, Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from webtesterpro.auth import auth as auth_utils
from webtesterpro.auth import crud
from webtesterpro.auth.dependencies import get_current_active_user
from webtesterpro.auth.models import User
from webtesterpro.auth.router import router as auth_router
from webtesterpro.auth.schemas import ReportCreate, ReportResponse, UserCreate, UserLogin
from webtesterpro.core.config import Config
from webtesterpro.dashboard.constants import (
    FORM_MODULES,
    FULL_TEST_MODULES,
    MODULE_IDS,
    TEST_MODULES,
    VIEWPORT_OPTIONS,
)
from webtesterpro.dashboard.dependencies import (
    get_current_user_for_page,
    get_optional_user_for_page,
    require_admin_for_page,
)
from webtesterpro.dashboard.services.test_runner import load_report_results, run_website_test
from webtesterpro.dashboard.utils.results_parser import (
    build_recommendations,
    parse_issues,
    score_color,
    score_ring_color,
    severity_badge,
)
from webtesterpro.database import get_db, init_db

from webtesterpro.dashboard.services.sse_manager import EventEmitter, event_emitter

from webtesterpro.dashboard.services.audit_service import audit_service
from webtesterpro.dashboard.services.analytics_service import analytics_service

from webtesterpro.dashboard.services.export_service import export_service

from webtesterpro.dashboard.services.compare_service import compare_service

logger = logging.getLogger(__name__)

DASHBOARD_DIR = Path(__file__).parent
TEMPLATES_DIR = DASHBOARD_DIR / "templates"
STATIC_DIR = DASHBOARD_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
# Jinja2 filters & globals cho templates
templates.env.filters["tojson"] = lambda v, indent=2: json.dumps(
    v, indent=indent, ensure_ascii=False, default=str
)
templates.env.globals["score_color"] = score_color
templates.env.globals["score_ring_color"] = score_ring_color
templates.env.globals["severity_badge"] = severity_badge

config = Config.load_default()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("WebTesterPro Dashboard started.")
    yield


app = FastAPI(
    title="WebTesterPro Dashboard",
    description="Dashboard kiểm thử website với Authentication",
    version=config.project.version,
    lifespan=lifespan,
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
        location = exc.headers.get("Location", "/login") if exc.headers else "/login"
        return RedirectResponse(url=location, status_code=status.HTTP_302_FOUND)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def _ctx(request: Request, user: User, **extra):
    return {"request": request, "user": user, **extra}


def _validate_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError("URL không hợp lệ")
    return url


def _resolve_preselected(request: Request) -> list[str]:
    """Xác định modules được chọn sẵn từ query string."""
    preset = request.query_params.get("preset")
    module = request.query_params.get("module")
    if preset == "full" or module == "full":
        return FULL_TEST_MODULES.copy()
    if module and module in MODULE_IDS:
        return [module]
    return []


def _results_context(report, results, modules_list):
    """Context chung cho trang results."""
    issues = parse_issues(results)
    recommendations = build_recommendations(results)
    return {
        "report": report,
        "results": results,
        "modules_list": modules_list,
        "issues": issues,
        "recommendations": recommendations,
    }


# =============================================================================
# Auth Pages
# =============================================================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    next: Optional[str] = None,
    registered: Optional[int] = None,
    current_user: Optional[User] = Depends(get_optional_user_for_page),
):
    if current_user:
        return RedirectResponse(url=next or "/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request, "login.html", {"next_url": next or "/", "registered": bool(registered)}
    )


@app.post("/login")
async def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next_url: str = Form(default="/"),
    db: Session = Depends(get_db),
):
    # Validate next_url to prevent open redirect vulnerabilities
    if not next_url or not isinstance(next_url, str) or not next_url.startswith("/"):
        next_url = "/"
    
    client_ip = request.client.host if request.client else "unknown"
    if not auth_utils.login_rate_limiter.is_allowed(client_ip):
        return templates.TemplateResponse(
            request, "login.html",
            {"next_url": next_url, "error": "Quá nhiều lần thử. Thử lại sau 15 phút."},
            status_code=429,
        )
    user = auth_utils.authenticate_user(db, UserLogin(email=email, password=password))
    if not user or not user.is_active:
        auth_utils.login_rate_limiter.record_failure(client_ip)
        return templates.TemplateResponse(
            request, "login.html",
            {"next_url": next_url, "error": "Email hoặc mật khẩu không đúng."},
            status_code=401,
        )
    auth_utils.login_rate_limiter.reset(client_ip)
    crud.update_last_login(db, user)
    access_token, refresh_token = auth_utils.create_token_pair(user.id)
    response = RedirectResponse(url=next_url, status_code=302)
    auth_utils.set_auth_cookies(response, access_token, refresh_token)
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user_for_page),
):
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(request, "register.html", {})


@app.post("/register")
async def register_form(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    errors: list[str] = []
    if password != confirm_password:
        errors.append("Mật khẩu xác nhận không khớp.")
    user_in = None
    if not errors:
        try:
            user_in = UserCreate(email=email, username=username, password=password)
        except ValidationError as exc:
            errors = [e["msg"] for e in exc.errors()]
    if not errors:
        if crud.get_user_by_email(db, email.lower()):
            errors.append("Email đã được sử dụng.")
        if crud.get_user_by_username(db, username):
            errors.append("Username đã được sử dụng.")
    if errors:
        return templates.TemplateResponse(
            request, "register.html",
            {"errors": errors, "email": email, "username": username},
            status_code=400,
        )
    crud.create_user(db, user_in)
    return RedirectResponse(url="/login?registered=1", status_code=302)


@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    auth_utils.clear_auth_cookies(response)
    return response


@app.get("/auth/login-page")
async def legacy_login():
    return RedirectResponse("/login", status_code=301)


@app.get("/auth/register-page")
async def legacy_register():
    return RedirectResponse("/register", status_code=301)


@app.get("/dashboard")
async def legacy_dashboard():
    return RedirectResponse("/", status_code=301)


# =============================================================================
# Dashboard Pages
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def homepage(
    request: Request,
    current_user: User = Depends(get_current_user_for_page),
    db: Session = Depends(get_db),
):
    reports = crud.get_reports_by_user(db, current_user.id, limit=1000)
    recent = reports[:5]
    scored = [r.overall_score for r in reports if r.overall_score is not None]
    return templates.TemplateResponse(
        request, "index.html",
        _ctx(
            request, current_user,
            modules=TEST_MODULES,
            recent_reports=recent,
            stats={
                "total": len(reports),
                "completed": sum(1 for r in reports if getattr(r, "status", "completed") == "completed"),
                "avg_score": int(sum(scored) / len(scored)) if scored else 0,
            },
        ),
    )


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(
    request: Request,
    current_user: User = Depends(get_current_user_for_page),
):
    """Trang Analytics Dashboard."""
    return templates.TemplateResponse(
        request, "analytics.html",
        _ctx(request, current_user),
    )


@app.get("/compare", response_class=HTMLResponse)
async def compare_page(
    request: Request,
    current_user: User = Depends(get_current_user_for_page),
):
    """Trang so sánh 2 reports."""
    return templates.TemplateResponse(
        request, "compare.html",
        _ctx(request, current_user),
    )


@app.get("/api/compare/{report1_id}/{report2_id}")
def compare_api(
    report1_id: int,
    report2_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_for_page),
):
    """API so sánh 2 reports."""
    report1 = crud.get_report_by_id(db, report1_id)
    report2 = crud.get_report_by_id(db, report2_id)
    
    if not report1 or not report2:
        raise HTTPException(status_code=404, detail="Report không tồn tại.")
    
    if not crud.user_can_view_report(current_user, report1) or not crud.user_can_view_report(current_user, report2):
        raise HTTPException(status_code=403, detail="Không có quyền truy cập.")
    
    comparison = compare_service.compare_reports(report1, report2)
    return JSONResponse(comparison)


@app.get("/test/new", response_class=HTMLResponse)
async def new_test_page(
    request: Request,
    current_user: User = Depends(get_current_user_for_page),
):
    preselected = _resolve_preselected(request)
    return templates.TemplateResponse(
        request, "new_test.html",
        _ctx(
            request, current_user,
            modules=FORM_MODULES,
            viewports=VIEWPORT_OPTIONS,
            preselected=preselected,
            form_url=request.query_params.get("url", ""),
        ),
    )


@app.post("/test/new")
async def submit_new_test(
    request: Request,
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    modules: List[str] = Form(default=[]),
    max_depth: int = Form(default=2),
    max_pages: int = Form(default=20),
    viewport: str = Form(default="desktop"),
    monitor_duration: int = Form(default=30),
    current_user: User = Depends(get_current_user_for_page),
    db: Session = Depends(get_db),
):
    form_ctx = {
        "modules": FORM_MODULES,
        "viewports": VIEWPORT_OPTIONS,
        "preselected": modules,
        "form_url": url,
    }

    try:
        url = _validate_url(url)
    except ValueError:
        return templates.TemplateResponse(
            request, "new_test.html",
            _ctx(request, current_user, error="URL không hợp lệ. Ví dụ: https://example.com", **form_ctx),
            status_code=400,
        )

    selected = [m for m in modules if m in MODULE_IDS]
    if not selected:
        return templates.TemplateResponse(
            request, "new_test.html",
            _ctx(request, current_user, error="Vui lòng chọn ít nhất một module.", **form_ctx),
            status_code=400,
        )

    options = {
        "max_depth": max(1, min(max_depth, 5)),
        "max_pages": max(5, min(max_pages, 500)),
        "viewport": viewport,
        "monitor_duration": max(10, min(monitor_duration, 120)),
    }

    report = crud.create_report(
        db,
        ReportCreate(title=f"Test — {urlparse(url).netloc}", url=url, summary="Đang chạy..."),
        user_id=current_user.id,
    )
    crud.update_report(db, report, status="running", modules_run=json.dumps(selected))

    background_tasks.add_task(run_website_test, report.id, url, selected, options)
    return RedirectResponse(f"/results/{report.id}", status_code=302)


@app.get("/results/{report_id}", response_class=HTMLResponse)
async def results_page(
    request: Request,
    report_id: int,
    current_user: User = Depends(get_current_user_for_page),
    db: Session = Depends(get_db),
):
    report = crud.get_report_by_id(db, report_id)
    if not report or not crud.user_can_view_report(current_user, report):
        raise HTTPException(status_code=404, detail="Report không tồn tại.")

    results = load_report_results(report)
    modules_list = json.loads(report.modules_run) if report.modules_run else []
    return templates.TemplateResponse(
        request, "results.html",
        _ctx(request, current_user, **_results_context(report, results, modules_list)),
    )


@app.get("/results/{report_id}/progress")
async def results_progress(
    report_id: int,
    current_user: User = Depends(get_current_user_for_page),
    db: Session = Depends(get_db),
):
    """API trả về tiến trình test hiện tại (JSON)."""
    report = crud.get_report_by_id(db, report_id)
    if not report or not crud.user_can_view_report(current_user, report):
        raise HTTPException(status_code=404, detail="Report không tồn tại.")

    return JSONResponse({
        "status": report.status,
        "progress": report.progress,
        "current_module": report.current_module,
        "is_running": report.status == "running",
    })


@app.get("/results/{report_id}/stream")
async def results_stream(
    report_id: int,
    current_user: User = Depends(get_current_user_for_page),
    db: Session = Depends(get_db),
):
    """
    SSE endpoint cho real-time progress updates.
    Client kết nối và nhận events cho đến khi test hoàn thành.
    """
    from fastapi.responses import StreamingResponse
    
    report = crud.get_report_by_id(db, report_id)
    if not report or not crud.user_can_view_report(current_user, report):
        raise HTTPException(status_code=404, detail="Report không tồn tại.")
    
    async def event_generator():
        # Import SSE manager
        from webtesterpro.dashboard.services.sse_manager import event_emitter
        
        # Send initial state
        yield f"data: {json.dumps({'type': 'connected', 'report_id': report_id})}\n\n"
        
        # Track if test is still running
        max_wait = 600  # 10 minutes max
        check_count = 0
        
        async def send_event(message: str):
            yield f"data: {message}\n\n"
        
        # Subscribe to events
        callbacks = []
        
        async def callback(message: str):
            try:
                await send_event(message)
            except Exception:
                pass
        
        await event_emitter.subscribe(report_id, callback)
        callbacks.append(callback)
        
        try:
            # Poll DB to check if test completed (fallback if SSE events don't fire)
            from webtesterpro.database import SessionLocal
            from webtesterpro.auth.models import Report
            
            while check_count < max_wait:
                check_count += 1
                
                # Check current status
                db_check = SessionLocal()
                try:
                    report_check = db_check.query(Report).filter(Report.id == report_id).first()
                    if report_check:
                        if report_check.status != "running":
                            # Test completed or failed
                            final_data = {
                                "type": "complete" if report_check.status == "completed" else "error",
                                "report_id": report_id,
                                "data": {
                                    "status": report_check.status,
                                    "progress": report_check.progress,
                                    "score": report_check.overall_score,
                                    "url": report_check.url,
                                }
                            }
                            yield f"data: {json.dumps(final_data)}\n\n"
                            break
                finally:
                    db_check.close()
                
                await asyncio.sleep(2)  # Check every 2 seconds
                
        finally:
            # Cleanup
            await event_emitter.unsubscribe(report_id, callback)
            yield f"data: {json.dumps({'type': 'closed'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


import asyncio


@app.get("/results/{report_id}/status", response_class=HTMLResponse)
async def results_status_partial(
    request: Request,
    report_id: int,
    current_user: User = Depends(get_current_user_for_page),
    db: Session = Depends(get_db),
):
    report = crud.get_report_by_id(db, report_id)
    if not report or not crud.user_can_view_report(current_user, report):
        raise HTTPException(status_code=404, detail="Report không tồn tại.")

    results = load_report_results(report)
    modules_list = json.loads(report.modules_run) if report.modules_run else []
    return templates.TemplateResponse(
        request, "partials/results_wrapper.html",
        _ctx(request, current_user, **_results_context(report, results, modules_list)),
    )


@app.get("/results/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = "json",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Download report in JSON, CSV, or HTML format."""
    report = crud.get_report_by_id(db, report_id)
    if not report or not crud.user_can_view_report(current_user, report):
        raise HTTPException(status_code=404, detail="Report không tồn tại.")

    results = load_report_results(report)
    if not results:
        raise HTTPException(status_code=404, detail="Chưa có dữ liệu report.")

    if format == "csv":
        content = export_service.generate_csv(report, results)
        return JSONResponse(
            content={"csv": content},
            headers={"Content-Disposition": f'attachment; filename="report_{report_id}.csv"'},
        )
    elif format == "html":
        content = export_service.generate_html_report(report, results)
        return HTMLResponse(content=content)
    else:
        return JSONResponse(
            content=results,
            headers={"Content-Disposition": f'attachment; filename="report_{report_id}.json"'},
        )


@app.post("/results/{report_id}/share")
async def create_share_link(
    report_id: int,
    expires_days: int = 30,
    current_user: User = Depends(get_current_user_for_page),
    db: Session = Depends(get_db),
):
    """Tạo share link cho report."""
    report = crud.get_report_by_id(db, report_id)
    if not report or not crud.user_can_view_report(current_user, report):
        raise HTTPException(status_code=404, detail="Report không tồn tại.")

    token = export_service.generate_share_token(report_id, current_user.id, expires_days)
    share_url = f"/share/{token}"
    
    # Log audit
    audit_service.log_user_action(
        action="test_share",
        user_id=current_user.id,
        resource_type="report",
        resource_id=report_id,
        details={"expires_days": expires_days},
    )
    
    return JSONResponse({
        "share_url": share_url,
        "token": token,
        "expires_days": expires_days,
    })


@app.get("/share/{token}")
async def view_shared_report(
    request: Request,
    token: str,
):
    """Public page để xem shared report (không cần login)."""
    report_info = export_service.validate_share_token(token)
    
    if not report_info:
        raise HTTPException(status_code=404, detail="Link không hợp lệ hoặc đã hết hạn.")
    
    return templates.TemplateResponse(
        "shared_report.html",
        {
            "request": request,
            "user": None,
            "report": report_info,
            "token": token,
        }
    )


@app.get("/history", response_class=HTMLResponse)
async def history_page(
    request: Request,
    current_user: User = Depends(get_current_user_for_page),
    db: Session = Depends(get_db),
):
    reports = (
        crud.get_all_reports(db, limit=100)
        if current_user.is_admin
        else crud.get_reports_by_user(db, current_user.id, limit=100)
    )
    return templates.TemplateResponse(
        request, "history.html", _ctx(request, current_user, reports=reports)
    )


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    current_user: User = Depends(require_admin_for_page),
    db: Session = Depends(get_db),
):
    return templates.TemplateResponse(
        request, "admin_users.html",
        _ctx(request, current_user, users=crud.get_users(db)),
    )


@app.get("/api/reports", response_model=list[ReportResponse])
def list_reports_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.is_admin:
        return crud.get_all_reports(db)
    return crud.get_reports_by_user(db, current_user.id)


@app.get("/api/analytics")
def analytics_api(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_for_page),
):
    """API trả về dữ liệu analytics."""
    user_id = None if current_user.is_admin else current_user.id
    
    return JSONResponse({
        "stats": analytics_service.get_user_stats(db, current_user.id),
        "score_trend": analytics_service.get_score_trend(db, user_id, days),
        "test_frequency": analytics_service.get_test_frequency(db, user_id, days),
        "score_distribution": analytics_service.get_score_distribution(db, user_id, days),
        "module_usage": analytics_service.get_module_usage(db, user_id, days),
        "top_urls": analytics_service.get_top_urls(db, user_id),
        "performance": analytics_service.get_performance_stats(db, user_id, days),
        "recent_activity": _format_recent_activity(
            audit_service.get_user_activity(db, current_user.id, limit=10)
        ),
    })


def _format_recent_activity(logs: list) -> list:
    """Format audit logs cho frontend."""
    from datetime import datetime
    action_labels = {
        "login": "Đăng nhập",
        "logout": "Đăng xuất",
        "login_failed": "Đăng nhập thất bại",
        "register": "Đăng ký",
        "test_start": "Bắt đầu test",
        "test_complete": "Hoàn thành test",
        "test_view": "Xem kết quả",
        "test_delete": "Xóa test",
        "test_share": "Chia sẻ test",
    }
    
    result = []
    for log in logs:
        # Calculate time ago
        delta = datetime.utcnow() - log.created_at
        if delta.days > 0:
            time_ago = f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            time_ago = f"{delta.seconds // 3600}h ago"
        elif delta.seconds >= 60:
            time_ago = f"{delta.seconds // 60}m ago"
        else:
            time_ago = "just now"
        
        result.append({
            "action": log.action,
            "action_label": action_labels.get(log.action, log.action),
            "details": log.details,
            "time_ago": time_ago,
            "created_at": log.created_at.isoformat(),
        })
    return result


def run_dashboard(host: str = None, port: int = None, reload: bool = False):
    import uvicorn
    uvicorn.run(
        "webtesterpro.dashboard.main:app",
        host=host or config.dashboard.host,
        port=port or config.dashboard.port,
        reload=reload or config.dashboard.debug,
    )


if __name__ == "__main__":
    run_dashboard(reload=True)
