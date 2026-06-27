"""
Performance Testing Module

Measures website performance metrics including Core Web Vitals,
resource loading, and custom performance metrics.
"""

from webtesterpro.modules.performance.performance_tester import (
    PerformanceTester,
    CoreWebVitals,
    ResourceMetrics,
    PerformanceResult,
)

__all__ = [
    "PerformanceTester",
    "CoreWebVitals",
    "ResourceMetrics",
    "PerformanceResult",
]
