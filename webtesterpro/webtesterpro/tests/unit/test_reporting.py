"""
Tests for the WebTesterPro reporting module.
"""

import pytest
from datetime import datetime
from webtesterpro.modules.reporting.report_generator import (
    ReportGenerator,
    ReportData,
    ReportConfig,
)


class TestReportConfig:
    """Tests for ReportConfig dataclass."""

    def test_creation_defaults(self):
        """Should create with defaults."""
        config = ReportConfig()

        assert config.output_dir == "reports"
        assert config.template_name == "default"
        assert config.include_screenshots is False
        assert config.include_charts is True

    def test_creation_custom(self):
        """Should create with custom values."""
        config = ReportConfig(
            output_dir="/custom/path",
            include_screenshots=True,
            pdf_enabled=True,
        )

        assert config.output_dir == "/custom/path"
        assert config.include_screenshots is True
        assert config.pdf_enabled is True

    def test_to_dict(self):
        """Should convert to dictionary."""
        config = ReportConfig()

        result = config.to_dict()

        assert "output_dir" in result
        assert "template_name" in result
        assert "include_screenshots" in result


class TestReportData:
    """Tests for ReportData dataclass."""

    def test_creation_defaults(self):
        """Should create with defaults."""
        data = ReportData()

        assert data.url == ""
        assert data.test_name == ""
        assert data.crawl_results == {}
        assert data.scores == {}
        assert data.errors == []

    def test_creation_with_values(self):
        """Should create with values."""
        data = ReportData(
            url="https://example.com",
            test_name="Homepage Test",
            overall_score=85,
        )

        assert data.url == "https://example.com"
        assert data.test_name == "Homepage Test"
        assert data.overall_score == 85

    def test_to_dict(self):
        """Should convert to dictionary."""
        data = ReportData(
            url="https://example.com",
            test_name="Test",
        )

        result = data.to_dict()

        assert result["url"] == "https://example.com"
        assert result["test_name"] == "Test"
        assert "timestamp" in result


class TestReportGenerator:
    """Tests for ReportGenerator class."""

    def test_initialization(self):
        """Should initialize generator."""
        generator = ReportGenerator(output_dir="/tmp/test_reports")

        assert generator.output_dir.name == "test_reports"
        assert generator.history_file.name == "history.json"

    def test_get_score_color(self):
        """Should return correct color for score."""
        generator = ReportGenerator()

        assert generator._get_score_color(95) == "success"
        assert generator._get_score_color(75) == "info"
        assert generator._get_score_color(55) == "warning"
        assert generator._get_score_color(35) == "danger"

    def test_get_risk_color(self):
        """Should return correct color for risk."""
        generator = ReportGenerator()

        assert generator._get_risk_color("SECURE") == "success"
        assert generator._get_risk_color("LOW") == "info"
        assert generator._get_risk_color("MEDIUM") == "warning"
        assert generator._get_risk_color("HIGH") == "danger"

    def test_calculate_overall_score_no_data(self):
        """Should return 0 when no data."""
        generator = ReportGenerator()
        data = ReportData(url="https://example.com")

        score = generator._calculate_overall_score(data)

        assert score == 0

    def test_calculate_overall_score_seo(self):
        """Should calculate score from SEO data."""
        generator = ReportGenerator()
        data = ReportData(url="https://example.com")
        data.seo_results = {"scores": {"overall": 80}}

        score = generator._calculate_overall_score(data)

        assert score == 80

    def test_calculate_overall_score_multiple(self):
        """Should calculate average from multiple sources."""
        generator = ReportGenerator()
        data = ReportData(url="https://example.com")
        data.seo_results = {"scores": {"overall": 80}}
        data.performance_results = {"scores": {"overall": 90}}

        score = generator._calculate_overall_score(data)

        assert score == 85  # (80 + 90) / 2

    def test_extract_scores_seo(self):
        """Should extract SEO scores."""
        generator = ReportGenerator()
        data = ReportData()
        data.seo_results = {"scores": {"overall": 75, "title": 80}}

        scores = generator._extract_scores(data)

        assert "SEO" in scores
        assert scores["SEO"] == 75

    def test_extract_scores_security(self):
        """Should calculate security score from issues."""
        generator = ReportGenerator()
        data = ReportData()
        data.security_results = {
            "summary": {
                "critical": 0,
                "high": 1,
                "medium": 2,
            }
        }

        scores = generator._extract_scores(data)

        assert "Security" in scores
        # 100 - (1*20) - (2*10) = 60
        assert scores["Security"] == 60

    def test_get_history_empty(self):
        """Should return empty list when no history."""
        generator = ReportGenerator(output_dir="/tmp/nonexistent_dir")

        history = generator.get_history()

        assert history == []

    def test_list_reports_empty(self):
        """Should return empty list when no reports."""
        generator = ReportGenerator(output_dir="/tmp/nonexistent_dir")

        reports = generator.list_reports()

        assert reports == []

    def test_get_dashboard_data_empty(self):
        """Should return empty data when no history."""
        generator = ReportGenerator(output_dir="/tmp/nonexistent_dir")

        data = generator.get_dashboard_data()

        assert data["total_tests"] == 0
        assert data["average_score"] == 0
        assert data["trend"] == []

    def test_get_dashboard_data_with_history(self, tmp_path):
        """Should return data with history."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        
        # Create fake history
        history_file = tmp_path / "history.json"
        history_file.write_text("""[
            {"url": "https://example.com", "overall_score": 80, "scores": {"SEO": 80}, "timestamp": "2024-01-01"},
            {"url": "https://test.com", "overall_score": 90, "scores": {"SEO": 90}, "timestamp": "2024-01-02"}
        ]""")

        data = generator.get_dashboard_data()

        assert data["total_tests"] == 2
        assert data["average_score"] == 85.0
        assert len(data["history"]) == 2

    def test_generate_json(self, tmp_path):
        """Should generate JSON report."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        data = ReportData(
            url="https://example.com",
            test_name="Test",
            seo_results={"scores": {"overall": 80}},
        )

        filepath = generator.generate_json(data)

        assert filepath.endswith(".json")
        assert (tmp_path / filepath.split("/")[-1]).exists()

    def test_generate_html(self, tmp_path):
        """Should generate HTML report."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        data = ReportData(
            url="https://example.com",
            test_name="Test",
        )

        filepath = generator.generate_html(data)

        assert filepath.endswith(".html")
        filename = filepath.split("/")[-1]
        assert tmp_path.joinpath(filename).exists()

    def test_generate_multiple_formats(self, tmp_path):
        """Should generate multiple formats."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        data = ReportData(
            url="https://example.com",
            test_name="Test",
        )

        results = generator.generate(data, formats=["html", "json"])

        assert "html" in results
        assert "json" in results
