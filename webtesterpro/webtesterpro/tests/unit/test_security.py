"""
Tests for the WebTesterPro security module.
"""

import pytest
from webtesterpro.modules.security.security_scanner import (
    SecurityScanner,
    SecurityIssue,
    SecurityReport,
    RiskLevel,
)


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_risk_levels_exist(self):
        """Should have all risk levels defined."""
        assert RiskLevel.CRITICAL.value == "Critical"
        assert RiskLevel.HIGH.value == "High"
        assert RiskLevel.MEDIUM.value == "Medium"
        assert RiskLevel.LOW.value == "Low"
        assert RiskLevel.INFO.value == "Info"

    def test_risk_level_order(self):
        """Risk levels should be ordered by severity."""
        from webtesterpro.modules.security.security_scanner import Severity
        
        assert Severity.CRITICAL.value > Severity.HIGH.value
        assert Severity.HIGH.value > Severity.MEDIUM.value
        assert Severity.MEDIUM.value > Severity.LOW.value
        assert Severity.LOW.value > Severity.INFO.value


class TestSecurityIssue:
    """Tests for SecurityIssue dataclass."""

    def test_creation(self):
        """Should create security issue with required fields."""
        issue = SecurityIssue(
            category="Security Headers",
            title="Missing CSP",
            description="Content-Security-Policy header missing",
            risk_level=RiskLevel.HIGH,
            url="https://example.com",
        )

        assert issue.category == "Security Headers"
        assert issue.title == "Missing CSP"
        assert issue.risk_level == RiskLevel.HIGH
        assert issue.evidence == ""

    def test_creation_with_all_fields(self):
        """Should create security issue with all fields."""
        issue = SecurityIssue(
            category="SSL/TLS",
            title="No HTTPS",
            description="Site not using HTTPS",
            risk_level=RiskLevel.CRITICAL,
            url="https://example.com",
            evidence="http://example.com detected",
            recommendation="Enable HTTPS",
            cwe_id="CWE-319",
            remediation="Install SSL certificate",
        )

        assert issue.cwe_id == "CWE-319"
        assert issue.recommendation == "Enable HTTPS"
        assert issue.remediation == "Install SSL certificate"

    def test_to_dict(self):
        """Should convert to dictionary."""
        issue = SecurityIssue(
            category="Test",
            title="Test Issue",
            description="Test description",
            risk_level=RiskLevel.MEDIUM,
            url="https://example.com",
        )

        result = issue.to_dict()

        assert result["category"] == "Test"
        assert result["title"] == "Test Issue"
        assert result["risk_level"] == "Medium"
        assert result["url"] == "https://example.com"


class TestSecurityReport:
    """Tests for SecurityReport dataclass."""

    def test_creation(self):
        """Should create security report."""
        report = SecurityReport(url="https://example.com")

        assert report.url == "https://example.com"
        assert report.issues == []
        assert report.critical_count == 0
        assert report.high_count == 0

    def test_counts_updated(self):
        """Should update issue counts automatically."""
        issues = [
            SecurityIssue("Test", "1", "Desc", RiskLevel.CRITICAL, "url"),
            SecurityIssue("Test", "2", "Desc", RiskLevel.CRITICAL, "url"),
            SecurityIssue("Test", "3", "Desc", RiskLevel.HIGH, "url"),
            SecurityIssue("Test", "4", "Desc", RiskLevel.MEDIUM, "url"),
            SecurityIssue("Test", "5", "Desc", RiskLevel.LOW, "url"),
            SecurityIssue("Test", "6", "Desc", RiskLevel.INFO, "url"),
        ]
        report = SecurityReport(url="https://example.com", issues=issues)

        assert report.critical_count == 2
        assert report.high_count == 1
        assert report.medium_count == 1
        assert report.low_count == 1
        assert report.info_count == 1

    def test_overall_risk_score(self):
        """Should calculate overall risk score."""
        issues = [
            SecurityIssue("Test", "1", "Desc", RiskLevel.CRITICAL, "url"),
            SecurityIssue("Test", "2", "Desc", RiskLevel.HIGH, "url"),
        ]
        report = SecurityReport(url="https://example.com", issues=issues)

        score = report.get_overall_risk_score()

        # 100 - (1 * 30) - (1 * 20) = 50
        assert score == 50

    def test_overall_risk_score_max(self):
        """Should return max score when no issues."""
        report = SecurityReport(url="https://example.com")

        score = report.get_overall_risk_score()

        assert score == 100

    def test_risk_rating_critical(self):
        """Should return CRITICAL when critical issues exist."""
        issues = [
            SecurityIssue("Test", "1", "Desc", RiskLevel.CRITICAL, "url"),
        ]
        report = SecurityReport(url="https://example.com", issues=issues)

        rating = report.get_risk_rating()

        assert rating == "CRITICAL"

    def test_risk_rating_high(self):
        """Should return HIGH when high issues exist."""
        issues = [
            SecurityIssue("Test", "1", "Desc", RiskLevel.HIGH, "url"),
        ]
        report = SecurityReport(url="https://example.com", issues=issues)

        rating = report.get_risk_rating()

        assert rating == "HIGH"

    def test_risk_rating_secure(self):
        """Should return SECURE when no issues."""
        report = SecurityReport(url="https://example.com")

        rating = report.get_risk_rating()

        assert rating == "SECURE"

    def test_to_dict(self):
        """Should convert to dictionary."""
        issue = SecurityIssue(
            category="Test",
            title="Test",
            description="Desc",
            risk_level=RiskLevel.LOW,
            url="https://example.com",
        )
        report = SecurityReport(url="https://example.com", issues=[issue])

        result = report.to_dict()

        assert result["url"] == "https://example.com"
        assert "summary" in result
        assert "issues" in result
        assert result["summary"]["total"] == 1
        assert result["summary"]["low"] == 1


class TestSecurityScanner:
    """Tests for SecurityScanner class."""

    def test_initialization(self):
        """Should initialize scanner."""
        scanner = SecurityScanner()

        assert scanner._context is None
        assert scanner._report is None

    def test_security_headers_defined(self):
        """Should have security headers defined."""
        headers = SecurityScanner.SECURITY_HEADERS

        assert "content-security-policy" in headers
        assert "strict-transport-security" in headers
        assert "x-frame-options" in headers
        assert "x-content-type-options" in headers

    def test_sensitive_files_defined(self):
        """Should have sensitive file patterns defined."""
        files = SecurityScanner.SENSITIVE_FILES

        assert len(files) > 0
        assert any(".env" in f[1] for f in files)
        assert any("Git" in f[1] for f in files)

    def test_xss_patterns_defined(self):
        """Should have XSS patterns defined."""
        patterns = SecurityScanner.XSS_PATTERNS

        assert len(patterns) > 0
        assert any("script" in p[1].lower() for p in patterns)

    def test_sqli_patterns_defined(self):
        """Should have SQLi patterns defined."""
        patterns = SecurityScanner.SQLI_PATTERNS

        assert len(patterns) > 0
        assert any("union" in p[0].lower() for p in patterns)

    def test_headers_have_risk_level(self):
        """All headers should have risk level defined."""
        for header, info in SecurityScanner.SECURITY_HEADERS.items():
            assert "risk" in info
            assert isinstance(info["risk"], RiskLevel)

    def test_headers_have_remediation(self):
        """All headers should have remediation defined."""
        for header, info in SecurityScanner.SECURITY_HEADERS.items():
            assert "remediation" in info
            assert len(info["remediation"]) > 0
