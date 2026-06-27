"""
Accessibility Testing Module

Accessibility scanning for websites:
- WCAG 2.1/2.2 compliance
- axe-core integration
- Alt text, contrast, ARIA
- Keyboard navigation
- Violation severity levels
"""

from webtesterpro.modules.accessibility.accessibility_checker import (
    AccessibilityChecker,
    A11yIssue,
    A11yReport,
    ViolationLevel,
)

__all__ = [
    "AccessibilityChecker",
    "A11yIssue",
    "A11yReport",
    "ViolationLevel",
]
