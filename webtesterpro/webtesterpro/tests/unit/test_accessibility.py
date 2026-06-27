"""
Tests for the WebTesterPro accessibility module.
"""

import pytest
from webtesterpro.modules.accessibility.accessibility_checker import (
    AccessibilityChecker,
    A11yIssue,
    A11yReport,
    ViolationLevel,
)


class TestViolationLevel:
    """Tests for ViolationLevel enum."""

    def test_violation_levels_exist(self):
        """Should have all violation levels defined."""
        assert ViolationLevel.CRITICAL.value == "critical"
        assert ViolationLevel.SERIOUS.value == "serious"
        assert ViolationLevel.MODERATE.value == "moderate"
        assert ViolationLevel.MINOR.value == "minor"


class TestA11yIssue:
    """Tests for A11yIssue dataclass."""

    def test_creation(self):
        """Should create A11yIssue with required fields."""
        issue = A11yIssue(
            rule_id="image-alt",
            description="Images must have alt text",
            help="Images missing alt text",
            help_url="https://example.com/rule",
            impact=ViolationLevel.SERIOUS,
        )

        assert issue.rule_id == "image-alt"
        assert issue.impact == ViolationLevel.SERIOUS
        assert issue.wcag_criterion == ""
        assert issue.node_count == 1

    def test_creation_with_all_fields(self):
        """Should create A11yIssue with all fields."""
        issue = A11yIssue(
            rule_id="color-contrast",
            description="Color contrast issue",
            help="Insufficient color contrast",
            help_url="https://example.com/contrast",
            impact=ViolationLevel.MODERATE,
            wcag_criterion="1.4.3",
            wcag_level="AA",
            html="<p style='color:#999'>Text</p>",
            selector="#content > p",
            fix_description="Increase contrast ratio",
        )

        assert issue.wcag_criterion == "1.4.3"
        assert issue.wcag_level == "AA"
        assert issue.fix_description == "Increase contrast ratio"

    def test_to_dict(self):
        """Should convert to dictionary."""
        issue = A11yIssue(
            rule_id="test",
            description="Test issue",
            help="Help text",
            help_url="https://example.com",
            impact=ViolationLevel.MINOR,
        )

        result = issue.to_dict()

        assert result["rule_id"] == "test"
        assert result["impact"] == "minor"
        assert result["wcag_criterion"] == ""
        assert "html" in result
        assert "selector" in result


