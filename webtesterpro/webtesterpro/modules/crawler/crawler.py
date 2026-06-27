"""
Website Crawler Module

Provides comprehensive website crawling functionality with:
- Depth-limited crawling
- robots.txt respect
- URL blacklist filtering
- Login support (cookies/form)
- Rate limiting and random delays
- Network graph output
"""

import asyncio
import logging
import random
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, List, Dict
from urllib.parse import urljoin, urlparse

import httpx
from playwright.async_api import BrowserContext, Page, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import tldextract

from webtesterpro.core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """Represents a single crawled page."""
    url: str
    status_code: int
    title: str = ""
    html: str = ""
    links: List[Dict[str, str]] = field(default_factory=list)
    resources: List[Dict[str, str]] = field(default_factory=list)
    depth: int = 0
    crawled_at: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


@dataclass
class CrawlStats:
    """Statistics from a crawl operation."""
    total_pages: int = 0
    successful_pages: int = 0
    failed_pages: int = 0
    total_links: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0


class RobotsTxtParser:
    """Parses and checks robots.txt rules."""
    
    def __init__(self):
        self.rules: Dict[str, List[str]] = {}
        self.user_agent: str = "*"
        self._disallow_all = False
    
    async def fetch(self, base_url: str, timeout: int = 5000) -> None:
        """
        Fetch and parse robots.txt from a website.
        
        Args:
            base_url: Base URL of the website.
            timeout: Request timeout in milliseconds.
        """
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        try:
            async with httpx.AsyncClient(timeout=timeout / 1000) as client:
                response = await client.get(robots_url)
                
                if response.status_code == 200:
                    self._parse(response.text)
                    logger.info(f"Fetched robots.txt from {robots_url}")
                else:
                    logger.warning(f"robots.txt not found at {robots_url}")
                    self._disallow_all = True
                    
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt: {e}")
            self._disallow_all = True
    
    def _parse(self, content: str) -> None:
        """Parse robots.txt content."""
        current_user_agent = "*"
        
        for line in content.splitlines():
            line = line.strip()
            
            if not line or line.startswith("#"):
                continue
            
            if line.lower().startswith("user-agent:"):
                current_user_agent = line.split(":", 1)[1].strip()
                if current_user_agent not in self.rules:
                    self.rules[current_user_agent] = []
            
            elif line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if current_user_agent in self.rules:
                    self.rules[current_user_agent].append(path)
            
            elif line.lower().startswith("allow:"):
                path = line.split(":", 1)[1].strip()
                if current_user_agent in self.rules:
                    self.rules[current_user_agent].append(f"!{path}")
    
    def is_allowed(self, url: str) -> bool:
        """
        Check if a URL is allowed by robots.txt.
        
        Args:
            url: URL to check.
            
        Returns:
            True if URL is allowed, False otherwise.
        """
        if self._disallow_all:
            return False
        
        parsed = urlparse(url)
        path = parsed.path or "/"
        
        if path == "":
            path = "/"
        
        rules = self.rules.get("*", [])
        
        for rule in rules:
            is_negative = rule.startswith("!")
            pattern = rule.lstrip("!")
            
            if pattern and re.match(pattern.replace("*", ".*"), path):
                return is_negative
        
        for ua_rules in self.rules.values():
            for rule in ua_rules:
                is_negative = rule.startswith("!")
                pattern = rule.lstrip("!")
                
                if pattern and re.match(pattern.replace("*", ".*"), path):
                    return is_negative
        
        return True


class URLFilter:
    """Filters URLs based on blacklist patterns and domain rules."""
    
    def __init__(self, blacklist: List[str] = None, allowed_domains: List[str] = None):
        self.blacklist = blacklist or []
        self.allowed_domains = allowed_domains or []
    
    def is_allowed(self, url: str) -> bool:
        """
        Check if URL passes the filter.
        
        Args:
            url: URL to check.
            
        Returns:
            True if URL is allowed, False otherwise.
        """
        for pattern in self.blacklist:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        if self.allowed_domains:
            extracted = tldextract.extract(url)
            domain = f"{extracted.domain}.{extracted.suffix}"
            
            if domain not in self.allowed_domains:
                return False
        
        return True


