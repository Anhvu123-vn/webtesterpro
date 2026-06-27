"""
Tests for the WebTesterPro SEO module.
"""

import pytest
from webtesterpro.modules.seo.seo_analyzer import (
    SEOAnalyzer,
    SEOIssue,
    SEOReport,
    SEOScore,
)


class TestSEOIssue:
    """Tests for SEOIssue dataclass."""

    def test_creation(self):
        """Should create SEOIssue with required fields."""
        issue = SEOIssue(
            category="Title",
            title="Missing title",
            description="Page has no title",
            impact="high",
        )

        assert issue.category == "Title"
        assert issue.title == "Missing title"
        assert issue.impact == "high"

    def test_creation_with_element(self):
        """Should create SEOIssue with element."""
        issue = SEOIssue(
            category="Images",
            title="Missing alt",
            description="Image missing alt",
            impact="medium",
            element="<img src='test.jpg'>",
            recommendation="Add alt text",
        )

        assert issue.element == "<img src='test.jpg'>"
        assert issue.recommendation == "Add alt text"

    def test_to_dict(self):
        """Should convert to dictionary."""
        issue = SEOIssue(
            category="Test",
            title="Test",
            description="Test desc",
            impact="low",
        )

        result = issue.to_dict()

        assert result["category"] == "Test"
        assert result["impact"] == "low"
        assert "element" in result
        assert "recommendation" in result


class TestSEOScore:
    """Tests for SEOScore dataclass."""

    def test_creation_defaults(self):
        """Should create SEOScore with defaults."""
        score = SEOScore()

        assert score.overall == 0
        assert score.title == 0
        assert score.meta_tags == 0

    def test_creation_with_values(self):
        """Should create SEOScore with values."""
        score = SEOScore(
            overall=85,
            title=90,
            meta_tags=80,
            headings=75,
        )

        assert score.overall == 85
        assert score.title == 90

    def test_to_dict(self):
        """Should convert to dictionary."""
        score = SEOScore(overall=75)

        result = score.to_dict()

        assert result["overall"] == 75
        assert "title" in result
        assert "meta_tags" in result


class TestSEOReport:
    """Tests for SEOReport dataclass."""

    def test_creation(self):
        """Should create SEOReport."""
        report = SEOReport(url="https://example.com")

        assert report.url == "https://example.com"
        assert report.issues == []
        assert report.h1_tags == []
        assert report.og_tags == {}

    def test_get_issue_count(self):
        """Should return correct issue count."""
        issues = [
            SEOIssue("Test", "1", "Desc", "high"),
            SEOIssue("Test", "2", "Desc", "medium"),
        ]
        report = SEOReport(url="https://example.com", issues=issues)

        assert report.get_issue_count() == 2

    def test_to_dict(self):
        """Should convert to dictionary."""
        issue = SEOIssue("Test", "Test", "Desc", "low")
        report = SEOReport(url="https://example.com", issues=[issue])

        result = report.to_dict()

        assert result["url"] == "https://example.com"
        assert "scores" in result
        assert "summary" in result
        assert "page_info" in result
        assert "issues" in result


