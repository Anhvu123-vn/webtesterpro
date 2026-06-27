"""
Reporting Module

Report generation for WebTesterPro:
- HTML reports with Bootstrap
- PDF export
- JSON export
- Dashboard with charts
- Test history
"""

from webtesterpro.modules.reporting.report_generator import (
    ReportGenerator,
    ReportData,
    ReportConfig,
)

__all__ = [
    "ReportGenerator",
    "ReportData",
    "ReportConfig",
]
