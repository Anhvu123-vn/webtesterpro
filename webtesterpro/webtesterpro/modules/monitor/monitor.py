"""
Website Monitor Module

Monitors website uptime and performance over time.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from playwright.async_api import BrowserContext, Page, TimeoutError as PlaywrightTimeout

from webtesterpro.core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class MonitorResult:
    """Result of a single monitoring check."""
    url: str
    is_up: bool
    status_code: Optional[int] = None
    response_time: float = 0.0
    error: Optional[str] = None
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class MonitorSession:
    """A monitoring session with multiple checks."""
    url: str
    results: List[MonitorResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    uptime_percentage: float = 0.0
    avg_response_time: float = 0.0


class WebsiteMonitor:
    """
    Async website monitor using Playwright.
    
    Monitors websites for:
    - Uptime tracking
    - Response time measurement
    - Alert generation
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize the monitor.
        
        Args:
            config: Configuration object.
        """
        self.config = config or Config.load_default()
        self._context: Optional[BrowserContext] = None
        self._alert_callbacks: List[Callable] = []
        self._running = False
    
    def set_context(self, context: BrowserContext) -> None:
        """
        Set the Playwright browser context.
        
        Args:
            context: Browser context to use.
        """
        self._context = context
    
    def add_alert_callback(self, callback: Callable[[str, MonitorResult], None]) -> None:
        """
        Add a callback function for alerts.
        
        Args:
            callback: Function that takes (url, result) and is called on alerts.
        """
        self._alert_callbacks.append(callback)
    
    async def _check_url(self, url: str) -> MonitorResult:
        """
        Perform a single check on a URL.
        
        Args:
            url: URL to check.
            
        Returns:
            MonitorResult object.
        """
        page = None
        start_time = asyncio.get_event_loop().time()
        
        try:
            page = await self._context.new_page()
            
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.config.monitor.timeout * 1000,
            )
            
            response_time = asyncio.get_event_loop().time() - start_time
            
            result = MonitorResult(
                url=url,
                is_up=True,
                status_code=response.status if response else 200,
                response_time=response_time,
            )
            
            logger.debug(f"Check OK: {url} ({response.status}, {response_time:.2f}s)")
            
            return result
            
        except PlaywrightTimeout:
            response_time = asyncio.get_event_loop().time() - start_time
            result = MonitorResult(
                url=url,
                is_up=False,
                status_code=None,
                response_time=response_time,
                error="Timeout",
            )
            logger.warning(f"Check FAILED (timeout): {url}")
            return result
            
        except Exception as e:
            response_time = asyncio.get_event_loop().time() - start_time
            result = MonitorResult(
                url=url,
                is_up=False,
                status_code=None,
                response_time=response_time,
                error=str(e),
            )
            logger.warning(f"Check FAILED: {url} - {e}")
            return result
            
        finally:
            if page:
                await page.close()
    
    async def monitor(
        self,
        url: str,
        interval: Optional[int] = None,
        duration: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Monitor a website.
        
        Args:
            url: URL to monitor.
            interval: Check interval in seconds (default from config).
            duration: Total duration in seconds, None for indefinite.
            
        Returns:
            Dictionary containing monitoring results.
        """
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        interval = interval or self.config.monitor.interval
        duration = duration or 300
        
        session = MonitorSession(url=url)
        self._running = True
        start_time = asyncio.get_event_loop().time()
        
        logger.info(f"Starting monitoring of {url}")
        logger.info(f"Interval: {interval}s, Duration: {duration}s")
        
        check_count = 0
        max_checks = duration // interval if duration else float("inf")
        
        while self._running and check_count < max_checks:
            elapsed = asyncio.get_event_loop().time() - start_time
            if duration and elapsed >= duration:
                break
            
            result = await self._check_url(url)
            session.results.append(result)
            
            if not result.is_up and self.config.monitor.alert_on_down:
                for callback in self._alert_callbacks:
                    try:
                        callback(url, result)
                    except Exception as e:
                        logger.error(f"Alert callback error: {e}")
            
            check_count += 1
            
            if check_count < max_checks:
                await asyncio.sleep(interval)
        
        session.end_time = datetime.now()
        
        successful_checks = sum(1 for r in session.results if r.is_up)
        session.uptime_percentage = (
            (successful_checks / len(session.results)) * 100
            if session.results else 0
        )
        
        response_times = [r.response_time for r in session.results]
        session.avg_response_time = (
            sum(response_times) / len(response_times)
            if response_times else 0
        )
        
        logger.info(f"Monitoring completed: {session.uptime_percentage:.1f}% uptime, "
                   f"{len(session.results)} checks")
        
        return {
            "url": url,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat(),
            "duration_seconds": (session.end_time - session.start_time).total_seconds(),
            "total_checks": len(session.results),
            "successful_checks": successful_checks,
            "failed_checks": len(session.results) - successful_checks,
            "uptime_percentage": round(session.uptime_percentage, 2),
            "avg_response_time_seconds": round(session.avg_response_time, 3),
            "min_response_time_seconds": round(min(response_times), 3) if response_times else 0,
            "max_response_time_seconds": round(max(response_times), 3) if response_times else 0,
            "results": [
                {
                    "is_up": r.is_up,
                    "status_code": r.status_code,
                    "response_time_seconds": round(r.response_time, 3),
                    "error": r.error,
                    "checked_at": r.checked_at.isoformat(),
                }
                for r in session.results
            ],
        }
    
    async def check_once(self, url: str) -> MonitorResult:
        """
        Perform a single check on a URL.
        
        Args:
            url: URL to check.
            
        Returns:
            MonitorResult object.
        """
        return await self._check_url(url)
    
    def stop(self) -> None:
        """Stop the monitoring session."""
        self._running = False
        logger.info("Monitoring stopped")
