"""
Module Authentication cho WebTesterPro.

Cung cấp đăng ký, đăng nhập, JWT và phân quyền Admin/User.
"""

from webtesterpro.auth.router import router as auth_router

__all__ = ["auth_router"]
