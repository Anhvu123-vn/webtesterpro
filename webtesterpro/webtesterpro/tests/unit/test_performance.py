"""
Tests for the WebTesterPro performance module.
"""

import pytest
from webtesterpro.modules.performance.performance_tester import (
    PerformanceTester,
    CoreWebVitals,
    ResourceMetrics,
    PerformanceResult,
)


class TestCoreWebVitals:
    """Tests for CoreWebVitals dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        vitals = CoreWebVitals()

        assert vitals.ttfb == 0.0
        assert vitals.fcp == 0.0
        assert vitals.lcp == 0.0
        assert vitals.fid == 0.0
        assert vitals.inp == 0.0
        assert vitals.cls == 0.0
        assert vitals.tbt == 0.0

    def test_with_values(self):
        """Should accept custom values."""
        vitals = CoreWebVitals(
            ttfb=500.0,
            fcp=1200.0,
            lcp=2000.0,
            fid=50.0,
            cls=0.05,
        )

        assert vitals.ttfb == 500.0
        assert vitals.fcp == 1200.0
        assert vitals.lcp == 2000.0
        assert vitals.fid == 50.0
        assert vitals.cls == 0.05

    def test_to_dict(self):
        """Should convert to dictionary."""
        vitals = CoreWebVitals(
            ttfb=500.0,
            fcp=1200.0,
            lcp=2000.0,
        )

        result = vitals.to_dict()

        assert "ttfb_ms" in result
        assert "fcp_ms" in result
        assert "lcp_ms" in result
        assert result["ttfb_ms"] == 500.0
        assert result["lcp_ms"] == 2000.0

    def test_get_score_good(self):
        """Should return 'good' for good metrics."""
        vitals = CoreWebVitals(ttfb=500.0, lcp=2000.0, cls=0.05)
        thresholds = {"ttfb": 800, "lcp": 2500, "cls": 0.1}

        scores = vitals.get_score(thresholds)

        assert scores["ttfb"] == "good"
        assert scores["lcp"] == "good"
        assert scores["cls"] == "good"

    def test_get_score_needs_improvement(self):
        """Should return 'needs_improvement' for moderate metrics."""
        vitals = CoreWebVitals(ttfb=1000.0, lcp=3000.0, cls=0.15)
        thresholds = {"ttfb": 800, "lcp": 2500, "cls": 0.1}

        scores = vitals.get_score(thresholds)

        assert scores["ttfb"] == "needs_improvement"
        assert scores["lcp"] == "needs_improvement"
        assert scores["cls"] == "needs_improvement"

    def test_get_score_poor(self):
        """Should return 'poor' for poor metrics."""
        vitals = CoreWebVitals(ttfb=2000.0, lcp=5000.0, cls=0.3)
        thresholds = {"ttfb": 800, "lcp": 2500, "cls": 0.1}

        scores = vitals.get_score(thresholds)

        assert scores["ttfb"] == "poor"
        assert scores["lcp"] == "poor"
        assert scores["cls"] == "poor"


class TestResourceMetrics:
    """Tests for ResourceMetrics dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        metrics = ResourceMetrics()

        assert metrics.total_requests == 0
        assert metrics.total_size == 0
        assert metrics.scripts_count == 0
        assert metrics.images_count == 0
        assert metrics.failed_requests == 0

    def test_with_values(self):
        """Should accept custom values."""
        metrics = ResourceMetrics(
            total_requests=50,
            total_size=1024 * 1024,
            scripts_count=10,
            images_count=20,
        )

        assert metrics.total_requests == 50
        assert metrics.total_size == 1048576
        assert metrics.scripts_count == 10
        assert metrics.images_count == 20

    def test_to_dict(self):
        """Should convert to dictionary."""
        metrics = ResourceMetrics(
            total_requests=10,
            total_size=1024000,
            scripts_count=3,
        )

        result = metrics.to_dict()

        assert "summary" in result
        assert result["summary"]["total_requests"] == 10
        assert result["summary"]["total_size_kb"] == 1000.0
        assert result["by_type"]["scripts"]["count"] == 3