class WebsiteCrawler:
    """
    Async website crawler using Playwright.
    
    Features:
    - Depth-limited crawling
    - robots.txt respect
    - URL blacklist filtering
    - Login support (cookies/form)
    - Rate limiting with random delays
    - Network graph output
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize the crawler.
        
        Args:
            config: Configuration object.
        """
        self.config = config or Config.load_default()
        self._context: Optional[BrowserContext] = None
        self._robots: RobotsTxtParser = RobotsTxtParser()
        self._url_filter = URLFilter(
            blacklist=self.config.crawler.blacklist,
            allowed_domains=self.config.crawler.allowed_domains,
        )
        self._visited: set = set()
        self._pending: List = []
        self._semaphore: asyncio.Semaphore = None
        self._throttle: Optional[asyncio.Lock] = None
        self._stats = CrawlStats()
        self._graph: Dict[str, List[str]] = {}
    
    def set_context(self, context: BrowserContext) -> None:
        """
        Set the Playwright browser context.
        
        Args:
            context: Browser context to use.
        """
        self._context = context
        self._semaphore = asyncio.Semaphore(self.config.crawler.max_concurrent)
    
    async def _throttled_delay(self) -> None:
        """Apply throttled delay between requests."""
        if self._throttle is None:
            self._throttle = asyncio.Lock()
        
        async with self._throttle:
            delay = random.uniform(
                self.config.crawler.delay_min,
                self.config.crawler.delay_max
            )
            await asyncio.sleep(delay)
    
    async def _extract_links(self, page: Page, html: str) -> List[Dict[str, str]]:
        """
        Extract all links from a page.
        
        Args:
            page: Playwright page object.
            html: HTML content of the page.
            
        Returns:
            List of link dictionaries with url, text, and type.
        """
        links = []
        current_url = page.url
        parsed_current = urlparse(current_url)
        
        soup = BeautifulSoup(html, "lxml")
        
        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "")
            absolute_url = urljoin(current_url, href)
            
            parsed = urlparse(absolute_url)
            
            if parsed.scheme in ("http", "https"):
                links.append({
                    "url": absolute_url,
                    "text": tag.get_text(strip=True)[:100],
                    "type": "internal" if parsed.netloc == parsed_current.netloc else "external",
                })
        
        return links
    
    async def _extract_resources(self, page: Page, html: str) -> List[Dict[str, str]]:
        """
        Extract all resources from a page (scripts, stylesheets, images).
        
        Args:
            page: Playwright page object.
            html: HTML content of the page.
            
        Returns:
            List of resource dictionaries.
        """
        resources = []
        current_url = page.url
        
        soup = BeautifulSoup(html, "lxml")
        
        for tag in soup.find_all(["script", "link", "img"], src=True):
            src = tag.get("src", "")
            absolute_url = urljoin(current_url, src)
            
            resources.append({
                "url": absolute_url,
                "type": tag.name,
                "tag": str(tag)[:100],
            })
        
        for tag in soup.find_all("link", href=True):
            href = tag.get("href", "")
            absolute_url = urljoin(current_url, href)
            
            if tag.get("rel") == ["stylesheet"] or tag.name == "link":
                resources.append({
                    "url": absolute_url,
                    "type": "stylesheet",
                    "tag": str(tag)[:100],
                })
        
        return resources
    
    async def _crawl_page(self, url: str, depth: int) -> Optional[CrawlResult]:
        """
        Crawl a single page.
        
        Args:
            url: URL to crawl.
            depth: Current crawl depth.
            
        Returns:
            CrawlResult object or None if failed.
        """
        if url in self._visited:
            return None
        
        self._visited.add(url)
        
        async with self._semaphore:
            await self._throttled_delay()
            
            page = None
            try:
                page = await self._context.new_page()
                
                response = await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.config.crawler.timeout,
                )
                
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                status_code = response.status if response else 0
                title = await page.title()
                html = await page.content()
                
                links = await self._extract_links(page, html)
                resources = await self._extract_resources(page, html)
                
                self._stats.successful_pages += 1
                self._stats.total_links += len(links)
                
                result = CrawlResult(
                    url=url,
                    status_code=status_code,
                    title=title,
                    html=html,
                    links=links,
                    resources=resources,
                    depth=depth,
                )
                
                self._graph[url] = [link["url"] for link in links]
                
                logger.debug(f"Crawled: {url} (status: {status_code}, depth: {depth})")
                
                return result
                
            except PlaywrightTimeout:
                logger.warning(f"Timeout crawling: {url}")
                self._stats.failed_pages += 1
                return CrawlResult(
                    url=url,
                    status_code=0,
                    error="Timeout",
                    depth=depth,
                )
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                self._stats.failed_pages += 1
                return CrawlResult(
                    url=url,
                    status_code=0,
                    error=str(e),
                    depth=depth,
                )
                
            finally:
                if page:
                    await page.close()
    
    async def crawl(
        self,
        url: str,
        max_depth: Optional[int] = None,
        max_pages: Optional[int] = None,
        login_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Crawl a website starting from the given URL.
        
        Args:
            url: Starting URL to crawl.
            max_depth: Maximum crawl depth (default from config).
            max_pages: Maximum number of pages to crawl (default from config).
            login_data: Optional login data for authenticated crawling.
            
        Returns:
            Dictionary containing crawl results and statistics.
        """
        max_depth = max_depth or self.config.crawler.max_depth
        max_pages = max_pages or self.config.crawler.max_pages
        
        self._visited.clear()
        self._pending.clear()
        self._graph.clear()
        self._stats = CrawlStats()
        
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        if self.config.crawler.respect_robots_txt:
            await self._robots.fetch(url)
            
            if not self._robots.is_allowed(url):
                logger.warning(f"Starting URL blocked by robots.txt: {url}")
                return {"error": "Starting URL blocked by robots.txt", "stats": self._stats.__dict__}
        
        if login_data:
            await self._login(login_data)
        
        self._pending.append((url, 0))
        results = []
        
        logger.info(f"Starting crawl of {url}")
        logger.info(f"Max depth: {max_depth}, Max pages: {max_pages}")
        
        while self._pending:
            if len(self._visited) >= max_pages:
                logger.info(f"Reached max pages limit: {max_pages}")
                break
            
            current_url, current_depth = self._pending.pop(0)
            
            if current_depth > max_depth:
                continue
            
            result = await self._crawl_page(current_url, current_depth)
            
            if result:
                results.append(result)
                self._stats.total_pages += 1
                
                if result.error is None:
                    for link in result.links:
                        link_url = link["url"]
                        
                        if (
                            link_url not in self._visited
                            and self._url_filter.is_allowed(link_url)
                            and (not self.config.crawler.respect_robots_txt or self._robots.is_allowed(link_url))
                            and link["type"] == "internal"
                        ):
                            self._pending.append((link_url, current_depth + 1))
        
        self._stats.end_time = datetime.now()
        self._stats.duration_seconds = (
            self._stats.end_time - self._stats.start_time
        ).total_seconds()
        
        logger.info(f"Crawl completed: {self._stats.successful_pages} success, "
                   f"{self._stats.failed_pages} failed, "
                   f"{self._stats.duration_seconds:.2f}s")
        
        return {
            "results": [self._result_to_dict(r) for r in results],
            "graph": self._graph,
            "stats": self._stats.__dict__,
        }
    
    async def _login(self, login_data: dict) -> bool:
        """
        Perform login before crawling.
        
        Args:
            login_data: Dictionary with login credentials.
            
        Returns:
            True if login successful, False otherwise.
        """
        url = login_data.get("url")
        username = login_data.get("username")
        password = login_data.get("password")
        
        if not all([url, username, password]):
            logger.error("Login data missing required fields")
            return False
        
        try:
            page = await self._context.new_page()
            
            await page.goto(url, wait_until="networkidle")
            
            username_selectors = self.config.login.wait_for_selectors[:2]
            password_selectors = self.config.login.wait_for_selectors[2:]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = selector
                    await page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue
            
            if not username_field:
                for selector in ["input[name='username']", "#username", "#email"]:
                    try:
                        await page.wait_for_selector(selector, timeout=2000)
                        username_field = selector
                        break
                    except:
                        continue
            
            for selector in password_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    break
                except:
                    continue
            
            username_field = login_data.get("username_field", username_field or "input[name='username']")
            password_field = login_data.get("password_field", "#password")
            submit_button = login_data.get("submit_button", "button[type='submit']")
            
            await page.fill(username_field, username)
            await page.fill(password_field, password)
            await page.click(submit_button)
            
            await asyncio.sleep(self.config.login.post_login_wait / 1000)
            
            logger.info("Login completed successfully")
            await page.close()
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def login_with_cookies(self, url: str, cookies: List[Dict]) -> bool:
        """
        Set cookies for authenticated crawling.
        
        Args:
            url: URL to set cookies for.
            cookies: List of cookie dictionaries.
            
        Returns:
            True if cookies set successfully.
        """
        try:
            await self._context.add_cookies(cookies)
            logger.info(f"Added {len(cookies)} cookies for authenticated access")
            return True
        except Exception as e:
            logger.error(f"Failed to set cookies: {e}")
            return False
    
    def _result_to_dict(self, result: CrawlResult) -> Dict[str, Any]:
        """Convert CrawlResult to dictionary."""
        return {
            "url": result.url,
            "status_code": result.status_code,
            "title": result.title,
            "links_count": len(result.links),
            "resources_count": len(result.resources),
            "depth": result.depth,
            "crawled_at": result.crawled_at.isoformat(),
            "error": result.error,
        }
    
    def get_graph(self) -> Dict[str, List[str]]:
        """
        Get the crawl graph.
        
        Returns:
            Dictionary mapping URLs to their linked URLs.
        """
        return self._graph
    
    def get_stats(self) -> CrawlStats:
        """
        Get crawl statistics.
        
        Returns:
            CrawlStats object.
        """
        return self._stats


# Backwards compatibility alias
Crawler = WebsiteCrawler
