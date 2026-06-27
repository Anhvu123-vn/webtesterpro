"""
WebTesterPro - All-in-One Website Testing Tool

A comprehensive Python framework for website testing, crawling, and analysis
using Playwright as the core engine.
"""

__version__ = "0.1.0"
__author__ = "WebTesterPro Team"

from webtesterpro.core.engine import WebTesterEngine
from webtesterpro.core.config import Config

__all__ = [
    "WebTesterEngine",
    "Config",
    "__version__",
]
