"""
Tests for the WebTesterPro config module.
"""

import pytest
import tempfile
from pathlib import Path
import yaml

from webtesterpro.core.config import (
    Config,
    CrawlerConfig,
    ScannerConfig,
    AnalyzerConfig,
    MonitorConfig,
)


class TestCrawlerConfig:
    """Tests for CrawlerConfig."""

    def test_default_values(self):
        """Should have correct default values."""
        config = CrawlerConfig()

        assert config.max_depth == 3
        assert config.max_pages == 1000
        assert config.timeout == 30000
        assert config.delay_min == 1.0
        assert config.delay_max == 3.0
        assert config.respect_robots_txt is True
        assert config.max_concurrent == 5

    def test_custom_values(self):
        """Should accept custom values."""
        config = CrawlerConfig(
            max_depth=5,
            max_pages=500,
            delay_min=2.0,
            delay_max=5.0,
        )

        assert config.max_depth == 5
        assert config.max_pages == 500
        assert config.delay_min == 2.0
        assert config.delay_max == 5.0


class TestScannerConfig:
    """Tests for ScannerConfig."""

    def test_default_values(self):
        """Should have correct default values."""
        config = ScannerConfig()

        assert config.timeout == 30000
        assert config.follow_redirects is True
        assert config.max_redirects == 5
        assert config.verify_ssl is True
        assert config.check_forms is True
        assert config.check_links is True
        assert config.check_resources is True


class TestAnalyzerConfig:
    """Tests for AnalyzerConfig."""

    def test_default_values(self):
        """Should have correct default values."""
        config = AnalyzerConfig()

        assert config.check_seo is True
        assert config.check_performance is True
        assert config.check_security_headers is True
        assert config.check_responsive is False
        assert config.lighthouse_enabled is False


class TestMonitorConfig:
    """Tests for MonitorConfig."""

    def test_default_values(self):
        """Should have correct default values."""
        config = MonitorConfig()

        assert config.interval == 60
        assert config.timeout == 10
        assert config.retry_count == 3
        assert config.alert_on_down is True


class TestConfig:
    """Tests for main Config class."""

    def test_default_config(self):
        """Should create config with default values."""
        config = Config()

        assert config.project.name == "WebTesterPro"
        assert config.crawler.max_depth == 3
        assert config.scanner.check_forms is True
        assert config.analyzer.check_seo is True
        assert config.monitor.interval == 60

    def test_from_yaml(self):
        """Should load config from YAML file."""
        yaml_content = """
crawler:
  max_depth: 5
  max_pages: 500

project:
  name: "TestProject"
  version: "1.0.0"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            config = Config.from_yaml(temp_path)

            assert config.crawler.max_depth == 5
            assert config.crawler.max_pages == 500
            assert config.project.name == "TestProject"
            assert config.project.version == "1.0.0"
        finally:
            Path(temp_path).unlink()

    def test_from_yaml_file_not_found(self):
        """Should return default config when file not found."""
        config = Config.from_yaml("/nonexistent/path/config.yaml")

        assert config.crawler.max_depth == 3

    def test_to_dict(self):
        """Should convert config to dictionary."""
        config = Config()

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "project" in config_dict
        assert "crawler" in config_dict
        assert "scanner" in config_dict
        assert config_dict["project"]["name"] == "WebTesterPro"
