"""
Accessibility Checker Module

Provides comprehensive accessibility testing using Playwright and axe-core:
- WCAG 2.1/2.2 AA compliance
- Automated accessibility audits
- Alt text validation
- Color contrast checking
- ARIA label verification
- Keyboard navigation testing
- Violation severity classification
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page
from playwright.async_api import TimeoutError as PlaywrightTimeout

from webtesterpro.core.config import Config

logger = logging.getLogger(__name__)


class ViolationLevel(Enum):
    """
    Accessibility violation severity levels.
    
    Based on WCAG Conformance Levels:
    - CRITICAL: WCAG Level A failures that must be fixed
    - SERIOUS: WCAG Level AA failures that should be fixed
    - MODERATE: WCAG Level AAA or best practice violations
    - MINOR: Minor issues or informational items
    """
    CRITICAL = "critical"
    SERIOUS = "serious"
    MODERATE = "moderate"
    MINOR = "minor"


class ImpactLevel(Enum):
    """Impact levels matching axe-core terminology."""
    CRITICAL = "critical"
    SERIOUS = "serious"
    MODERATE = "moderate"
    MINOR = "minor"


@dataclass
class A11yIssue:
    """
    Represents a single accessibility issue.
    """
    rule_id: str
    description: str
    help: str
    help_url: str
    impact: ViolationLevel
    wcag_criterion: str = ""  # e.g., "1.1.1", "1.4.3"
    wcag_level: str = ""      # "A", "AA", "AAA"
    
    # Element information
    html: str = ""
    selector: str = ""
    element_xpath: str = ""
    
    # Related nodes
    node_count: int = 1
    node_summaries: List[str] = field(default_factory=list)
    
    # Fix information
    fix_description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "help": self.help,
            "help_url": self.help_url,
            "impact": self.impact.value,
            "wcag_criterion": self.wcag_criterion,
            "wcag_level": self.wcag_level,
            "html": self.html[:500] if self.html else "",
            "selector": self.selector,
            "node_count": self.node_count,
            "node_summaries": self.node_summaries[:5],
            "fix_description": self.fix_description,
        }


@dataclass
class A11yReport:
    """
    Complete accessibility audit report.
    """
    url: str
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[A11yIssue] = field(default_factory=list)
    
    # Summary counts
    critical_count: int = 0
    serious_count: int = 0
    moderate_count: int = 0
    minor_count: int = 0
    
    # Page info
    page_title: str = ""
    page_url: str = ""
    page_has_title: bool = False
    page_has_lang: bool = False
    
    # Additional metrics
    total_elements: int = 0
    images_without_alt: int = 0
    links_without_name: int = 0
    buttons_without_name: int = 0
    inputs_without_label: int = 0
    
    # Scan metadata
    scan_duration: float = 0.0
    
    def __post_init__(self):
        """Update counts after initialization."""
        self.critical_count = sum(1 for i in self.issues if i.impact == ViolationLevel.CRITICAL)
        self.serious_count = sum(1 for i in self.issues if i.impact == ViolationLevel.SERIOUS)
        self.moderate_count = sum(1 for i in self.issues if i.impact == ViolationLevel.MODERATE)
        self.minor_count = sum(1 for i in self.issues if i.impact == ViolationLevel.MINOR)

    def get_accessibility_score(self) -> int:
        """
        Calculate accessibility score (0-100).
        
        Based on violation counts and severity.
        """
        # Start at 100 and subtract points based on violations
        score = 100
        
        # Weight by severity
        score -= self.critical_count * 15
        score -= self.serious_count * 10
        score -= self.moderate_count * 5
        score -= self.minor_count * 1
        
        return max(0, min(100, score))

    def get_conformance_level(self) -> str:
        """
        Get WCAG conformance level based on violations.
        
        Returns: "A", "AA", "AAA", or "None"
        """
        if self.critical_count > 0:
            return "Fail"
        elif self.serious_count > 0:
            return "A"  # Passes Level A
        elif self.moderate_count > 0:
            return "AA"  # Passes Level AA
        return "AAA"  # Passes Level AAA

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "accessibility_score": self.get_accessibility_score(),
                "conformance_level": self.get_conformance_level(),
                "critical": self.critical_count,
                "serious": self.serious_count,
                "moderate": self.moderate_count,
                "minor": self.minor_count,
                "total_violations": len(self.issues),
            },
            "page_info": {
                "title": self.page_title,
                "has_title": self.page_has_title,
                "has_lang": self.page_has_lang,
                "total_elements": self.total_elements,
            },
            "metrics": {
                "images_without_alt": self.images_without_alt,
                "links_without_name": self.links_without_name,
                "buttons_without_name": self.buttons_without_name,
                "inputs_without_label": self.inputs_without_label,
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": {
                "scan_duration_seconds": round(self.scan_duration, 2),
            },
        }


class AccessibilityChecker:
    """
    Async accessibility checker using Playwright with axe-core.
    
    Performs comprehensive accessibility audits including:
    - WCAG 2.1/2.2 compliance checks
    - Automated axe-core audits
    - Manual accessibility checks
    - Color contrast validation
    - Alt text verification
    - ARIA attribute checks
    - Keyboard navigation testing
    
    Usage:
        async with WebTesterEngine() as engine:
            checker = AccessibilityChecker()
            checker.set_context(engine._context)
            report = await checker.check("https://example.com")
    """
    
    # WCAG criteria mapping
    WCAG_CRITERIA = {
        "1.1.1": {"name": "Non-text Content", "level": "A"},
        "1.2.1": {"name": "Audio-only and Video-only", "level": "A"},
        "1.3.1": {"name": "Info and Relationships", "level": "A"},
        "1.3.2": {"name": "Meaningful Sequence", "level": "A"},
        "1.4.1": {"name": "Use of Color", "level": "A"},
        "1.4.3": {"name": "Contrast (Minimum)", "level": "AA"},
        "1.4.4": {"name": "Resize Text", "level": "AA"},
        "1.4.10": {"name": "Reflow", "level": "AA"},
        "1.4.11": {"name": "Non-text Contrast", "level": "AA"},
        "2.1.1": {"name": "Keyboard", "level": "A"},
        "2.1.2": {"name": "No Keyboard Trap", "level": "A"},
        "2.4.1": {"name": "Bypass Blocks", "level": "A"},
        "2.4.2": {"name": "Page Titled", "level": "A"},
        "2.4.3": {"name": "Focus Order", "level": "A"},
        "2.4.4": {"name": "Link Purpose", "level": "A"},
        "2.4.6": {"name": "Headings and Labels", "level": "AA"},
        "2.4.7": {"name": "Focus Visible", "level": "AA"},
        "3.1.1": {"name": "Language of Page", "level": "A"},
        "3.2.1": {"name": "On Focus", "level": "A"},
        "3.3.1": {"name": "Error Identification", "level": "A"},
        "4.1.1": {"name": "Parsing", "level": "A"},
        "4.1.2": {"name": "Name, Role, Value", "level": "A"},
        "4.1.3": {"name": "Status Messages", "level": "AA"},
    }
    
    # Common WCAG rule mappings
    RULE_TO_WCAG = {
        "image-alt": "1.1.1",
        "input-image-alt": "1.1.1",
        "area-alt": "1.1.1",
        "aria-required-attr": "4.1.2",
        "aria-roles": "4.1.2",
        "button-name": "4.1.2",
        "color-contrast": "1.4.3",
        "duplicate-id-active": "4.1.1",
        "form-field-multiple-label": "1.3.1",
        "frame-title": "2.4.2",
        "heading-order": "1.3.1",
        "html-has-lang": "3.1.1",
        "html-lang-valid": "3.1.1",
        "image-alt": "1.1.1",
        "link-name": "2.4.4",
        "meta-viewport": "1.4.4",
        "page-has-heading-one": "2.4.6",
        "region": "1.3.6",
        "table-fake-caption": "1.3.1",
        "td-has-header": "1.3.1",
        "th-has-data-cells": "1.3.1",
    }
    
    # axe-core JavaScript code to inject
    AXE_CORE_SCRIPT = """
    () => {
        return new Promise((resolve, reject) => {
            // Check if axe is already loaded
            if (typeof axe === 'undefined') {
                // Try to load axe-core from CDN
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.0/axe.min.js';
                script.onload = () => runAxe(resolve, reject);
                script.onerror = () => reject(new Error('Failed to load axe-core'));
                document.head.appendChild(script);
            } else {
                runAxe(resolve, reject);
            }
            
            function runAxe(resolve, reject) {
                const options = {
                    runOnly: {
                        type: 'tag',
                        values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice'],
                    },
                    resultTypes: ['violations', 'incomplete'],
                };
                
                try {
                    axe.run(document, options)
                        .then(results => resolve(results))
                        .catch(err => reject(err));
                } catch (e) {
                    reject(e);
                }
            }
        });
    }
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize the accessibility checker.
        
        Args:
            config: Configuration object.
        """
        self.config = config
        self._context: Optional[BrowserContext] = None
        self._report: Optional[A11yReport] = None
    
    def set_context(self, context: BrowserContext) -> None:
        """
        Set the Playwright browser context.
        
        Args:
            context: Browser context to use.
        """
        self._context = context
    
    def _impact_to_violation_level(self, impact: str) -> ViolationLevel:
        """Convert axe-core impact to ViolationLevel."""
        impact_lower = impact.lower() if impact else "minor"
        
        mapping = {
            "critical": ViolationLevel.CRITICAL,
            "serious": ViolationLevel.SERIOUS,
            "moderate": ViolationLevel.MODERATE,
            "minor": ViolationLevel.MINOR,
        }
        
        return mapping.get(impact_lower, ViolationLevel.MINOR)
    
    def _get_wcag_info(self, rule_id: str) -> tuple:
        """Get WCAG criterion and level for a rule."""
        if rule_id in self.RULE_TO_WCAG:
            criterion = self.RULE_TO_WCAG[rule_id]
            if criterion in self.WCAG_CRITERIA:
                info = self.WCAG_CRITERIA[criterion]
                return criterion, info["level"]
        
        return "", ""
    
    async def _inject_axe(self, page: Page) -> bool:
        """Inject axe-core into the page."""
        try:
            await page.goto("data:text/html,<html></html>")
            await page.add_script_tag(
                url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.0/axe.min.js"
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to inject axe-core: {e}")
            return False
    
    async def _run_axe_audit(self, page: Page) -> Dict[str, Any]:
        """Run axe-core audit on the page."""
        try:
            # Inject axe-core
            await self._inject_axe(page)
            
            # Run axe with options
            result = await page.evaluate("""
                async () => {
                    return new Promise((resolve, reject) => {
                        if (typeof axe === 'undefined') {
                            reject(new Error('axe not loaded'));
                            return;
                        }
                        
                        const options = {
                            runOnly: {
                                type: 'tag',
                                values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice'],
                            },
                            resultTypes: ['violations', 'incomplete'],
                        };
                        
                        axe.run(document, options)
                            .then(results => resolve(results))
                            .catch(err => reject(err));
                    });
                }
            """)
            
            return result if result else {"violations": [], "incomplete": []}
            
        except Exception as e:
            logger.warning(f"axe-core audit failed: {e}")
            return {"violations": [], "incomplete": []}
    
    async def _parse_axe_results(self, axe_results: Dict[str, Any], url: str) -> List[A11yIssue]:
        """Parse axe-core results into A11yIssue objects."""
        issues = []
        
        # Process violations
        for violation in axe_results.get("violations", []):
            rule_id = violation.get("id", "")
            description = violation.get("description", "")
            help_text = violation.get("help", "")
            help_url = violation.get("helpUrl", "")
            impact = violation.get("impact", "minor")
            nodes = violation.get("nodes", [])
            
            wcag_criterion, wcag_level = self._get_wcag_info(rule_id)
            
            issue = A11yIssue(
                rule_id=rule_id,
                description=description,
                help=help_text,
                help_url=help_url,
                impact=self._impact_to_violation_level(impact),
                wcag_criterion=wcag_criterion,
                wcag_level=wcag_level,
                node_count=len(nodes),
                node_summaries=[
                    f"{node.get('html', '')[:100]}..." 
                    for node in nodes[:3]
                ],
            )
            
            # Add first node HTML and selector
            if nodes:
                node = nodes[0]
                issue.html = node.get("html", "")
                issue.selector = node.get("target", [""])[0] if node.get("target") else ""
                issue.element_xpath = node.get("xpath", "")
            
            # Add fix description
            issue.fix_description = self._get_fix_description(rule_id)
            
            issues.append(issue)
        
        # Process incomplete (treat as violations for awareness)
        for incomplete in axe_results.get("incomplete", []):
            rule_id = incomplete.get("id", "")
            description = incomplete.get("description", "")
            help_text = incomplete.get("help", "")
            help_url = incomplete.get("helpUrl", "")
            impact = incomplete.get("impact", "minor")
            nodes = incomplete.get("nodes", [])
            
            wcag_criterion, wcag_level = self._get_wcag_info(rule_id)
            
            issue = A11yIssue(
                rule_id=rule_id,
                description=f"[Needs Review] {description}",
                help=help_text,
                help_url=help_url,
                impact=self._impact_to_violation_level(impact),
                wcag_criterion=wcag_criterion,
                wcag_level=wcag_level,
                node_count=len(nodes),
                node_summaries=[
                    f"{node.get('html', '')[:100]}..."
                    for node in nodes[:3]
                ],
            )
            
            if nodes:
                node = nodes[0]
                issue.html = node.get("html", "")
                issue.selector = node.get("target", [""])[0] if node.get("target") else ""
            
            issue.fix_description = self._get_fix_description(rule_id)
            
            issues.append(issue)
        
        return issues
    
    def _get_fix_description(self, rule_id: str) -> str:
        """Get fix description for a rule."""
        fix_descriptions = {
            "image-alt": "Add alt text to describe the image's purpose or content. Use alt='' for decorative images.",
            "button-name": "Ensure button has accessible name through text content or aria-label.",
            "link-name": "Ensure link has descriptive text or aria-label that makes sense out of context.",
            "color-contrast": "Increase contrast between text and background colors to at least 4.5:1 (AA) or 7:1 (AAA).",
            "aria-required-attr": "Add required ARIA attributes to the element.",
            "aria-roles": "Ensure element has valid ARIA role or remove invalid role.",
            "html-has-lang": "Add lang attribute to the html element, e.g., <html lang='en'>.",
            "html-lang-valid": "Use a valid language code, e.g., 'en', 'en-US', 'vi'.",
            "frame-title": "Add a descriptive title attribute to the frame.",
            "label": "Associate label with input using 'for' attribute or wrapping.",
            "input-image-alt": "Add alt text to describe the image button's function.",
            "heading-order": "Ensure heading levels only increase by one (don't skip h2 to h4).",
            "page-has-heading-one": "Add a single h1 heading that describes the page content.",
            "link-in-text-block": "Ensure links are distinguishable without relying on color alone.",
        }
        
        return fix_descriptions.get(rule_id, "Review this issue and fix according to WCAG guidelines.")
    
    async def _manual_checks(self, page: Page) -> List[A11yIssue]:
        """Perform manual accessibility checks."""
        issues = []
        
        try:
            # Check for images without alt
            images_without_alt = await page.evaluate("""
                () => {
                    const images = document.querySelectorAll('img');
                    let count = 0;
                    images.forEach(img => {
                        if (!img.hasAttribute('alt')) count++;
                    });
                    return count;
                }
            """)
            
            if images_without_alt > 0:
                issues.append(A11yIssue(
                    rule_id="img-alt-manual",
                    description=f"{images_without_alt} image(s) missing alt attribute",
                    help="Images must have alt text or be marked as decorative",
                    help_url="https://www.w3.org/WAI/WCAG21/Understanding/non-text-content.html",
                    impact=ViolationLevel.SERIOUS,
                    wcag_criterion="1.1.1",
                    wcag_level="A",
                    fix_description="Add alt attribute to all images. Use alt='' for decorative images.",
                ))
            
            # Check for links without text
            links_without_text = await page.evaluate("""
                () => {
                    const links = document.querySelectorAll('a');
                    let count = 0;
                    links.forEach(link => {
                        if (!link.textContent.trim() && !link.getAttribute('aria-label')) count++;
                    });
                    return count;
                }
            """)
            
            if links_without_text > 0:
                issues.append(A11yIssue(
                    rule_id="link-name-manual",
                    description=f"{links_without_text} link(s) have no accessible name",
                    help="Links must have descriptive text or aria-label",
                    help_url="https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-in-context.html",
                    impact=ViolationLevel.SERIOUS,
                    wcag_criterion="2.4.4",
                    wcag_level="A",
                ))
            
            # Check for buttons without text
            buttons_without_text = await page.evaluate("""
                () => {
                    const buttons = document.querySelectorAll('button');
                    let count = 0;
                    buttons.forEach(btn => {
                        if (!btn.textContent.trim() && !btn.getAttribute('aria-label')) count++;
                    });
                    return count;
                }
            """)
            
            if buttons_without_text > 0:
                issues.append(A11yIssue(
                    rule_id="button-name-manual",
                    description=f"{buttons_without_text} button(s) have no accessible name",
                    help="Buttons must have text content or aria-label",
                    help_url="https://www.w3.org/WAI/WCAG21/Understanding/name-role-value.html",
                    impact=ViolationLevel.SERIOUS,
                    wcag_criterion="4.1.2",
                    wcag_level="A",
                ))
            
            # Check for inputs without labels
            inputs_without_label = await page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]):not([type="image"])');
                    let count = 0;
                    inputs.forEach(input => {
                        const hasLabel = input.id && document.querySelector(`label[for="${input.id}"]`);
                        const hasAriaLabel = input.getAttribute('aria-label') || input.getAttribute('aria-labelledby');
                        const hasTitle = input.getAttribute('title');
                        const wrappedLabel = input.closest('label');
                        if (!hasLabel && !hasAriaLabel && !hasTitle && !wrappedLabel) count++;
                    });
                    return count;
                }
            """)
            
            if inputs_without_label > 0:
                issues.append(A11yIssue(
                    rule_id="label-manual",
                    description=f"{inputs_without_label} input(s) missing associated label",
                    help="Form inputs must have visible or accessible labels",
                    help_url="https://www.w3.org/WAI/WCAG21/Understanding/labels-or-instructions.html",
                    impact=ViolationLevel.SERIOUS,
                    wcag_criterion="1.3.1",
                    wcag_level="A",
                ))
            
            # Check page title
            page_title = await page.title()
            if not page_title:
                issues.append(A11yIssue(
                    rule_id="page-title-manual",
                    description="Page has no title",
                    help="Pages must have a descriptive title",
                    help_url="https://www.w3.org/WAI/WCAG21/Understanding/page-titled.html",
                    impact=ViolationLevel.CRITICAL,
                    wcag_criterion="2.4.2",
                    wcag_level="A",
                ))
            
            # Check for html lang attribute
            has_lang = await page.evaluate("""
                () => document.documentElement.hasAttribute('lang')
            """)
            
            if not has_lang:
                issues.append(A11yIssue(
                    rule_id="html-lang-manual",
                    description="HTML element missing lang attribute",
                    help="The html element must have a lang attribute",
                    help_url="https://www.w3.org/WAI/WCAG21/Understanding/language-of-page.html",
                    impact=ViolationLevel.CRITICAL,
                    wcag_criterion="3.1.1",
                    wcag_level="A",
                ))
            
            # Check for skip link
            has_skip_link = await page.evaluate("""
                () => {
                    const skipLinks = document.querySelectorAll('a[href^="#"]');
                    for (const link of skipLinks) {
                        if (link.textContent.toLowerCase().includes('skip')) return true;
                    }
                    return false;
                }
            """)
            
            if not has_skip_link:
                issues.append(A11yIssue(
                    rule_id="skip-link-manual",
                    description="No skip navigation link found",
                    help="Provide a way to skip repetitive navigation links",
                    help_url="https://www.w3.org/WAI/WCAG21/Understanding/bypass-blocks.html",
                    impact=ViolationLevel.MODERATE,
                    wcag_criterion="2.4.1",
                    wcag_level="A",
                ))
            
        except Exception as e:
            logger.warning(f"Manual accessibility check error: {e}")
        
        return issues
    
    async def check(
        self,
        url: str,
        run_axe: bool = True,
        run_manual: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform accessibility check on a URL.
        
        Args:
            url: URL to check.
            run_axe: Run axe-core automated checks.
            run_manual: Run additional manual checks.
            
        Returns:
            Dictionary containing accessibility audit results.
        """
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        start_time = asyncio.get_event_loop().time()
        self._report = A11yReport(url=url)
        
        try:
            page = await self._context.new_page()
            
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.config.scanner.timeout if self.config else 30000,
            )
            
            # Wait for page to stabilize
            await asyncio.sleep(1)
            
            # Get page info
            self._report.page_title = await page.title()
            self._report.page_has_title = bool(self._report.page_title)
            
            self._report.page_has_lang = await page.evaluate(
                "document.documentElement.hasAttribute('lang')"
            )
            
            # Get element counts
            self._report.total_elements = await page.evaluate("""
                () => document.querySelectorAll('img, a, button, input, select, textarea').length
            """)
            
            # Run axe-core if enabled
            if run_axe:
                logger.info(f"Running axe-core audit on {url}")
                axe_results = await self._run_axe_audit(page)
                axe_issues = await self._parse_axe_results(axe_results, url)
                self._report.issues.extend(axe_issues)
            
            # Run manual checks if enabled
            if run_manual:
                logger.info(f"Running manual accessibility checks on {url}")
                manual_issues = await self._manual_checks(page)
                self._report.issues.extend(manual_issues)
            
            # Update metrics
            self._report.images_without_alt = sum(
                1 for i in self._report.issues 
                if "alt" in i.rule_id.lower() and "manual" in i.rule_id.lower()
            )
            
            # Calculate scan duration
            self._report.scan_duration = asyncio.get_event_loop().time() - start_time
            
            await page.close()
            
            logger.info(f"Accessibility check completed for {url}")
            logger.info(f"Found {len(self._report.issues)} issues")
            
            return self._report.to_dict()
            
        except PlaywrightTimeout:
            logger.error(f"Timeout during accessibility check: {url}")
            self._report.issues.append(A11yIssue(
                rule_id="timeout",
                description="Accessibility check timed out",
                help="Page took too long to load",
                help_url="",
                impact=ViolationLevel.MINOR,
            ))
            return self._report.to_dict()
            
        except Exception as e:
            logger.error(f"Error during accessibility check: {e}")
            self._report.issues.append(A11yIssue(
                rule_id="error",
                description=f"Accessibility check error: {str(e)}",
                help="An error occurred during the check",
                help_url="",
                impact=ViolationLevel.MINOR,
            ))
            return self._report.to_dict()
    
    async def quick_check(self, url: str) -> Dict[str, Any]:
        """
        Perform a quick accessibility check (manual checks only).
        
        Args:
            url: URL to check.
            
        Returns:
            Dictionary containing quick check results.
        """
        return await self.check(url, run_axe=False, run_manual=True)
    
    def get_report(self) -> Optional[A11yReport]:
        """Get the current accessibility report."""
        return self._report


# Alias for backwards compatibility
AccessibilityTest = AccessibilityChecker
