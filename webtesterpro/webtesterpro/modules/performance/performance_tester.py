"""
Performance Tester Module

Provides comprehensive performance testing using Playwright:
- Core Web Vitals (LCP, FID, CLS, TTFB, FCP)
- Resource metrics (load time, size, request count)
- Threshold-based comparisons
- Detailed results dictionary
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page, Request, Response
from playwright.async_api import TimeoutError as PlaywrightTimeout

from webtesterpro.core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class CoreWebVitals:
    """
    Core Web Vitals metrics.
    
    These are user-centric metrics defined by Google:
    - LCP: Largest Contentful Paint
    - FID/INP: First Input Delay / Interaction to Next Paint
    - CLS: Cumulative Layout Shift
    - TTFB: Time to First Byte
    - FCP: First Contentful Paint
    """
    # Timing metrics (in milliseconds)
    ttfb: float = 0.0          # Time to First Byte
    fcp: float = 0.0           # First Contentful Paint
    lcp: float = 0.0           # Largest Contentful Paint
    fid: float = 0.0           # First Input Delay
    inp: float = 0.0           # Interaction to Next Paint (replaces FID)
    cls: float = 0.0           # Cumulative Layout Shift
    tbt: float = 0.0           # Total Blocking Time
    dom_content_loaded: float = 0.0
    load: float = 0.0           # Page Load
    interactive: float = 0.0   # Time to Interactive
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ttfb_ms": round(self.ttfb, 2),
            "fcp_ms": round(self.fcp, 2),
            "lcp_ms": round(self.lcp, 2),
            "fid_ms": round(self.fid, 2),
            "inp_ms": round(self.inp, 2),
            "cls": round(self.cls, 4),
            "tbt_ms": round(self.tbt, 2),
            "dom_content_loaded_ms": round(self.dom_content_loaded, 2),
            "load_ms": round(self.load, 2),
            "interactive_ms": round(self.interactive, 2),
        }
    
    def get_score(self, thresholds: Dict[str, float]) -> Dict[str, str]:
        """
        Get score based on thresholds.
        
        Args:
            thresholds: Dict with metric names and threshold values.
            
        Returns:
            Dict with scores: "good", "needs_improvement", "poor"
        """
        scores = {}
        
        def check_metric(value: float, poor_threshold: float, needs_improvement_threshold: float) -> str:
            if value <= needs_improvement_threshold:
                return "good"
            elif value <= poor_threshold:
                return "needs_improvement"
            else:
                return "poor"
        
        # TTFB: Good < 800ms, Needs Improvement < 1800ms
        if "ttfb" in thresholds:
            scores["ttfb"] = check_metric(self.ttfb, 1800, thresholds.get("ttfb", 800))
        
        # FCP: Good < 1800ms, Needs Improvement < 3000ms
        if "fcp" in thresholds:
            scores["fcp"] = check_metric(self.fcp, 3000, thresholds.get("fcp", 1800))
        
        # LCP: Good < 2500ms, Needs Improvement < 4000ms
        if "lcp" in thresholds:
            scores["lcp"] = check_metric(self.lcp, 4000, thresholds.get("lcp", 2500))
        
        # FID/INP: Good < 100ms, Needs Improvement < 300ms
        if "fid" in thresholds:
            scores["fid"] = check_metric(self.fid, 300, thresholds.get("fid", 100))
        
        # CLS: Good < 0.1, Needs Improvement < 0.25
        if "cls" in thresholds:
            scores["cls"] = check_metric(self.cls, 0.25, thresholds.get("cls", 0.1))
        
        return scores


@dataclass
class ResourceMetrics:
    """
    Metrics about page resources (scripts, stylesheets, images, etc.)
    """
    total_requests: int = 0
    total_size: int = 0
    total_load_time: float = 0.0
    document_size: int = 0
    html_size: int = 0
    
    # Resource counts by type
    scripts_count: int = 0
    stylesheets_count: int = 0
    images_count: int = 0
    fonts_count: int = 0
    xhr_count: int = 0
    fetch_count: int = 0
    other_count: int = 0
    
    # Size by type
    scripts_size: int = 0
    stylesheets_size: int = 0
    images_size: int = 0
    fonts_size: int = 0
    other_size: int = 0
    
    # Failed requests
    failed_requests: int = 0
    blocked_requests: int = 0
    
    resources: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": {
                "total_requests": self.total_requests,
                "total_size_bytes": self.total_size,
                "total_size_kb": round(self.total_size / 1024, 2),
                "total_size_mb": round(self.total_size / (1024 * 1024), 2),
                "total_load_time_ms": round(self.total_load_time, 2),
                "failed_requests": self.failed_requests,
                "blocked_requests": self.blocked_requests,
            },
            "document": {
                "size_bytes": self.document_size,
                "size_kb": round(self.document_size / 1024, 2),
            },
            "html": {
                "size_bytes": self.html_size,
                "size_kb": round(self.html_size / 1024, 2),
            },
            "by_type": {
                "scripts": {"count": self.scripts_count, "size_kb": round(self.scripts_size / 1024, 2)},
                "stylesheets": {"count": self.stylesheets_count, "size_kb": round(self.stylesheets_size / 1024, 2)},
                "images": {"count": self.images_count, "size_kb": round(self.images_size / 1024, 2)},
                "fonts": {"count": self.fonts_count, "size_kb": round(self.fonts_size / 1024, 2)},
                "xhr": {"count": self.xhr_count},
                "fetch": {"count": self.fetch_count},
                "other": {"count": self.other_count, "size_kb": round(self.other_size / 1024, 2)},
            },
            "resources": self.resources[:50],  # Limit to 50 resources
        }


@dataclass
class PerformanceResult:
    """
    Complete performance test result.
    """
    url: str
    timestamp: datetime = field(default_factory=datetime.now)
    web_vitals: CoreWebVitals = field(default_factory=CoreWebVitals)
    resources: ResourceMetrics = field(default_factory=ResourceMetrics)
    
    # Additional metrics
    navigation_type: str = "navigate"
    connection_type: Optional[str] = None
    
    # Score
    overall_score: float = 0.0
    
    # Errors
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "web_vitals": self.web_vitals.to_dict(),
            "resources": self.resources.to_dict(),
            "metadata": {
                "navigation_type": self.navigation_type,
                "connection_type": self.connection_type,
            },
            "scores": {
                "overall": self.overall_score,
            },
            "errors": self.errors,
            "warnings": self.warnings,
        }


class PerformanceTester:
    """
    Async performance tester using Playwright.
    
    Measures:
    - Core Web Vitals (LCP, FID, CLS, TTFB, FCP)
    - Resource loading metrics
    - Custom performance marks and measures
    - Comparison against configurable thresholds
    
    Usage:
        async with WebTesterEngine() as engine:
            tester = PerformanceTester()
            tester.set_context(engine._context)
            results = await tester.test_performance("https://example.com")
    """
    
    # Default thresholds based on Google's Core Web Vitals guidelines
    DEFAULT_THRESHOLDS = {
        "ttfb": 800,           # Good: < 800ms
        "fcp": 1800,           # Good: < 1800ms
        "lcp": 2500,           # Good: < 2500ms
        "fid": 100,            # Good: < 100ms
        "cls": 0.1,            # Good: < 0.1
        "tbt": 200,            # Good: < 200ms
        "load": 3000,          # Good: < 3000ms
        "interactive": 3800,   # Good: < 3800ms
    }
    
    def __init__(self, config: Config = None):
        """
        Initialize the performance tester.
        
        Args:
            config: Configuration object.
        """
        self.config = config
        self._context: Optional[BrowserContext] = None
        self._thresholds: Dict[str, float] = self.DEFAULT_THRESHOLDS.copy()
        self._capture_traces: bool = False
        self._trace_path: Optional[str] = None
    
    def set_context(self, context: BrowserContext) -> None:
        """
        Set the Playwright browser context.
        
        Args:
            context: Browser context to use.
        """
        self._context = context
    
    def set_thresholds(self, thresholds: Dict[str, float]) -> None:
        """
        Set custom thresholds for performance metrics.
        
        Args:
            thresholds: Dict with metric names and threshold values in ms (except CLS).
        """
        self._thresholds.update(thresholds)
        logger.info(f"Updated thresholds: {self._thresholds}")
    
    def enable_tracing(self, trace_path: str) -> None:
        """
        Enable performance tracing.
        
        Args:
            trace_path: Path to save the trace file.
        """
        self._capture_traces = True
        self._trace_path = trace_path
    
    async def _setup_tracing(self, page: Page) -> None:
        """Setup performance tracing on a page."""
        if self._capture_traces and self._trace_path:
            await page.context.tracing.start(
                screenshots=True,
                snapshots=True,
                sources=True,
            )
    
    async def _stop_tracing(self, page: Page) -> Optional[str]:
        """Stop tracing and return the path."""
        if self._capture_traces and self._trace_path:
            await page.context.tracing.stop(path=self._trace_path)
            return self._trace_path
        return None
    
    async def _inject_performance_observer(self, page: Page) -> None:
        """Inject JavaScript to capture performance metrics."""
        js_code = """
        () => {
            return new Promise((resolve) => {
                const metrics = {};
                const observerEntries = [];
                
                // Navigation Timing
                const navigation = performance.getEntriesByType('navigation')[0];
                if (navigation) {
                    metrics.navigation = {
                        ttfb: navigation.responseStart - navigation.requestStart,
                        fcp: 0, // Will be set by Paint Timing API
                        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.requestStart,
                        load: navigation.loadEventEnd - navigation.requestStart,
                        interactive: navigation.domInteractive - navigation.requestStart,
                    };
                    
                    // Calculate TTFB
                    metrics.ttfb = navigation.responseStart - navigation.requestStart;
                }
                
                // Paint Timing
                const paintEntries = performance.getEntriesByType('paint');
                paintEntries.forEach(entry => {
                    if (entry.name === 'first-contentful-paint') {
                        metrics.fcp = entry.startTime;
                    }
                });
                
                // LCP Observer
                let lcpValue = 0;
                const lcpObserver = new PerformanceObserver((entryList) => {
                    const entries = entryList.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    lcpValue = lastEntry.startTime;
                });
                
                try {
                    lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
                } catch (e) {
                    // LCP not supported
                }
                
                // FID Observer
                let fidValue = 0;
                const fidObserver = new PerformanceObserver((entryList) => {
                    const entries = entryList.getEntries();
                    if (entries.length > 0) {
                        fidValue = entries[0].processingStart - entries[0].startTime;
                    }
                });
                
                try {
                    fidObserver.observe({ type: 'first-input', buffered: true });
                } catch (e) {
                    // FID not supported
                }
                
                // CLS Observer
                let clsValue = 0;
                let clsEntries = [];
                const clsObserver = new PerformanceObserver((entryList) => {
                    const entries = entryList.getEntries();
                    entries.forEach(entry => {
                        if (!entry.hadRecentInput) {
                            clsEntries.push(entry);
                        }
                    });
                    
                    // Calculate CLS
                    let sessionValue = 0;
                    let lastEntryTime = 0;
                    
                    clsEntries.forEach(entry => {
                        if (entry.startTime - lastEntryTime > 1000) {
                            sessionValue = 0;
                        }
                        sessionValue += entry.value;
                        lastEntryTime = entry.startTime;
                        clsValue = Math.max(clsValue, sessionValue);
                    });
                });
                
                try {
                    clsObserver.observe({ type: 'layout-shift', buffered: true });
                } catch (e) {
                    // CLS not supported
                }
                
                // TBT Calculation (long tasks)
                let tbtValue = 0;
                const longTaskObserver = new PerformanceObserver((entryList) => {
                    entryList.getEntries().forEach(entry => {
                        if (entry.duration > 50) {
                            tbtValue += entry.duration - 50;
                        }
                    });
                });
                
                try {
                    longTaskObserver.observe({ type: 'longtask', buffered: true });
                } catch (e) {
                    // Long Tasks not supported
                }
                
                // Resource Timing
                const resources = performance.getEntriesByType('resource');
                metrics.resources = resources.map(r => ({
                    name: r.name,
                    type: r.initiatorType,
                    size: r.transferSize || 0,
                    duration: r.duration,
                    ttfb: r.responseStart - r.requestStart,
                }));
                
                // Set timeout to collect final values
                setTimeout(() => {
                    metrics.lcp = lcpValue;
                    metrics.fid = fidValue;
                    metrics.cls = clsValue;
                    metrics.tbt = tbtValue;
                    
                    // Get LCP from entries if not captured
                    const lcpEntries = performance.getEntriesByType('largest-contentful-paint');
                    if (lcpEntries.length > 0 && metrics.lcp === 0) {
                        metrics.lcp = lcpEntries[lcpEntries.length - 1].startTime;
                    }
                    
                    resolve(metrics);
                }, 3000);
            });
        }
        """
        
        return await page.evaluate(js_code)
    
    async def _setup_request_listeners(self, page: Page) -> Dict[str, Any]:
        """Setup listeners to track requests and responses."""
        request_data = {
            "requests": [],
            "responses": [],
            "failed": [],
            "blocked": [],
        }
        
        async def handle_request(request: Request):
            request_data["requests"].append({
                "url": request.url,
                "type": request.resource_type,
                "method": request.method,
                "size": request.sizes.get("requestBody", 0) if hasattr(request, 'sizes') else 0,
            })
            
            # Check if blocked by CSP or ad blocker
            try:
                failure = request.failure
                if failure:
                    request_data["blocked"].append({
                        "url": request.url,
                        "error": failure.get("errorText", "Unknown"),
                    })
            except Exception:
                pass
        
        async def handle_response(response: Response):
            size = 0
            try:
                size = len(await response.body()) if response.status < 400 else 0
            except Exception:
                pass
            
            request_data["responses"].append({
                "url": response.url,
                "status": response.status,
                "type": response.request.resource_type,
                "size": size,
                "headers": dict(response.headers) if hasattr(response, 'headers') else {},
            })
            
            if response.status >= 400:
                request_data["failed"].append({
                    "url": response.url,
                    "status": response.status,
                })
        
        page.on("request", handle_request)
        page.on("response", handle_response)
        
        return request_data
    
    async def _calculate_resource_metrics(
        self,
        page: Page,
        js_metrics: Dict[str, Any],
    ) -> ResourceMetrics:
        """Calculate resource metrics from page."""
        metrics = ResourceMetrics()
        
        # Get resource timing entries
        resource_entries = await page.evaluate("""
            () => {
                const entries = performance.getEntriesByType('resource');
                return entries.map(e => ({
                    name: e.name,
                    type: e.initiatorType,
                    size: e.transferSize || 0,
                    duration: e.duration,
                    ttfb: (e.responseStart - e.requestStart) || 0,
                    dns: (e.domainLookupEnd - e.domainLookupStart) || 0,
                    tcp: (e.connectEnd - e.connectStart) || 0,
                }));
            }
        """)
        
        for entry in resource_entries:
            metrics.total_requests += 1
            metrics.total_size += entry.get("size", 0)
            metrics.total_load_time += entry.get("duration", 0)
            
            resource_info = {
                "url": entry.get("name", ""),
                "type": entry.get("type", ""),
                "size": entry.get("size", 0),
                "duration_ms": round(entry.get("duration", 0), 2),
                "ttfb_ms": round(entry.get("ttfb", 0), 2),
            }
            metrics.resources.append(resource_info)
            
            # Count by type
            resource_type = entry.get("type", "")
            size = entry.get("size", 0)
            
            if resource_type in ("script", "js"):
                metrics.scripts_count += 1
                metrics.scripts_size += size
            elif resource_type == "stylesheet":
                metrics.stylesheets_count += 1
                metrics.stylesheets_size += size
            elif resource_type in ("image", "img"):
                metrics.images_count += 1
                metrics.images_size += size
            elif resource_type in ("font", "woff", "woff2"):
                metrics.fonts_count += 1
                metrics.fonts_size += size
            elif resource_type == "xhr":
                metrics.xhr_count += 1
            elif resource_type == "fetch":
                metrics.fetch_count += 1
            else:
                metrics.other_count += 1
                metrics.other_size += size
        
        # Add JS-injected metrics if available
        if js_metrics and "resources" in js_metrics:
            # Some additional resources might be captured here
            pass
        
        return metrics
    
    async def test_performance(
        self,
        url: str,
        wait_until: str = "networkidle",
        capture_screenshot: bool = False,
    ) -> Dict[str, Any]:
        """
        Test the performance of a URL.
        
        Args:
            url: URL to test.
            wait_until: Wait until which event to consider page loaded.
                       Options: 'load', 'domcontentloaded', 'networkidle'
            capture_screenshot: Whether to capture a screenshot.
            
        Returns:
            Dictionary containing detailed performance results.
        """
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        page = None
        result = PerformanceResult(url=url)
        
        try:
            page = await self._context.new_page()
            
            # Setup tracing if enabled
            await self._setup_tracing(page)
            
            # Get initial response info
            start_time = asyncio.get_event_loop().time()
            
            response = await page.goto(
                url,
                wait_until=wait_until,
                timeout=self.config.scanner.timeout if self.config else 30000,
            )
            
            ttfb = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if response:
                result.metadata = {
                    "status": response.status,
                    "navigation_type": getattr(response, "navigation_type", "navigate"),
                }
            
            # Wait a bit for dynamic content
            await asyncio.sleep(1)
            
            # Capture Core Web Vitals
            js_metrics = await self._inject_performance_observer(page)
            
            # Get standard performance timing
            perf_timing = await page.evaluate("""
                () => {
                    const timing = performance.timing;
                    return {
                        navigationStart: timing.navigationStart,
                        loadEventEnd: timing.loadEventEnd,
                        domContentLoadedEventEnd: timing.domContentLoadedEventEnd,
                        domInteractive: timing.domInteractive,
                        responseStart: timing.responseStart,
                        requestStart: timing.requestStart,
                    };
                }
            """)
            
            # Calculate Core Web Vitals from JS metrics and Performance API
            vitals = CoreWebVitals()
            
            # TTFB
            if js_metrics and "ttfb" in js_metrics:
                vitals.ttfb = js_metrics["ttfb"]
            elif perf_timing:
                vitals.ttfb = perf_timing.get("responseStart", 0) - perf_timing.get("requestStart", 0)
            else:
                vitals.ttfb = ttfb
            
            # FCP
            if js_metrics and "fcp" in js_metrics and js_metrics["fcp"] > 0:
                vitals.fcp = js_metrics["fcp"]
            elif perf_timing:
                try:
                    fcp_entries = await page.evaluate("""
                        () => {
                            const entries = performance.getEntriesByType('paint');
                            const fcp = entries.find(e => e.name === 'first-contentful-paint');
                            return fcp ? fcp.startTime : 0;
                        }
                    """)
                    vitals.fcp = fcp_entries if fcp_entries else 0
                except Exception:
                    vitals.fcp = 0
            
            # LCP
            if js_metrics and "lcp" in js_metrics and js_metrics["lcp"] > 0:
                vitals.lcp = js_metrics["lcp"]
            else:
                lcp_value = await page.evaluate("""
                    () => {
                        const entries = performance.getEntriesByType('largest-contentful-paint');
                        return entries.length > 0 ? entries[entries.length - 1].startTime : 0;
                    }
                """)
                vitals.lcp = lcp_value if lcp_value else 0
            
            # FID
            if js_metrics and "fid" in js_metrics and js_metrics["fid"] > 0:
                vitals.fid = js_metrics["fid"]
            else:
                fid_value = await page.evaluate("""
                    () => {
                        const entries = performance.getEntriesByType('first-input');
                        return entries.length > 0 ? (entries[0].processingStart - entries[0].startTime) : 0;
                    }
                """)
                vitals.fid = fid_value if fid_value else 0
            
            # CLS
            if js_metrics and "cls" in js_metrics and js_metrics["cls"] > 0:
                vitals.cls = js_metrics["cls"]
            else:
                cls_value = await page.evaluate("""
                    () => {
                        const entries = performance.getEntriesByType('layout-shift');
                        let cls = 0;
                        let sessionValue = 0;
                        let lastTime = 0;
                        
                        entries.forEach(entry => {
                            if (!entry.hadRecentInput) {
                                if (entry.startTime - lastTime > 1000) {
                                    sessionValue = 0;
                                }
                                sessionValue += entry.value;
                                lastTime = entry.startTime;
                                cls = Math.max(cls, sessionValue);
                            }
                        });
                        return cls;
                    }
                """)
                vitals.cls = cls_value if cls_value else 0
            
            # TBT
            if js_metrics and "tbt" in js_metrics:
                vitals.tbt = js_metrics["tbt"]
            else:
                tbt_value = await page.evaluate("""
                    () => {
                        const entries = performance.getEntriesByType('longtask');
                        let tbt = 0;
                        entries.forEach(entry => {
                            if (entry.duration > 50) {
                                tbt += entry.duration - 50;
                            }
                        });
                        return tbt;
                    }
                """)
                vitals.tbt = tbt_value
            
            # Load and Interactive times
            if perf_timing:
                vitals.load = perf_timing.get("loadEventEnd", 0) - perf_timing.get("navigationStart", 0)
                vitals.interactive = perf_timing.get("domInteractive", 0) - perf_timing.get("navigationStart", 0)
                vitals.dom_content_loaded = perf_timing.get("domContentLoadedEventEnd", 0) - perf_timing.get("navigationStart", 0)
            
            result.web_vitals = vitals
            
            # Calculate Resource Metrics
            result.resources = await self._calculate_resource_metrics(page, js_metrics)
            
            # Get document size
            doc_size = await page.evaluate("""
                () => document.documentElement.innerHTML.length
            """)
            result.resources.document_size = doc_size
            result.resources.html_size = doc_size
            
            # Calculate overall score
            result.overall_score = self._calculate_overall_score(vitals)
            
            # Add warnings based on metrics
            self._add_warnings(result, vitals)
            
            # Stop tracing if enabled
            trace_path = await self._stop_tracing(page)
            if trace_path:
                logger.info(f"Performance trace saved to: {trace_path}")
            
            logger.info(f"Performance test completed for {url}")
            logger.info(f"  LCP: {vitals.lcp:.0f}ms, CLS: {vitals.cls:.4f}, FID: {vitals.fid:.0f}ms")
            
            return result.to_dict()
            
        except PlaywrightTimeout:
            logger.error(f"Timeout testing performance: {url}")
            result.errors.append("Timeout during performance test")
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Error testing performance {url}: {e}")
            result.errors.append(str(e))
            return result.to_dict()
            
        finally:
            if page:
                await page.close()
    
    def _calculate_overall_score(self, vitals: CoreWebVitals) -> float:
        """
        Calculate overall performance score (0-100).
        
        Based on Core Web Vitals thresholds.
        """
        score = 100
        
        # LCP score (weight: 25%)
        if vitals.lcp > 4000:
            score -= 25
        elif vitals.lcp > 2500:
            score -= 15
        elif vitals.lcp > 0:
            pass  # Good
        
        # CLS score (weight: 25%)
        if vitals.cls > 0.25:
            score -= 25
        elif vitals.cls > 0.1:
            score -= 15
        
        # FID/INP score (weight: 25%)
        if vitals.fid > 300:
            score -= 25
        elif vitals.fid > 100:
            score -= 15
        
        # TTFB score (weight: 15%)
        if vitals.ttfb > 1800:
            score -= 15
        elif vitals.ttfb > 800:
            score -= 10
        
        # TBT score (weight: 10%)
        if vitals.tbt > 600:
            score -= 10
        elif vitals.tbt > 200:
            score -= 5
        
        return max(0, score)
    
    def _add_warnings(self, result: PerformanceResult, vitals: CoreWebVitals) -> None:
        """Add performance warnings based on metrics."""
        
        # LCP warnings
        if vitals.lcp > 4000:
            result.warnings.append(f"LCP is poor ({vitals.lcp:.0f}ms). Consider optimizing images and server response.")
        elif vitals.lcp > 2500:
            result.warnings.append(f"LCP needs improvement ({vitals.lcp:.0f}ms).")
        
        # CLS warnings
        if vitals.cls > 0.25:
            result.warnings.append(f"CLS is poor ({vitals.cls:.4f}). Add size attributes to images and embeds.")
        elif vitals.cls > 0.1:
            result.warnings.append(f"CLS needs improvement ({vitals.cls:.4f}).")
        
        # FID warnings
        if vitals.fid > 300:
            result.warnings.append(f"FID is poor ({vitals.fid:.0f}ms). Break up long tasks.")
        elif vitals.fid > 100:
            result.warnings.append(f"FID needs improvement ({vitals.fid:.0f}ms).")
        
        # TTFB warnings
        if vitals.ttfb > 1800:
            result.warnings.append(f"TTFB is slow ({vitals.ttfb:.0f}ms). Consider using a CDN or optimizing server.")
        
        # TBT warnings
        if vitals.tbt > 600:
            result.warnings.append(f"High Total Blocking Time ({vitals.tbt:.0f}ms). Break up long JavaScript tasks.")
        
        # Resource warnings
        if result.resources.total_requests > 100:
            result.warnings.append(f"High number of requests ({result.resources.total_requests}). Consider bundling or code splitting.")
        
        if result.resources.total_size > 5 * 1024 * 1024:
            result.warnings.append(f"Large total page size ({result.resources.total_size / (1024*1024):.1f}MB). Optimize resources.")
    
    async def compare_urls(
        self,
        urls: List[str],
        iterations: int = 1,
    ) -> Dict[str, Any]:
        """
        Compare performance across multiple URLs.
        
        Args:
            urls: List of URLs to compare.
            iterations: Number of test iterations per URL.
            
        Returns:
            Dictionary with comparison results.
        """
        results = {}
        
        for url in urls:
            url_results = []
            for i in range(iterations):
                logger.info(f"Testing {url} (iteration {i+1}/{iterations})")
                result = await self.test_performance(url)
                url_results.append(result)
                
                # Brief delay between iterations
                if i < iterations - 1:
                    await asyncio.sleep(2)
            
            # Calculate averages
            if url_results:
                avg_web_vitals = CoreWebVitals()
                avg_vitals = url_results[0]["web_vitals"]
                
                for key in ["ttfb", "fcp", "lcp", "fid", "cls", "tbt", "load", "interactive"]:
                    values = [r["web_vitals"].get(f"{key}_ms", 0) for r in url_results]
                    avg_value = sum(values) / len(values)
                    setattr(avg_web_vitals, key, avg_value)
                
                results[url] = {
                    "individual_results": url_results,
                    "average": {
                        "web_vitals": avg_web_vitals.to_dict(),
                        "score": sum(r.get("scores", {}).get("overall", 0) for r in url_results) / len(url_results),
                        "total_requests": sum(r["resources"]["summary"]["total_requests"] for r in url_results) / len(url_results),
                    },
                    "iterations": iterations,
                }
        
        return results


# Alias for backwards compatibility
PerformanceTest = PerformanceTester
