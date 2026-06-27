"""
Website Analyzer Module

Analyzes websites for SEO, performance, and security.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

from webtesterpro.core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class SEOAnalysis:
    """SEO analysis results."""
    title: str = ""
    meta_description: str = ""
    h1_tags: List[str] = field(default_factory=list)
    h2_tags: List[str] = field(default_factory=list)
    canonical_url: str = ""
    og_tags: Dict[str, str] = field(default_factory=dict)
    twitter_tags: Dict[str, str] = field(default_factory=dict)
    images_without_alt: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


@dataclass
class PerformanceAnalysis:
    """Performance analysis results."""
    load_time: float = 0.0
    dom_size: int = 0
    resource_count: int = 0
    total_resource_size: int = 0
    issues: List[str] = field(default_factory=list)


@dataclass
class SecurityAnalysis:
    """Security analysis results."""
    has_https: bool = False
    security_headers: Dict[str, str] = field(default_factory=dict)
    mixed_content: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis results."""
    url: str
    seo: SEOAnalysis = field(default_factory=SEOAnalysis)
    performance: PerformanceAnalysis = field(default_factory=PerformanceAnalysis)
    security: SecurityAnalysis = field(default_factory=SecurityAnalysis)
    analyzed_at: datetime = field(default_factory=datetime.now)


