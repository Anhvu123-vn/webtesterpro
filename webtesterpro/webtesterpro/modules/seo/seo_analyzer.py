"""
SEO Analyzer Module

Provides comprehensive SEO analysis using Playwright:
- Title and meta tags validation
- Heading structure (H1-H6)
- Open Graph and Schema.org markup
- Image optimization checks
- Link analysis (internal/external)
- Page speed metrics
- Keyword density analysis (optional)
"""

import asyncio
import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from bs4 import BeautifulSoup
from playwright.async_api import BrowserContext, Page
from playwright.async_api import TimeoutError as PlaywrightTimeout

from webtesterpro.core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class SEOIssue:
    """
    Represents a single SEO issue.
    """
    category: str
    title: str
    description: str
    impact: str  # "high", "medium", "low"
    element: str = ""
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "element": self.element[:200] if self.element else "",
            "recommendation": self.recommendation,
        }


@dataclass
class SEOScore:
    """
    SEO scores for different categories.
    """
    overall: int = 0
    title: int = 0
    meta_tags: int = 0
    headings: int = 0
    content: int = 0
    images: int = 0
    links: int = 0
    technical: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall": self.overall,
            "title": self.title,
            "meta_tags": self.meta_tags,
            "headings": self.headings,
            "content": self.content,
            "images": self.images,
            "links": self.links,
            "technical": self.technical,
        }


@dataclass
class SEOReport:
    """
    Complete SEO analysis report.
    """
    url: str
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[SEOIssue] = field(default_factory=list)
    
    # Page info
    page_title: str = ""
    meta_description: str = ""
    meta_keywords: str = ""
    
    # Headings
    h1_tags: List[str] = field(default_factory=list)
    h2_tags: List[str] = field(default_factory=list)
    h3_tags: List[str] = field(default_factory=list)
    h4_tags: List[str] = field(default_factory=list)
    h5_tags: List[str] = field(default_factory=list)
    h6_tags: List[str] = field(default_factory=list)
    
    # Social tags
    og_tags: Dict[str, str] = field(default_factory=dict)
    twitter_tags: Dict[str, str] = field(default_factory=dict)
    
    # Schema.org
    schemas: List[str] = field(default_factory=list)
    
    # Links
    internal_links: int = 0
    external_links: int = 0
    total_links: int = 0
    
    # Images
    total_images: int = 0
    images_with_alt: int = 0
    images_without_alt: int = 0
    
    # Technical
    canonical_url: str = ""
    robots_meta: str = ""
    viewport_meta: str = ""
    charset: str = ""
    
    # Content
    word_count: int = 0
    content_text: str = ""
    keyword_density: Dict[str, float] = field(default_factory=dict)
    
    # Scores
    scores: SEOScore = field(default_factory=SEOScore)
    
    # Scan metadata
    scan_duration: float = 0.0
    
    # Issues by category
    high_impact_issues: int = 0
    medium_impact_issues: int = 0
    low_impact_issues: int = 0
    
    def get_issue_count(self) -> int:
        """Get total issue count."""
        return len(self.issues)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "scores": self.scores.to_dict(),
            "summary": {
                "total_issues": self.get_issue_count(),
                "high_impact": self.high_impact_issues,
                "medium_impact": self.medium_impact_issues,
                "low_impact": self.low_impact_issues,
                "word_count": self.word_count,
            },
            "page_info": {
                "title": self.page_title[:200] if self.page_title else "",
                "meta_description": self.meta_description[:300] if self.meta_description else "",
                "meta_keywords": self.meta_keywords[:200] if self.meta_keywords else "",
            },
            "headings": {
                "h1": self.h1_tags,
                "h2": self.h2_tags[:10],
                "h3": self.h3_tags[:10],
                "total_h1": len(self.h1_tags),
                "total_h2": len(self.h2_tags),
                "total_h3": len(self.h3_tags),
            },
            "social": {
                "open_graph": self.og_tags,
                "twitter": self.twitter_tags,
            },
            "schema": {
                "types": self.schemas,
                "count": len(self.schemas),
            },
            "links": {
                "total": self.total_links,
                "internal": self.internal_links,
                "external": self.external_links,
            },
            "images": {
                "total": self.total_images,
                "with_alt": self.images_with_alt,
                "without_alt": self.images_without_alt,
            },
            "technical": {
                "canonical_url": self.canonical_url,
                "robots_meta": self.robots_meta,
                "viewport": self.viewport_meta,
                "charset": self.charset,
            },
            "content": {
                "word_count": self.word_count,
                "keyword_density": {k: round(v, 2) for k, v in self.keyword_density.items()},
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": {
                "scan_duration_seconds": round(self.scan_duration, 2),
            },
        }


