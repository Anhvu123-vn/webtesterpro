"""
Tests for the WebTesterPro crawler module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from webtesterpro.modules.crawler.crawler import (
    WebsiteCrawler,
    RobotsTxtParser,
    URLFilter,
    CrawlResult,
)


class TestURLFilter:
    """Tests for URLFilter class."""

    def test_blacklist_blocks_matching_urls(self):
        """URLs matching blacklist patterns should be blocked."""
        url_filter = URLFilter(
            blacklist=[r".*\.pdf$", r".*\.zip$", r".*/admin/.*"]
        )

        assert url_filter.is_allowed("https://example.com/page") is True
        assert url_filter.is_allowed("https://example.com/file.pdf") is False
        assert url_filter.is_allowed("https://example.com/archive.zip") is False
        assert url_filter.is_allowed("https://example.com/admin/dashboard") is False

    def test_allowed_domains_filter(self):
        """URLs should be filtered by allowed domains."""
        url_filter = URLFilter(
            allowed_domains=["example.com", "sub.example.com"]
        )

        assert url_filter.is_allowed("https://example.com/page") is True
        assert url_filter.is_allowed("https://sub.example.com/page") is True
        assert url_filter.is_allowed("https://other.com/page") is False

    def test_empty_blacklist_allows_all(self):
        """Empty blacklist should allow all URLs."""
        url_filter = URLFilter(blacklist=[])

        assert url_filter.is_allowed("https://example.com/anything") is True


class TestRobotsTxtParser:
    """Tests for RobotsTxtParser class."""

    def test_disallow_all_when_no_robots(self):
        """Should disallow all when robots.txt is not found."""
        parser = RobotsTxtParser()
        parser._disallow_all = True

        assert parser.is_allowed("https://example.com/page") is False

    def test_parse_robots_txt(self):
        """Should parse robots.txt content correctly."""
        parser = RobotsTxtParser()
        content = """
        User-agent: *
        Disallow: /admin/
        Disallow: /private/

        User-agent: Googlebot
        Disallow: /search
        """
        parser._parse(content)

        assert "/admin/" in parser.rules.get("*", [])
        assert "/private/" in parser.rules.get("*", [])

    def test_is_allowed_for_allowed_path(self):
        """Should allow URLs that are not disallowed."""
        parser = RobotsTxtParser()
        parser._parse("User-agent: *\nDisallow: /admin/")
        parser.rules["*"] = ["/admin/"]

        assert parser.is_allowed("https://example.com/public") is True

    def test_is_not_allowed_for_disallowed_path(self):
        """Should not allow URLs that are disallowed."""
        parser = RobotsTxtParser()
        parser.rules["*"] = ["/admin/"]
        parser._parse("User-agent: *\nDisallow: /admin/")

        assert parser.is_allowed("https://example.com/admin/") is False


class TestCrawlResult:
    """Tests for CrawlResult dataclass."""

    def test_crawl_result_creation(self):
        """Should create CrawlResult with default values."""
        result = CrawlResult(url="https://example.com", status_code=200)

        assert result.url == "https://example.com"
        assert result.status_code == 200
        assert result.title == ""
        assert result.html == ""
        assert result.links == []
        assert result.resources == []
        assert result.depth == 0
        assert result.error is None

    def test_crawl_result_with_values(self):
        """Should create CrawlResult with all values."""
        result = CrawlResult(
            url="https://example.com",
            status_code=200,
            title="Example",
            html="<html></html>",
            links=[{"url": "https://example.com/page", "text": "Page"}],
            depth=1,
        )

        assert result.title == "Example"
        assert len(result.links) == 1
        assert result.depth == 1


class TestWebsiteCrawler:
    """Tests for WebsiteCrawler class."""

    def test_initialization(self):
        """Should initialize crawler with config."""
        from webtesterpro.core.config import Config

        config = Config()
        crawler = WebsiteCrawler(config)

        assert crawler.config == config
        assert isinstance(crawler._url_filter, URLFilter)
        assert crawler._visited == set()

    def test_default_initialization(self):
        """Should initialize crawler with defaults."""
        crawler = WebsiteCrawler()

        assert crawler.config is not None
        assert isinstance(crawler._url_filter, URLFilter)

    @pytest.mark.asyncio
    async def test_set_context(self):
        """Should set browser context."""
        crawler = WebsiteCrawler()
        mock_context = AsyncMock()

        crawler.set_context(mock_context)

        assert crawler._context == mock_context
        assert crawler._semaphore is not None

    def test_result_to_dict(self):
        """Should convert CrawlResult to dictionary."""
        crawler = WebsiteCrawler()
        result = CrawlResult(
            url="https://example.com",
            status_code=200,
            title="Example",
            depth=1,
        )

        result_dict = crawler._result_to_dict(result)

        assert result_dict["url"] == "https://example.com"
        assert result_dict["status_code"] == 200
        assert result_dict["title"] == "Example"
        assert result_dict["depth"] == 1
        assert "crawled_at" in result_dict

    def test_get_graph(self):
        """Should return crawl graph."""
        crawler = WebsiteCrawler()
        crawler._graph = {
            "https://example.com": ["https://example.com/page1", "https://example.com/page2"]
        }

        graph = crawler.get_graph()

        assert len(graph) == 1
        assert len(graph["https://example.com"]) == 2

    def test_get_stats(self):
        """Should return crawl statistics."""
        crawler = WebsiteCrawler()

        stats = crawler.get_stats()

        assert stats.total_pages == 0
        assert stats.successful_pages == 0
        assert stats.failed_pages == 0
