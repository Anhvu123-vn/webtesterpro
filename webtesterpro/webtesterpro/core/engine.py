"""
WebTesterPro Main Engine

The core engine that coordinates all testing modules.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from webtesterpro.core.config import Config

# Fix for Windows + Python 3.13 + Playwright compatibility
# Set policy inside function to ensure it takes effect
def _ensure_windows_event_loop():
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass
from webtesterpro.modules.crawler.crawler import WebsiteCrawler
from webtesterpro.modules.scanner.scanner import WebsiteScanner
from webtesterpro.modules.analyzer.analyzer import WebsiteAnalyzer
from webtesterpro.modules.monitor.monitor import WebsiteMonitor
from webtesterpro.modules.performance.performance_tester import PerformanceTester
from webtesterpro.modules.security.security_scanner import SecurityScanner
from webtesterpro.modules.accessibility.accessibility_checker import AccessibilityChecker
from webtesterpro.modules.seo.seo_analyzer import SEOAnalyzer
from webtesterpro.modules.visual.visual_tester import VisualTester
from webtesterpro.modules.reporting.report_generator import ReportGenerator, ReportData

logger = logging.getLogger(__name__)


class WebTesterEngine:
    """
    Main engine for WebTesterPro.
    
    Coordinates all testing modules and manages the browser lifecycle.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the WebTesterPro engine.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or Config.load_default()
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        
        self.crawler = WebsiteCrawler(self.config)
        self.scanner = WebsiteScanner(self.config)
        self.analyzer = WebsiteAnalyzer(self.config)
        self.monitor = WebsiteMonitor(self.config)
        self.performance = PerformanceTester(self.config)
        self.security = SecurityScanner(self.config)
        self.accessibility = AccessibilityChecker(self.config)
        self.seo = SEOAnalyzer(self.config)
        self.visual = VisualTester(self.config)
        self.reporter = ReportGenerator(self.config)

    async def __aenter__(self) -> "WebTesterEngine":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()

    async def start(self) -> None:
        """Initialize Playwright and launch browser."""
        _ensure_windows_event_loop()
        logger.info("Starting WebTesterPro engine...")
        self._playwright = await async_playwright().start()
        
        launch_options = {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        }
        
        self._browser = await self._playwright.chromium.launch(**launch_options)
        
        context_options = {
            "user_agent": self.config.crawler.user_agent,
            "viewport": {"width": 1920, "height": 1080},
            "ignore_https_errors": not self.config.scanner.verify_ssl,
        }
        
        self._context = await self._browser.new_context(**context_options)
        
        # Update modules with browser context
        self.crawler.set_context(self._context)
        self.scanner.set_context(self._context)
        self.performance.set_context(self._context)
        self.security.set_context(self._context)
        self.accessibility.set_context(self._context)
        self.seo.set_context(self._context)
        self.visual.set_context(self._context)
        
        logger.info("WebTesterPro engine started successfully")

    async def stop(self) -> None:
        """Stop Playwright and cleanup resources."""
        logger.info("Stopping WebTesterPro engine...")
        
        if self._context:
            await self._context.close()
            self._context = None
        
        if self._browser:
            await self._browser.close()
            self._browser = None
        
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        
        logger.info("WebTesterPro engine stopped")

    async def new_page(self) -> Page:
        """Create a new page in the current context."""
        if not self._context:
            raise RuntimeError("Engine not started. Call start() first.")
        return await self._context.new_page()

    async def crawl_site(
        self,
        url: str,
        max_depth: Optional[int] = None,
        max_pages: Optional[int] = None,
        login_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Crawl a website.
        
        Args:
            url: Starting URL to crawl.
            max_depth: Maximum crawl depth.
            max_pages: Maximum number of pages to crawl.
            login_data: Optional login credentials.
            
        Returns:
            Crawl results as a dictionary.
        """
        if login_data:
            await self.login(login_data)
        
        return await self.crawler.crawl(url, max_depth, max_pages)

    async def login(self, login_data: Dict) -> bool:
        """
        Perform login on a website.
        
        Args:
            login_data: Dictionary with 'url', 'username', 'password', and optional 'selectors'.
            
        Returns:
            True if login successful, False otherwise.
        """
        url = login_data.get("url")
        username = login_data.get("username")
        password = login_data.get("password")
        selectors = login_data.get("selectors")
        
        if not all([url, username, password]):
            raise ValueError("login_data must contain url, username, and password")
        
        page = await self.new_page()
        try:
            await page.goto(url, wait_until="networkidle")
            
            username_field = selectors.get("username", "#username") if selectors else "#username"
            password_field = selectors.get("password", "#password") if selectors else "#password"
            submit_button = selectors.get("submit", "button[type='submit']") if selectors else "button[type='submit']"
            
            await page.fill(username_field, username)
            await page.fill(password_field, password)
            await page.click(submit_button)
            
            await page.wait_for_load_state("networkidle")
            
            logger.info(f"Login successful at {url}")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
        finally:
            await page.close()

    async def scan_site(self, url: str) -> Dict[str, Any]:
        """
        Scan a website for forms, links, and resources.
        
        Args:
            url: URL to scan.
            
        Returns:
            Scan results as a dictionary.
        """
        return await self.scanner.scan(url)

    async def analyze_site(self, url: str) -> Dict[str, Any]:
        """
        Analyze a website for SEO, performance, and security.
        
        Args:
            url: URL to analyze.
            
        Returns:
            Analysis results as a dictionary.
        """
        return await self.analyzer.analyze(url)

    async def monitor_site(
        self,
        url: str,
        interval: Optional[int] = None,
        duration: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Monitor a website for uptime.
        
        Args:
            url: URL to monitor.
            interval: Check interval in seconds.
            duration: Total monitoring duration in seconds (None = indefinite).
            
        Returns:
            Monitoring results as a dictionary.
        """
        return await self.monitor.monitor(url, interval, duration)

    async def test_performance(
        self,
        url: str,
        wait_until: str = "networkidle",
    ) -> Dict[str, Any]:
        """
        Test the performance of a website.
        
        Args:
            url: URL to test.
            wait_until: Wait until which event to consider page loaded.
                       Options: 'load', 'domcontentloaded', 'networkidle'
            
        Returns:
            Performance test results as a dictionary.
        """
        return await self.performance.test_performance(url, wait_until)

    async def scan_security(
        self,
        url: str,
        check_xss: bool = True,
        check_sqli: bool = True,
        check_sensitive: bool = True,
    ) -> Dict[str, Any]:
        """
        Scan a website for security issues.
        
        Args:
            url: URL to scan.
            check_xss: Enable XSS pattern detection.
            check_sqli: Enable SQL injection pattern detection.
            check_sensitive: Enable sensitive file checks.
            
        Returns:
            Security scan results as a dictionary.
        """
        return await self.security.scan(url, check_xss, check_sqli, check_sensitive)

    async def check_accessibility(
        self,
        url: str,
        run_axe: bool = True,
        run_manual: bool = True,
    ) -> Dict[str, Any]:
        """
        Check website accessibility.
        
        Args:
            url: URL to check.
            run_axe: Run axe-core automated checks.
            run_manual: Run additional manual checks.
            
        Returns:
            Accessibility check results as a dictionary.
        """
        return await self.accessibility.check(url, run_axe, run_manual)

    async def analyze_seo(
        self,
        url: str,
        check_keyword_density: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze website SEO.
        
        Args:
            url: URL to analyze.
            check_keyword_density: Include keyword density analysis.
            
        Returns:
            SEO analysis results as a dictionary.
        """
        return await self.seo.analyze(url, check_keyword_density)

    async def capture_screenshot(
        self,
        url: str,
        viewport_name: str = "desktop",
        full_page: bool = False,
    ) -> Dict[str, Any]:
        """
        Capture a screenshot of a URL.
        
        Args:
            url: URL to screenshot.
            viewport_name: Viewport name (desktop, laptop, tablet-landscape, mobile-portrait, etc.)
            full_page: Capture full scrollable page.
            
        Returns:
            Screenshot result as a dictionary.
        """
        from webtesterpro.modules.visual.visual_tester import Viewport
        
        viewport_map = {
            "desktop": Viewport.desktop,
            "laptop": Viewport.laptop,
            "tablet-landscape": Viewport.tablet_landscape,
            "tablet-portrait": Viewport.tablet_portrait,
            "mobile-landscape": Viewport.mobile_landscape,
            "mobile-portrait": Viewport.mobile_portrait,
        }
        
        viewport_func = viewport_map.get(viewport_name, Viewport.desktop)
        viewport = viewport_func()
        
        result = await self.visual.screenshot(url, viewport, full_page=full_page)
        return result.to_dict()


async def run_demo() -> None:
    """Run a demo of WebTesterPro."""
    print("=" * 60)
    print("WebTesterPro Demo")
    print("=" * 60)
    
    async with WebTesterEngine() as engine:
        print("\n1. Testing basic page load...")
        page = await engine.new_page()
        await page.goto("https://example.com")
        title = await page.title()
        print(f"   Page title: {title}")
        await page.close()
        
        print("\n2. Crawler module ready...")
        print(f"   Max depth: {engine.config.crawler.max_depth}")
        print(f"   Max pages: {engine.config.crawler.max_pages}")
        
        print("\n3. Scanner module ready...")
        print(f"   Check forms: {engine.config.scanner.check_forms}")
        print(f"   Check links: {engine.config.scanner.check_links}")
        
        print("\nDemo completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demo())
