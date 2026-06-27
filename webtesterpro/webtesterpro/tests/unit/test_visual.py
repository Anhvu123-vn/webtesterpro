"""
Tests for the WebTesterPro visual module.
"""

import pytest
from webtesterpro.modules.visual.visual_tester import (
    VisualTester,
    Viewport,
    ScreenshotResult,
    VisualDiff,
)


class TestViewport:
    """Tests for Viewport dataclass."""

    def test_creation(self):
        """Should create Viewport with values."""
        viewport = Viewport(name="test", width=1920, height=1080)

        assert viewport.name == "test"
        assert viewport.width == 1920
        assert viewport.height == 1080
        assert viewport.device_scale_factor == 1.0
        assert viewport.is_mobile is False
        assert viewport.has_touch is False

    def test_desktop(self):
        """Should create desktop viewport."""
        viewport = Viewport.desktop()

        assert viewport.name == "desktop"
        assert viewport.width == 1920
        assert viewport.height == 1080

    def test_mobile_portrait(self):
        """Should create mobile portrait viewport."""
        viewport = Viewport.mobile_portrait()

        assert viewport.name == "mobile-portrait"
        assert viewport.width == 375
        assert viewport.height == 667
        assert viewport.is_mobile is True
        assert viewport.has_touch is True

    def test_laptop(self):
        """Should create laptop viewport."""
        viewport = Viewport.laptop()

        assert viewport.name == "laptop"
        assert viewport.width == 1366
        assert viewport.height == 768

    def test_tablet_landscape(self):
        """Should create tablet landscape viewport."""
        viewport = Viewport.tablet_landscape()

        assert viewport.name == "tablet-landscape"
        assert viewport.width == 1024
        assert viewport.height == 768
        assert viewport.is_mobile is False

    def test_tablet_portrait(self):
        """Should create tablet portrait viewport."""
        viewport = Viewport.tablet_portrait()

        assert viewport.name == "tablet-portrait"
        assert viewport.width == 768
        assert viewport.height == 1024
        assert viewport.is_mobile is True

    def test_responsive_all(self):
        """Should return all responsive viewports."""
        viewports = Viewport.responsive_all()

        assert len(viewports) == 6
        assert any(v.name == "desktop" for v in viewports)
        assert any(v.name == "mobile-portrait" for v in viewports)
        assert any(v.name == "mobile-landscape" for v in viewports)

    def test_to_dict(self):
        """Should convert to dictionary."""
        viewport = Viewport.desktop()

        result = viewport.to_dict()

        assert result["name"] == "desktop"
        assert result["width"] == 1920
        assert result["height"] == 1080


class TestScreenshotResult:
    """Tests for ScreenshotResult dataclass."""

    def test_creation(self):
        """Should create ScreenshotResult."""
        viewport = Viewport.desktop()
        result = ScreenshotResult(url="https://example.com", viewport=viewport)

        assert result.url == "https://example.com"
        assert result.viewport == viewport
        assert result.success is True
        assert result.base64_image == ""

    def test_creation_with_values(self):
        """Should create with all values."""
        viewport = Viewport.mobile_portrait()
        result = ScreenshotResult(
            url="https://example.com",
            viewport=viewport,
            base64_image="abc123",
            width=375,
            height=667,
            file_size=50000,
        )

        assert result.base64_image == "abc123"
        assert result.width == 375
        assert result.height == 667
        assert result.file_size == 50000

    def test_to_dict(self):
        """Should convert to dictionary."""
        viewport = Viewport.desktop()
        result = ScreenshotResult(url="https://example.com", viewport=viewport)

        dict_result = result.to_dict()

        assert dict_result["url"] == "https://example.com"
        assert dict_result["viewport"]["name"] == "desktop"
        assert dict_result["success"] is True


class TestVisualDiff:
    """Tests for VisualDiff dataclass."""

    def test_creation(self):
        """Should create VisualDiff."""
        diff = VisualDiff(
            baseline_path="/path/baseline.png",
            current_path="/path/current.png",
        )

        assert diff.baseline_path == "/path/baseline.png"
        assert diff.current_path == "/path/current.png"
        assert diff.is_identical is True
        assert diff.threshold_passed is True

    def test_creation_with_differences(self):
        """Should create with differences."""
        diff = VisualDiff(
            baseline_path="/path/baseline.png",
            current_path="/path/current.png",
            pixel_difference=1000,
            percentage_difference=0.5,
            is_identical=False,
            threshold_passed=True,
        )

        assert diff.pixel_difference == 1000
        assert diff.percentage_difference == 0.5
        assert diff.is_identical is False
        assert diff.threshold_passed is True

    def test_to_dict(self):
        """Should convert to dictionary."""
        diff = VisualDiff(
            baseline_path="/path/baseline.png",
            current_path="/path/current.png",
            pixel_difference=500,
            percentage_difference=0.25,
        )

        result = diff.to_dict()

        assert result["baseline_path"] == "/path/baseline.png"
        assert result["pixel_difference"] == 500
        assert result["percentage_difference"] == 0.25
        assert result["is_identical"] is True


class TestVisualTester:
    """Tests for VisualTester class."""

    def test_initialization(self):
        """Should initialize tester."""
        tester = VisualTester(baseline_dir="/tmp/test_baselines")

        assert tester._context is None
        assert tester.baseline_dir.name == "test_baselines"
        assert tester.threshold == 0.1

    def test_initialization_default(self):
        """Should initialize with defaults."""
        tester = VisualTester()

        assert tester.threshold == 0.1
        assert tester.baseline_dir.name == "baselines"

    def test_generate_baseline_path(self):
        """Should generate correct baseline path."""
        tester = VisualTester(baseline_dir="/tmp/test_baselines")
        viewport = Viewport.desktop()
        url = "https://example.com"

        path = tester._generate_baseline_path(url, viewport)

        assert path.parent.name == "test_baselines"
        assert path.name.startswith("desktop_")
        assert path.suffix == ".png"

    def test_generate_baseline_path_consistency(self):
        """Should generate same path for same URL."""
        tester = VisualTester(baseline_dir="/tmp/test_baselines")
        viewport = Viewport.mobile_portrait()
        url = "https://example.com/page"

        path1 = tester._generate_baseline_path(url, viewport)
        path2 = tester._generate_baseline_path(url, viewport)

        assert path1 == path2

    def test_get_image_hash(self):
        """Should calculate image hash."""
        tester = VisualTester()

        hash1 = tester._get_image_hash(b"test data")
        hash2 = tester._get_image_hash(b"test data")
        hash3 = tester._get_image_hash(b"different data")

        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 32  # MD5 hash length

    def test_list_baselines_empty(self):
        """Should return empty list when no baselines."""
        tester = VisualTester(baseline_dir="/tmp/nonexistent_dir")

        baselines = tester.list_baselines()

        assert baselines == []

    def test_threshold_default(self):
        """Should have correct default threshold."""
        tester = VisualTester()

        assert tester.DEFAULT_THRESHOLD == 0.1
        assert tester.threshold == 0.1

    def test_set_threshold(self):
        """Should update threshold."""
        tester = VisualTester()
        tester.threshold = 0.05

        assert tester.threshold == 0.05

    def test_viewport_creation(self):
        """Should create custom viewport."""
        viewport = Viewport(
            name="custom",
            width=1440,
            height=900,
            device_scale_factor=2.0,
            is_mobile=True,
            has_touch=True,
        )

        assert viewport.name == "custom"
        assert viewport.width == 1440
        assert viewport.height == 900
        assert viewport.device_scale_factor == 2.0
        assert viewport.is_mobile is True
        assert viewport.has_touch is True