class TestPerformanceResult:
    """Tests for PerformanceResult dataclass."""

    def test_default_creation(self):
        """Should create with URL and defaults."""
        result = PerformanceResult(url="https://example.com")

        assert result.url == "https://example.com"
        assert isinstance(result.web_vitals, CoreWebVitals)
        assert isinstance(result.resources, ResourceMetrics)
        assert result.overall_score == 0.0
        assert result.errors == []
        assert result.warnings == []

    def test_with_metrics(self):
        """Should create with metrics."""
        vitals = CoreWebVitals(lcp=1500.0, cls=0.05)
        resources = ResourceMetrics(total_requests=30)

        result = PerformanceResult(
            url="https://example.com",
            web_vitals=vitals,
            resources=resources,
            overall_score=85.0,
        )

        assert result.web_vitals.lcp == 1500.0
        assert result.resources.total_requests == 30
        assert result.overall_score == 85.0

    def test_to_dict(self):
        """Should convert to dictionary."""
        result = PerformanceResult(
            url="https://example.com",
            overall_score=90.0,
        )

        dict_result = result.to_dict()

        assert dict_result["url"] == "https://example.com"
        assert dict_result["scores"]["overall"] == 90.0
        assert "web_vitals" in dict_result
        assert "resources" in dict_result


class TestPerformanceTester:
    """Tests for PerformanceTester class."""

    def test_initialization(self):
        """Should initialize with defaults."""
        tester = PerformanceTester()

        assert tester._context is None
        assert isinstance(tester._thresholds, dict)
        assert tester._capture_traces is False

    def test_default_thresholds(self):
        """Should have correct default thresholds."""
        tester = PerformanceTester()

        assert tester.DEFAULT_THRESHOLDS["ttfb"] == 800
        assert tester.DEFAULT_THRESHOLDS["fcp"] == 1800
        assert tester.DEFAULT_THRESHOLDS["lcp"] == 2500
        assert tester.DEFAULT_THRESHOLDS["cls"] == 0.1

    def test_set_thresholds(self):
        """Should update thresholds."""
        tester = PerformanceTester()
        new_thresholds = {"lcp": 2000, "cls": 0.05}

        tester.set_thresholds(new_thresholds)

        assert tester._thresholds["lcp"] == 2000
        assert tester._thresholds["cls"] == 0.05
        # Original thresholds should be preserved
        assert tester._thresholds["ttfb"] == 800

    def test_enable_tracing(self):
        """Should enable tracing."""
        tester = PerformanceTester()

        tester.enable_tracing("/path/to/trace.json")

        assert tester._capture_traces is True
        assert tester._trace_path == "/path/to/trace.json"

    def test_calculate_overall_score_good(self):
        """Should calculate good score for good metrics."""
        tester = PerformanceTester()
        vitals = CoreWebVitals(
            lcp=1500.0,
            cls=0.05,
            fid=50.0,
            ttfb=400.0,
            tbt=50.0,
        )

        score = tester._calculate_overall_score(vitals)

        assert score == 100

    def test_calculate_overall_score_with_penalties(self):
        """Should apply penalties for poor metrics."""
        tester = PerformanceTester()
        vitals = CoreWebVitals(
            lcp=5000.0,   # -25 penalty
            cls=0.3,      # -25 penalty
            fid=400.0,    # -25 penalty
            ttfb=2000.0,  # -15 penalty
            tbt=700.0,    # -10 penalty
        )

        score = tester._calculate_overall_score(vitals)

        assert score == 0

    def test_add_warnings(self):
        """Should add warnings for poor metrics."""
        tester = PerformanceTester()
        result = PerformanceResult(url="https://example.com")
        vitals = CoreWebVitals(lcp=5000.0, cls=0.3, ttfb=2000.0)

        tester._add_warnings(result, vitals)

        assert len(result.warnings) > 0
        assert any("LCP" in w for w in result.warnings)
        assert any("CLS" in w for w in result.warnings)