class TestA11yReport:
    """Tests for A11yReport dataclass."""

    def test_creation(self):
        """Should create A11yReport."""
        report = A11yReport(url="https://example.com")

        assert report.url == "https://example.com"
        assert report.issues == []
        assert report.critical_count == 0
        assert report.serious_count == 0

    def test_counts_updated(self):
        """Should update issue counts automatically."""
        issues = [
            A11yIssue("test", "desc", "help", "url", ViolationLevel.CRITICAL),
            A11yIssue("test", "desc", "help", "url", ViolationLevel.SERIOUS),
            A11yIssue("test", "desc", "help", "url", ViolationLevel.SERIOUS),
            A11yIssue("test", "desc", "help", "url", ViolationLevel.MODERATE),
            A11yIssue("test", "desc", "help", "url", ViolationLevel.MINOR),
        ]
        report = A11yReport(url="https://example.com", issues=issues)

        assert report.critical_count == 1
        assert report.serious_count == 2
        assert report.moderate_count == 1
        assert report.minor_count == 1

    def test_accessibility_score_perfect(self):
        """Should return 100 for no issues."""
        report = A11yReport(url="https://example.com")

        score = report.get_accessibility_score()

        assert score == 100

    def test_accessibility_score_with_violations(self):
        """Should calculate score based on violations."""
        issues = [
            A11yIssue("test", "desc", "help", "url", ViolationLevel.CRITICAL),
            A11yIssue("test", "desc", "help", "url", ViolationLevel.SERIOUS),
        ]
        report = A11yReport(url="https://example.com", issues=issues)

        score = report.get_accessibility_score()

        # 100 - (1 * 15) - (1 * 10) = 75
        assert score == 75

    def test_conformance_level_fail(self):
        """Should return Fail when critical issues exist."""
        issues = [
            A11yIssue("test", "desc", "help", "url", ViolationLevel.CRITICAL),
        ]
        report = A11yReport(url="https://example.com", issues=issues)

        level = report.get_conformance_level()

        assert level == "Fail"

    def test_conformance_level_a(self):
        """Should return A when only serious issues exist."""
        issues = [
            A11yIssue("test", "desc", "help", "url", ViolationLevel.SERIOUS),
        ]
        report = A11yReport(url="https://example.com", issues=issues)

        level = report.get_conformance_level()

        assert level == "A"

    def test_conformance_level_aaa(self):
        """Should return AAA when no issues."""
        report = A11yReport(url="https://example.com")

        level = report.get_conformance_level()

        assert level == "AAA"

    def test_to_dict(self):
        """Should convert to dictionary."""
        issue = A11yIssue(
            rule_id="test",
            description="Test",
            help="Help",
            help_url="https://example.com",
            impact=ViolationLevel.MINOR,
        )
        report = A11yReport(url="https://example.com", issues=[issue])

        result = report.to_dict()

        assert result["url"] == "https://example.com"
        assert "summary" in result
        assert result["summary"]["total_violations"] == 1
        assert "issues" in result


class TestAccessibilityChecker:
    """Tests for AccessibilityChecker class."""

    def test_initialization(self):
        """Should initialize checker."""
        checker = AccessibilityChecker()

        assert checker._context is None
        assert checker._report is None

    def test_wcag_criteria_defined(self):
        """Should have WCAG criteria defined."""
        criteria = AccessibilityChecker.WCAG_CRITERIA

        assert "1.1.1" in criteria
        assert "1.4.3" in criteria
        assert "2.4.2" in criteria
        assert criteria["1.1.1"]["level"] == "A"
        assert criteria["1.4.3"]["level"] == "AA"

    def test_rule_to_wcag_defined(self):
        """Should have rule to WCAG mapping."""
        mapping = AccessibilityChecker.RULE_TO_WCAG

        assert "image-alt" in mapping
        assert "button-name" in mapping
        assert mapping["image-alt"] == "1.1.1"

    def test_impact_to_violation_level(self):
        """Should convert impact to violation level."""
        checker = AccessibilityChecker()

        assert checker._impact_to_violation_level("critical") == ViolationLevel.CRITICAL
        assert checker._impact_to_violation_level("serious") == ViolationLevel.SERIOUS
        assert checker._impact_to_violation_level("moderate") == ViolationLevel.MODERATE
        assert checker._impact_to_violation_level("minor") == ViolationLevel.MINOR
        assert checker._impact_to_violation_level("unknown") == ViolationLevel.MINOR

    def test_get_wcag_info(self):
        """Should get WCAG info for rule."""
        checker = AccessibilityChecker()

        criterion, level = checker._get_wcag_info("image-alt")

        assert criterion == "1.1.1"
        assert level == "A"

    def test_get_wcag_info_unknown_rule(self):
        """Should return empty for unknown rule."""
        checker = AccessibilityChecker()

        criterion, level = checker._get_wcag_info("unknown-rule")

        assert criterion == ""
        assert level == ""

    def test_get_fix_description(self):
        """Should get fix description for rule."""
        checker = AccessibilityChecker()

        desc = checker._get_fix_description("image-alt")

        assert "alt" in desc.lower()
        assert len(desc) > 0

    def test_get_fix_description_unknown(self):
        """Should return generic message for unknown rule."""
        checker = AccessibilityChecker()

        desc = checker._get_fix_description("unknown-rule")

        assert "WCAG" in desc