class WebsiteAnalyzer:
    """
    Async website analyzer using Playwright.
    
    Analyzes websites for:
    - SEO best practices
    - Performance metrics
    - Security headers and issues
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize the analyzer.
        
        Args:
            config: Configuration object.
        """
        self.config = config or Config.load_default()
        self._context: Optional[BrowserContext] = None
    
    def set_context(self, context: BrowserContext) -> None:
        """
        Set the Playwright browser context.
        
        Args:
            context: Browser context to use.
        """
        self._context = context
    
    async def _analyze_seo(self, page: Page, html: str) -> SEOAnalysis:
        """Analyze SEO aspects of a page."""
        soup = BeautifulSoup(html, "lxml")
        analysis = SEOAnalysis()
        
        title_tag = soup.find("title")
        analysis.title = title_tag.get_text(strip=True) if title_tag else ""
        
        meta_desc = soup.find("meta", attrs={"name": "description"})
        analysis.meta_description = meta_desc.get("content", "") if meta_desc else ""
        
        for h1 in soup.find_all("h1"):
            text = h1.get_text(strip=True)
            if text:
                analysis.h1_tags.append(text)
        
        for h2 in soup.find_all("h2"):
            text = h2.get_text(strip=True)
            if text:
                analysis.h2_tags.append(text)
        
        canonical = soup.find("link", attrs={"rel": "canonical"})
        analysis.canonical_url = canonical.get("href", "") if canonical else ""
        
        for tag in soup.find_all("meta", attrs={"property": lambda x: x and x.startswith("og:")}):
            prop = tag.get("property", "").replace("og:", "")
            content = tag.get("content", "")
            if prop and content:
                analysis.og_tags[prop] = content
        
        for tag in soup.find_all("meta", attrs={"name": lambda x: x and x.startswith("twitter:")}):
            name = tag.get("name", "").replace("twitter:", "")
            content = tag.get("content", "")
            if name and content:
                analysis.twitter_tags[name] = content
        
        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = img.get("alt", "")
            if src and not alt:
                analysis.images_without_alt.append(src)
        
        if not analysis.title:
            analysis.issues.append("Missing title tag")
        elif len(analysis.title) < 30:
            analysis.issues.append("Title tag too short (< 30 characters)")
        elif len(analysis.title) > 60:
            analysis.issues.append("Title tag too long (> 60 characters)")
        
        if not analysis.meta_description:
            analysis.issues.append("Missing meta description")
        elif len(analysis.meta_description) < 120:
            analysis.issues.append("Meta description too short (< 120 characters)")
        
        if len(analysis.h1_tags) == 0:
            analysis.issues.append("Missing H1 tag")
        elif len(analysis.h1_tags) > 1:
            analysis.issues.append(f"Multiple H1 tags found ({len(analysis.h1_tags)})")
        
        if analysis.images_without_alt:
            analysis.issues.append(f"{len(analysis.images_without_alt)} images without alt text")
        
        return analysis
    
    async def _analyze_performance(self, page: Page, html: str) -> PerformanceAnalysis:
        """Analyze performance aspects of a page."""
        soup = BeautifulSoup(html, "lxml")
        analysis = PerformanceAnalysis()
        
        analysis.resource_count = len(soup.find_all(["script", "link", "img"]))
        
        body = soup.find("body")
        if body:
            analysis.dom_size = len(str(body))
        
        if len(analysis.h1_tags) == 0:
            analysis.issues.append("Empty page or no body content")
        
        if analysis.resource_count > 50:
            analysis.issues.append(f"High resource count ({analysis.resource_count})")
        
        return analysis
    
    async def _analyze_security(self, page: Page) -> SecurityAnalysis:
        """Analyze security aspects of a page."""
        analysis = SecurityAnalysis()
        
        analysis.has_https = page.url.startswith("https://")
        
        try:
            response = await page.request.get(page.url)
            headers = dict(response.headers)
            
            security_header_names = [
                "content-security-policy",
                "strict-transport-security",
                "x-content-type-options",
                "x-frame-options",
                "x-xss-protection",
                "referrer-policy",
                "permissions-policy",
            ]
            
            for header_name in security_header_names:
                for actual_header, value in headers.items():
                    if actual_header.lower().replace("-", "") == header_name.replace("-", ""):
                        analysis.security_headers[header_name] = value
                        break
            
        except Exception as e:
            logger.debug(f"Could not fetch security headers: {e}")
        
        if not analysis.has_https:
            analysis.issues.append("Website not using HTTPS")
        
        if "strict-transport-security" not in analysis.security_headers:
            analysis.issues.append("Missing HSTS header")
        
        if "x-content-type-options" not in analysis.security_headers:
            analysis.issues.append("Missing X-Content-Type-Options header")
        
        if "x-frame-options" not in analysis.security_headers:
            analysis.issues.append("Missing X-Frame-Options header")
        
        return analysis
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """
        Analyze a website.
        
        Args:
            url: URL to analyze.
            
        Returns:
            Dictionary containing analysis results.
        """
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        page = None
        try:
            page = await self._context.new_page()
            
            logger.info(f"Analyzing: {url}")
            
            start_time = asyncio.get_event_loop().time()
            
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.config.scanner.timeout,
            )
            
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            load_time = asyncio.get_event_loop().time() - start_time
            html = await page.content()
            
            result = AnalysisResult(url=url)
            
            if self.config.analyzer.check_seo:
                result.seo = await self._analyze_seo(page, html)
            
            if self.config.analyzer.check_performance:
                result.performance = await self._analyze_performance(page, html)
                result.performance.load_time = load_time
            
            if self.config.analyzer.check_security_headers:
                result.security = await self._analyze_security(page)
            
            logger.info(f"Analysis completed for {url}")
            
            return {
                "url": url,
                "status_code": response.status if response else 0,
                "load_time_seconds": round(load_time, 3),
                "seo": {
                    "title": result.seo.title,
                    "meta_description": result.seo.meta_description,
                    "h1_tags": result.seo.h1_tags,
                    "h2_tags": result.seo.h2_tags[:10],
                    "canonical_url": result.seo.canonical_url,
                    "og_tags": result.seo.og_tags,
                    "images_without_alt": result.seo.images_without_alt[:10],
                    "issues": result.seo.issues,
                },
                "performance": {
                    "load_time": result.performance.load_time,
                    "dom_size": result.performance.dom_size,
                    "resource_count": result.performance.resource_count,
                    "issues": result.performance.issues,
                },
                "security": {
                    "has_https": result.security.has_https,
                    "security_headers": result.security.security_headers,
                    "issues": result.security.issues,
                },
                "summary": {
                    "seo_score": max(0, 100 - len(result.seo.issues) * 10),
                    "performance_score": max(0, 100 - len(result.performance.issues) * 15),
                    "security_score": max(0, 100 - len(result.security.issues) * 20),
                    "total_issues": len(result.seo.issues) + len(result.performance.issues) + len(result.security.issues),
                },
                "analyzed_at": result.analyzed_at.isoformat(),
            }
            
        except PlaywrightTimeout:
            logger.error(f"Timeout analyzing: {url}")
            return {"url": url, "error": "Timeout", "status_code": 0}
            
        except Exception as e:
            logger.error(f"Error analyzing {url}: {e}")
            return {"url": url, "error": str(e), "status_code": 0}
            
        finally:
            if page:
                await page.close()
