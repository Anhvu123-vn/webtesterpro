"""
Visual Testing Module

Visual testing and regression for websites:
- Screenshot capture
- Multi-device viewport
- Visual regression testing
"""

from webtesterpro.modules.visual.visual_tester import (
    VisualTester,
    Viewport,
    ScreenshotResult,
    VisualDiff,
)

__all__ = [
    "VisualTester",
    "Viewport",
    "ScreenshotResult",
    "VisualDiff",
]
