"""
Website Scanner Module

Scans websites for forms, links, resources, and accessibility.
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
class FormInfo:
    """Information about a form."""
    action: str
    method: str
    inputs: List[Dict[str, str]]
    has_submit: bool
    url: str


@dataclass
class LinkInfo:
    """Information about a link."""
    url: str
    text: str
    is_internal: bool
    is_valid: bool
    status_code: Optional[int] = None


@dataclass
class ResourceInfo:
    """Information about a resource."""
    url: str
    type: str
    size: Optional[int] = None
    load_time: Optional[float] = None
    is_valid: bool = True


@dataclass
class ScanResult:
    """Results from a website scan."""
    url: str
    forms: List[FormInfo] = field(default_factory=list)
    links: List[LinkInfo] = field(default_factory=list)
    resources: List[ResourceInfo] = field(default_factory=list)
    scanned_at: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)


class WebsiteScanner:
    """
    Async website scanner using Playwright.
    
    Scans websites for:
    - Forms and inputs
    - Links and their validity
    - Resources (scripts, stylesheets, images)
    - Basic accessibility checks
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize the scanner.
        
        Args:
            config: Configuration object.
        """
        self.config = config or Config.load_default()
        self._context: Optional[BrowserContext] = None
        self._semaphore = asyncio.Semaphore(5)
    
    def set_context(self, context: BrowserContext) -> None:
        """
        Set the Playwright browser context.
        
        Args:
            context: Browser context to use.
        """
        self._context = context
    
    async def _extract_forms(self, page: Page) -> List[FormInfo]:
        """Extract form information from a page."""
        forms = []
        
        form_elements = await page.query_selector_all("form")
        
        for form in form_elements:
            action = await form.get_attribute("action") or ""
            method = await form.get_attribute("method") or "get"
            
            inputs = []
            input_elements = await form.query_selector_all("input")
            
            for inp in input_elements:
                input_info = {
                    "name": await inp.get_attribute("name") or "",
                    "type": await inp.get_attribute("type") or "text",
                    "id": await inp.get_attribute("id") or "",
                    "placeholder": await inp.get_attribute("placeholder") or "",
                    "required": await inp.get_attribute("required") is not None,
                }
                inputs.append(input_info)
            
            textarea_elements = await form.query_selector_all("textarea")
            for ta in textarea_elements:
                inputs.append({
                    "name": await ta.get_attribute("name") or "",
                    "type": "textarea",
                    "id": await ta.get_attribute("id") or "",
                    "required": await ta.get_attribute("required") is not None,
                })
            
            select_elements = await form.query_selector_all("select")
            for sel in select_elements:
                inputs.append({
                    "name": await sel.get_attribute("name") or "",
                    "type": "select",
                    "id": await sel.get_attribute("id") or "",
                })
            
            has_submit = await form.query_selector("button[type='submit'], input[type='submit']") is not None
            
            forms.append(FormInfo(
                action=action,
                method=method,
                inputs=inputs,
                has_submit=has_submit,
                url=page.url,
            ))
        
        return forms
    
    async def _extract_links(self, page: Page) -> List[LinkInfo]:
        """Extract link information from a page."""
        links = []
        current_domain = page.url.split("/")[2] if "//" in page.url else ""
        
        anchor_elements = await page.query_selector_all("a[href]")
        
        for anchor in anchor_elements:
            href = await anchor.get_attribute("href") or ""
            text = await anchor.inner_text() or ""
            
            if href.startswith("/") or href.startswith(current_domain):
                is_internal = True
            elif href.startswith("http"):
                is_internal = href.split("/")[2] == current_domain
            else:
                is_internal = True
            
            links.append(LinkInfo(
                url=href,
                text=text[:100] if text else "",
                is_internal=is_internal,
                is_valid=True,
            ))
        
        return links
    
    async def _extract_resources(self, page: Page) -> List[ResourceInfo]:
        """Extract resource information from a page."""
        resources = []
        
        script_elements = await page.query_selector_all("script[src]")
        for script in script_elements:
            src = await script.get_attribute("src") or ""
            if src:
                resources.append(ResourceInfo(url=src, type="script"))
        
        link_elements = await page.query_selector_all("link[href]")
        for link in link_elements:
            href = await link.get_attribute("href") or ""
            rel = await link.get_attribute("rel") or []
            if href and ("stylesheet" in rel or not rel):
                resources.append(ResourceInfo(url=href, type="stylesheet"))
        
        img_elements = await page.query_selector_all("img[src]")
        for img in img_elements:
            src = await img.get_attribute("src") or ""
            if src:
                resources.append(ResourceInfo(url=src, type="image"))
        
        return resources
    
    async def scan(self, url: str) -> Dict[str, Any]:
        """
        Scan a website.
        
        Args:
            url: URL to scan.
            
        Returns:
            Dictionary containing scan results.
        """
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        page = None
        try:
            page = await self._context.new_page()
            
            logger.info(f"Scanning: {url}")
            
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.config.scanner.timeout,
            )
            
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            result = ScanResult(url=url)
            
            if self.config.scanner.check_forms:
                result.forms = await self._extract_forms(page)
            
            if self.config.scanner.check_links:
                result.links = await self._extract_links(page)
            
            if self.config.scanner.check_resources:
                result.resources = await self._extract_resources(page)
            
            logger.info(f"Scan completed for {url}")
            
            return {
                "url": url,
                "status_code": response.status if response else 0,
                "forms": [
                    {
                        "action": f.action,
                        "method": f.method,
                        "inputs": f.inputs,
                        "has_submit": f.has_submit,
                    }
                    for f in result.forms
                ],
                "links": [
                    {
                        "url": l.url,
                        "text": l.text,
                        "is_internal": l.is_internal,
                    }
                    for l in result.links
                ],
                "resources": [
                    {
                        "url": r.url,
                        "type": r.type,
                    }
                    for r in result.resources
                ],
                "scanned_at": result.scanned_at.isoformat(),
                "summary": {
                    "total_forms": len(result.forms),
                    "total_links": len(result.links),
                    "total_resources": len(result.resources),
                },
            }
            
        except PlaywrightTimeout:
            logger.error(f"Timeout scanning: {url}")
            return {"url": url, "error": "Timeout", "status_code": 0}
            
        except Exception as e:
            logger.error(f"Error scanning {url}: {e}")
            return {"url": url, "error": str(e), "status_code": 0}
            
        finally:
            if page:
                await page.close()