class SEOAnalyzer:
    """
    Async SEO analyzer using Playwright.
    
    Performs comprehensive SEO analysis including:
    - Title tag optimization
    - Meta description analysis
    - Heading structure validation
    - Open Graph and Twitter Card tags
    - Schema.org structured data
    - Image optimization
    - Internal and external links
    - Technical SEO factors
    
    Usage:
        async with WebTesterEngine() as engine:
            analyzer = SEOAnalyzer()
            analyzer.set_context(engine._context)
            report = await analyzer.analyze("https://example.com")
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize the SEO analyzer.
        
        Args:
            config: Configuration object.
        """
        self.config = config
        self._context: Optional[BrowserContext] = None
        self._report: Optional[SEOReport] = None
    
    def set_context(self, context: BrowserContext) -> None:
        """
        Set the Playwright browser context.
        
        Args:
            context: Browser context to use.
        """
        self._context = context
    
    def _calculate_scores(self, report: SEOReport) -> SEOScore:
        """Calculate SEO scores based on analysis."""
        scores = SEOScore()
        
        # Title score (0-100)
        title_len = len(report.page_title)
        if not report.page_title:
            scores.title = 0
        elif title_len < 30:
            scores.title = 50
        elif title_len > 60:
            scores.title = 60
        else:
            scores.title = 100
            # Bonus for optimal length
            if 50 <= title_len <= 60:
                scores.title = 100
        
        # Meta tags score (0-100)
        meta_score = 100
        if not report.meta_description:
            meta_score -= 50
        elif len(report.meta_description) < 120:
            meta_score -= 25
        elif len(report.meta_description) > 160:
            meta_score -= 25
        scores.meta_tags = max(0, meta_score)
        
        # Headings score (0-100)
        headings_score = 100
        if not report.h1_tags:
            headings_score -= 40
        elif len(report.h1_tags) > 1:
            headings_score -= 30
        if not report.h2_tags:
            headings_score -= 20
        scores.headings = max(0, headings_score)
        
        # Images score (0-100)
        images_score = 100
        if report.total_images > 0:
            alt_ratio = report.images_with_alt / report.total_images
            images_score = int(alt_ratio * 100)
        scores.images = images_score
        
        # Links score (0-100)
        links_score = 100
        if report.total_links == 0:
            links_score = 50
        elif report.internal_links == 0 and report.external_links > 0:
            links_score = 70
        scores.links = links_score
        
        # Content score (0-100)
        content_score = 100
        if report.word_count < 100:
            content_score = 30
        elif report.word_count < 300:
            content_score = 60
        elif report.word_count < 500:
            content_score = 80
        scores.content = content_score
        
        # Technical score (0-100)
        technical_score = 100
        if not report.canonical_url:
            technical_score -= 20
        if not report.viewport_meta:
            technical_score -= 15
        if not report.robots_meta:
            technical_score -= 10
        scores.technical = max(0, technical_score)
        
        # Calculate overall score
        scores.overall = int(
            scores.title * 0.15 +
            scores.meta_tags * 0.15 +
            scores.headings * 0.15 +
            scores.images * 0.15 +
            scores.links * 0.10 +
            scores.content * 0.15 +
            scores.technical * 0.15
        )
        
        return scores
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract text content from HTML."""
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator=" ")
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_keyword_density(self, text: str, min_length: int = 3) -> Dict[str, float]:
        """
        Calculate keyword density in text.
        
        Args:
            text: Text to analyze.
            min_length: Minimum word length to consider.
            
        Returns:
            Dictionary of keywords and their density percentage.
        """
        # Clean text
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Filter short words
        words = [w for w in words if len(w) >= min_length]
        
        if not words:
            return {}
        
        # Count words
        word_counts = Counter(words)
        total_words = len(words)
        
        # Calculate density
        density = {
            word: round((count / total_words) * 100, 2)
            for word, count in word_counts.most_common(20)
        }
        
        return density
    
    def _extract_og_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Open Graph meta tags."""
        og_tags = {}
        
        for tag in soup.find_all("meta", property=True):
            prop = tag.get("property", "")
            if prop.startswith("og:"):
                og_tags[prop] = tag.get("content", "")
        
        return og_tags
    
    def _extract_twitter_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Twitter Card meta tags."""
        twitter_tags = {}
        
        for tag in soup.find_all("meta", attrs={"name": True}):
            name = tag.get("name", "")
            if name.startswith("twitter:"):
                twitter_tags[name] = tag.get("content", "")
        
        return twitter_tags
    
    def _extract_schemas(self, soup: BeautifulSoup) -> List[str]:
        """Extract Schema.org structured data types."""
        schemas = []
        
        for tag in soup.find_all("script", type="application/ld+json"):
            try:
                # Try to parse as JSON
                from json import loads as json_loads
                content = tag.string
                if content:
                    data = json_loads(content)
                    if isinstance(data, dict):
                        if "@type" in data:
                            schemas.append(data["@type"])
                        if "@graph" in data:
                            for item in data["@graph"]:
                                if isinstance(item, dict) and "@type" in item:
                                    schemas.append(item["@type"])
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "@type" in item:
                                schemas.append(item["@type"])
            except Exception:
                pass
        
        return list(set(schemas))
    
    async def _analyze_page_structure(self, page: Page, html: str) -> SEOReport:
        """Analyze the page structure and extract SEO elements."""
        report = SEOReport(url=page.url)
        soup = BeautifulSoup(html, "lxml")
        
        # Extract title
        title_tag = soup.find("title")
        if title_tag:
            report.page_title = title_tag.get_text(strip=True)
        
        # Extract meta tags
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            report.meta_description = meta_desc.get("content", "")
        
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            report.meta_keywords = meta_keywords.get("content", "")
        
        # Extract headings
        for h1 in soup.find_all("h1"):
            text = h1.get_text(strip=True)
            if text:
                report.h1_tags.append(text[:200])
        
        for h2 in soup.find_all("h2"):
            text = h2.get_text(strip=True)
            if text:
                report.h2_tags.append(text[:200])
        
        for h3 in soup.find_all("h3"):
            text = h3.get_text(strip=True)
            if text:
                report.h3_tags.append(text[:200])
        
        for h4 in soup.find_all("h4"):
            text = h4.get_text(strip=True)
            if text:
                report.h4_tags.append(text[:200])
        
        for h5 in soup.find_all("h5"):
            text = h5.get_text(strip=True)
            if text:
                report.h5_tags.append(text[:200])
        
        for h6 in soup.find_all("h6"):
            text = h6.get_text(strip=True)
            if text:
                report.h6_tags.append(text[:200])
        
        # Extract canonical URL
        canonical = soup.find("link", rel="canonical")
        if canonical:
            report.canonical_url = canonical.get("href", "")
        
        # Extract robots meta
        robots = soup.find("meta", attrs={"name": "robots"})
        if robots:
            report.robots_meta = robots.get("content", "")
        
        # Extract viewport
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if viewport:
            report.viewport_meta = viewport.get("content", "")
        
        # Extract charset
        charset = soup.find("meta", charset=True)
        if charset:
            report.charset = charset.get("charset", "")
        
        # Extract Open Graph tags
        report.og_tags = self._extract_og_tags(soup)
        
        # Extract Twitter tags
        report.twitter_tags = self._extract_twitter_tags(soup)
        
        # Extract Schema.org
        report.schemas = self._extract_schemas(soup)
        
        # Extract images
        images = soup.find_all("img")
        report.total_images = len(images)
        
        for img in images:
            alt = img.get("alt", "")
            if alt:
                report.images_with_alt += 1
            else:
                report.images_without_alt += 1
                src = img.get("src", "")
                if src:
                    report.issues.append(SEOIssue(
                        category="Images",
                        title="Image missing alt attribute",
                        description="Images should have descriptive alt text",
                        impact="medium",
                        element=f"<img src='{src}'>",
                        recommendation="Add alt attribute to describe the image",
                    ))
        
        # Extract links
        current_domain = ""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(page.url)
            current_domain = parsed.netloc
        except Exception:
            pass
        
        links = soup.find_all("a", href=True)
        report.total_links = len(links)
        
        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True)
            
            if href.startswith("http"):
                try:
                    link_parsed = urlparse(href)
                    if link_parsed.netloc == current_domain:
                        report.internal_links += 1
                    else:
                        report.external_links += 1
                except Exception:
                    report.external_links += 1
            elif href.startswith("/") or href.startswith("#"):
                report.internal_links += 1
        
        # Extract content
        report.content_text = self._extract_text_content(soup)
        report.word_count = len(report.content_text.split())
        
        # Calculate keyword density
        report.keyword_density = self._calculate_keyword_density(report.content_text)
        
        return report
    
    def _check_title_issues(self, report: SEOReport) -> List[SEOIssue]:
        """Check for title-related issues."""
        issues = []
        
        if not report.page_title:
            issues.append(SEOIssue(
                category="Title",
                title="Missing title tag",
                description="Page is missing a title tag",
                impact="high",
                recommendation="Add a descriptive title tag between 50-60 characters",
            ))
        else:
            title_len = len(report.page_title)
            
            if title_len < 30:
                issues.append(SEOIssue(
                    category="Title",
                    title="Title too short",
                    description=f"Title is only {title_len} characters (recommended: 50-60)",
                    impact="medium",
                    element=report.page_title,
                    recommendation="Expand the title to include more descriptive keywords",
                ))
            elif title_len > 60:
                issues.append(SEOIssue(
                    category="Title",
                    title="Title too long",
                    description=f"Title is {title_len} characters (may be truncated in search results)",
                    impact="medium",
                    element=report.page_title[:70],
                    recommendation="Shorten the title to 50-60 characters",
                ))
        
        return issues
    
    def _check_meta_issues(self, report: SEOReport) -> List[SEOIssue]:
        """Check for meta tag issues."""
        issues = []
        
        if not report.meta_description:
            issues.append(SEOIssue(
                category="Meta Tags",
                title="Missing meta description",
                description="Page is missing a meta description",
                impact="high",
                recommendation="Add a compelling meta description between 150-160 characters",
            ))
        else:
            desc_len = len(report.meta_description)
            
            if desc_len < 120:
                issues.append(SEOIssue(
                    category="Meta Tags",
                    title="Meta description too short",
                    description=f"Meta description is only {desc_len} characters",
                    impact="medium",
                    element=report.meta_description[:100],
                    recommendation="Expand the meta description to 150-160 characters",
                ))
            elif desc_len > 160:
                issues.append(SEOIssue(
                    category="Meta Tags",
                    title="Meta description too long",
                    description=f"Meta description is {desc_len} characters (may be truncated)",
                    impact="low",
                    element=report.meta_description[:160],
                    recommendation="Shorten the meta description to 150-160 characters",
                ))
        
        return issues
    
    def _check_heading_issues(self, report: SEOReport) -> List[SEOIssue]:
        """Check for heading structure issues."""
        issues = []
        
        if not report.h1_tags:
            issues.append(SEOIssue(
                category="Headings",
                title="Missing H1 tag",
                description="Page has no H1 heading",
                impact="high",
                recommendation="Add a single H1 heading that describes the page content",
            ))
        elif len(report.h1_tags) > 1:
            issues.append(SEOIssue(
                category="Headings",
                title="Multiple H1 tags",
                description=f"Page has {len(report.h1_tags)} H1 tags (should have only one)",
                impact="medium",
                element="Multiple H1 tags found",
                recommendation="Use only one H1 tag per page",
            ))
        
        if not report.h2_tags:
            issues.append(SEOIssue(
                category="Headings",
                title="No H2 subheadings",
                description="Page has no H2 subheadings",
                impact="low",
                recommendation="Add H2 subheadings to improve content structure",
            ))
        
        return issues
    
    def _check_social_issues(self, report: SEOReport) -> List[SEOIssue]:
        """Check for social media tag issues."""
        issues = []
        
        # Open Graph
        if not report.og_tags:
            issues.append(SEOIssue(
                category="Social Tags",
                title="Missing Open Graph tags",
                description="Page has no Open Graph meta tags",
                impact="medium",
                recommendation="Add og:title, og:description, og:image, og:url tags",
            ))
        else:
            required_og = ["og:title", "og:description", "og:image", "og:url"]
            for tag in required_og:
                if tag not in report.og_tags:
                    issues.append(SEOIssue(
                        category="Social Tags",
                        title=f"Missing {tag}",
                        description=f"Open Graph {tag} is missing",
                        impact="low",
                        recommendation=f"Add {tag} tag for better social sharing",
                    ))
        
        # Twitter Card
        if not report.twitter_tags:
            issues.append(SEOIssue(
                category="Social Tags",
                title="Missing Twitter Card tags",
                description="Page has no Twitter Card meta tags",
                impact="low",
                recommendation="Add twitter:card and twitter:title tags",
            ))
        
        return issues
    
    def _check_schema_issues(self, report: SEOReport) -> List[SEOIssue]:
        """Check for Schema.org issues."""
        issues = []
        
        if not report.schemas:
            issues.append(SEOIssue(
                category="Structured Data",
                title="No Schema.org structured data",
                description="Page has no JSON-LD structured data",
                impact="medium",
                recommendation="Add relevant Schema.org markup for rich search results",
            ))
        
        return issues
    
    def _check_canonical_issues(self, report: SEOReport) -> List[SEOIssue]:
        """Check for canonical URL issues."""
        issues = []
        
        if not report.canonical_url:
            issues.append(SEOIssue(
                category="Technical SEO",
                title="Missing canonical URL",
                description="Page has no canonical URL specified",
                impact="medium",
                recommendation="Add a canonical tag to prevent duplicate content issues",
            ))
        
        return issues
    
    async def analyze(
        self,
        url: str,
        check_keyword_density: bool = False,
    ) -> Dict[str, Any]:
        """
        Perform SEO analysis on a URL.
        
        Args:
            url: URL to analyze.
            check_keyword_density: Include keyword density analysis.
            
        Returns:
            Dictionary containing SEO analysis results.
        """
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            page = await self._context.new_page()
            
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.config.scanner.timeout if self.config else 30000,
            )
            
            html = await page.content()
            
            # Analyze page structure
            report = await self._analyze_page_structure(page, html)
            
            # Run issue checks
            report.issues.extend(self._check_title_issues(report))
            report.issues.extend(self._check_meta_issues(report))
            report.issues.extend(self._check_heading_issues(report))
            report.issues.extend(self._check_social_issues(report))
            report.issues.extend(self._check_schema_issues(report))
            report.issues.extend(self._check_canonical_issues(report))
            
            # Update impact counts
            for issue in report.issues:
                if issue.impact == "high":
                    report.high_impact_issues += 1
                elif issue.impact == "medium":
                    report.medium_impact_issues += 1
                else:
                    report.low_impact_issues += 1
            
            # Calculate scores
            report.scores = self._calculate_scores(report)
            
            # Calculate scan duration
            report.scan_duration = asyncio.get_event_loop().time() - start_time
            
            await page.close()
            
            logger.info(f"SEO analysis completed for {url}")
            logger.info(f"Found {len(report.issues)} issues, score: {report.scores.overall}")
            
            return report.to_dict()
            
        except PlaywrightTimeout:
            logger.error(f"Timeout during SEO analysis: {url}")
            return {"error": "Timeout during analysis", "url": url}
            
        except Exception as e:
            logger.error(f"Error during SEO analysis: {e}")
            return {"error": str(e), "url": url}
    
    async def quick_analyze(self, url: str) -> Dict[str, Any]:
        """
        Perform a quick SEO analysis (basic checks only).
        
        Args:
            url: URL to analyze.
            
        Returns:
            Dictionary containing quick analysis results.
        """
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        try:
            page = await self._context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=10000)
            
            html = await page.content()
            soup = BeautifulSoup(html, "lxml")
            
            # Basic checks only
            title = soup.find("title")
            meta_desc = soup.find("meta", attrs={"name": "description"})
            h1_count = len(soup.find_all("h1"))
            img_count = len(soup.find_all("img"))
            img_no_alt = len(soup.find_all("img", alt=False)) + len(soup.find_all("img", alt=""))
            
            result = {
                "url": url,
                "title": title.get_text(strip=True) if title else None,
                "title_length": len(title.get_text(strip=True)) if title else 0,
                "has_meta_description": meta_desc is not None,
                "meta_description_length": len(meta_desc.get("content", "")) if meta_desc else 0,
                "h1_count": h1_count,
                "total_images": img_count,
                "images_without_alt": img_no_alt,
                "quick_score": self._calculate_quick_score(
                    title, meta_desc, h1_count, img_no_alt, img_count
                ),
            }
            
            await page.close()
            return result
            
        except Exception as e:
            return {"error": str(e), "url": url}
    
    def _calculate_quick_score(
        self,
        title,
        meta_desc,
        h1_count,
        img_no_alt,
        total_images,
    ) -> int:
        """Calculate a quick SEO score."""
        score = 100
        
        if not title:
            score -= 30
        elif len(title.get_text(strip=True)) < 30:
            score -= 15
        
        if not meta_desc:
            score -= 20
        
        if h1_count == 0:
            score -= 15
        elif h1_count > 1:
            score -= 10
        
        if total_images > 0:
            alt_ratio = 1 - (img_no_alt / total_images)
            score -= int((1 - alt_ratio) * 20)
        
        return max(0, score)


# Alias for backwards compatibility
SEOTest = SEOAnalyzer