class TestSEOAnalyzer:
    """Tests for SEOAnalyzer class."""

    def test_initialization(self):
        """Should initialize analyzer."""
        analyzer = SEOAnalyzer()

        assert analyzer._context is None
        assert analyzer._report is None

    def test_calculate_scores_title(self):
        """Should calculate title score correctly."""
        analyzer = SEOAnalyzer()
        
        # Perfect title
        report = SEOReport(url="https://example.com")
        report.page_title = "A Good Title Between 50 and 60 Characters"
        scores = analyzer._calculate_scores(report)
        assert scores.title == 100
        
        # No title
        report.page_title = ""
        scores = analyzer._calculate_scores(report)
        assert scores.title == 0
        
        # Short title
        report.page_title = "Short"
        scores = analyzer._calculate_scores(report)
        assert scores.title == 50

    def test_calculate_scores_meta(self):
        """Should calculate meta score correctly."""
        analyzer = SEOAnalyzer()
        
        # Good meta description (within 120-160 range)
        report = SEOReport(url="https://example.com")
        # 130+ characters to be in the optimal range
        report.meta_description = "This is a great meta description with about 130 characters that provides a good summary of the page content for search engines."
        scores = analyzer._calculate_scores(report)
        assert scores.meta_tags == 100
        
        # No meta description
        report.meta_description = ""
        scores = analyzer._calculate_scores(report)
        assert scores.meta_tags == 50

    def test_calculate_scores_headings(self):
        """Should calculate headings score correctly."""
        analyzer = SEOAnalyzer()
        
        # Perfect headings
        report = SEOReport(url="https://example.com")
        report.h1_tags = ["Main Title"]
        report.h2_tags = ["Subtitle 1", "Subtitle 2"]
        scores = analyzer._calculate_scores(report)
        assert scores.headings == 100
        
        # No h1
        report.h1_tags = []
        scores = analyzer._calculate_scores(report)
        assert scores.headings == 60
        
        # Multiple h1
        report.h1_tags = ["Title 1", "Title 2"]
        scores = analyzer._calculate_scores(report)
        assert scores.headings == 70

    def test_calculate_scores_images(self):
        """Should calculate images score correctly."""
        analyzer = SEOAnalyzer()
        
        # All images with alt
        report = SEOReport(url="https://example.com")
        report.total_images = 10
        report.images_with_alt = 10
        report.images_without_alt = 0
        scores = analyzer._calculate_scores(report)
        assert scores.images == 100
        
        # No alt images
        report.total_images = 10
        report.images_with_alt = 0
        report.images_without_alt = 10
        scores = analyzer._calculate_scores(report)
        assert scores.images == 0
        
        # 50% with alt
        report.total_images = 10
        report.images_with_alt = 5
        report.images_without_alt = 5
        scores = analyzer._calculate_scores(report)
        assert scores.images == 50

    def test_calculate_keyword_density(self):
        """Should calculate keyword density correctly."""
        analyzer = SEOAnalyzer()
        
        text = "python python python code tutorial programming"
        density = analyzer._calculate_keyword_density(text)
        
        assert "python" in density
        # python appears 3 times out of 6 words = 50%
        assert density["python"] == 50.0
        
        # Short words should be filtered
        assert "a" not in density
        assert "the" not in density

    def test_extract_text_content(self):
        """Should extract text content correctly."""
        from bs4 import BeautifulSoup
        
        analyzer = SEOAnalyzer()
        html = """
        <html>
            <head><title>Test</title></head>
            <body>
                <p>Hello World</p>
                <script>alert('test');</script>
                <style>.hidden { display: none; }</style>
                <p>More content</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "lxml")
        text = analyzer._extract_text_content(soup)
        
        assert "Hello World" in text
        assert "More content" in text
        assert "alert" not in text
        assert "hidden" not in text

    def test_extract_og_tags(self):
        """Should extract Open Graph tags correctly."""
        from bs4 import BeautifulSoup
        
        analyzer = SEOAnalyzer()
        html = """
        <html>
            <head>
                <meta property="og:title" content="Test Title">
                <meta property="og:description" content="Test Description">
                <meta property="og:image" content="test.jpg">
                <meta name="twitter:card" content="summary">
            </head>
            <body></body>
        </html>
        """
        soup = BeautifulSoup(html, "lxml")
        og_tags = analyzer._extract_og_tags(soup)
        
        assert "og:title" in og_tags
        assert og_tags["og:title"] == "Test Title"
        assert "og:description" in og_tags

    def test_extract_twitter_tags(self):
        """Should extract Twitter Card tags correctly."""
        from bs4 import BeautifulSoup
        
        analyzer = SEOAnalyzer()
        html = """
        <html>
            <head>
                <meta name="twitter:card" content="summary">
                <meta name="twitter:title" content="Twitter Title">
            </head>
            <body></body>
        </html>
        """
        soup = BeautifulSoup(html, "lxml")
        twitter_tags = analyzer._extract_twitter_tags(soup)
        
        assert "twitter:card" in twitter_tags
        assert twitter_tags["twitter:card"] == "summary"
