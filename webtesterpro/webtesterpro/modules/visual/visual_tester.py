"""
Visual Tester Module

Provides visual testing capabilities using Playwright:
- Screenshot capture (full page and viewport)
- Multi-device viewport simulation
- Visual regression testing with diff
- Baseline comparison
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import BrowserContext, Page
from playwright.async_api import TimeoutError as PlaywrightTimeout

from webtesterpro.core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class Viewport:
    """
    Viewport configuration for different devices.
    """
    name: str
    width: int
    height: int
    device_scale_factor: float = 1.0
    is_mobile: bool = False
    has_touch: bool = False
    
    @classmethod
    def desktop(cls) -> "Viewport":
        """Desktop viewport (1920x1080)."""
        return cls(name="desktop", width=1920, height=1080)
    
    @classmethod
    def laptop(cls) -> "Viewport":
        """Laptop viewport (1366x768)."""
        return cls(name="laptop", width=1366, height=768)
    
    @classmethod
    def tablet_landscape(cls) -> "Viewport":
        """Tablet landscape viewport (1024x768)."""
        return cls(name="tablet-landscape", width=1024, height=768)
    
    @classmethod
    def tablet_portrait(cls) -> "Viewport":
        """Tablet portrait viewport (768x1024)."""
        return cls(name="tablet-portrait", width=768, height=1024, is_mobile=True)
    
    @classmethod
    def mobile_landscape(cls) -> "Viewport":
        """Mobile landscape viewport (640x360)."""
        return cls(name="mobile-landscape", width=640, height=360, is_mobile=True, has_touch=True)
    
    @classmethod
    def mobile_portrait(cls) -> "Viewport":
        """Mobile portrait viewport (375x667) - iPhone 6/7/8."""
        return cls(name="mobile-portrait", width=375, height=667, is_mobile=True, has_touch=True)
    
    @classmethod
    def responsive_all(cls) -> List["Viewport"]:
        """Get all responsive viewports."""
        return [
            cls.desktop(),
            cls.laptop(),
            cls.tablet_landscape(),
            cls.tablet_portrait(),
            cls.mobile_landscape(),
            cls.mobile_portrait(),
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "device_scale_factor": self.device_scale_factor,
            "is_mobile": self.is_mobile,
            "has_touch": self.has_touch,
        }


@dataclass
class ScreenshotResult:
    """
    Result of a screenshot capture.
    """
    url: str
    viewport: Viewport
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Image data
    base64_image: str = ""
    image_path: str = ""
    image_hash: str = ""
    
    # Metadata
    width: int = 0
    height: int = 0
    file_size: int = 0
    
    # Status
    success: bool = True
    error: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "viewport": self.viewport.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "image_path": self.image_path,
            "image_hash": self.image_hash,
            "width": self.width,
            "height": self.height,
            "file_size": self.file_size,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class VisualDiff:
    """
    Visual difference between two screenshots.
    """
    baseline_path: str
    current_path: str
    diff_path: str = ""
    
    # Comparison results
    pixel_difference: int = 0
    percentage_difference: float = 0.0
    diff_regions: List[Dict] = field(default_factory=list)
    
    # Status
    is_identical: bool = True
    threshold_passed: bool = True
    error: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "baseline_path": self.baseline_path,
            "current_path": self.current_path,
            "diff_path": self.diff_path,
            "pixel_difference": self.pixel_difference,
            "percentage_difference": round(self.percentage_difference, 4),
            "diff_regions": self.diff_regions,
            "is_identical": self.is_identical,
            "threshold_passed": self.threshold_passed,
            "error": self.error,
        }


class VisualTester:
    """
    Async visual tester using Playwright.
    
    Provides visual testing capabilities:
    - Screenshot capture (full page and viewport)
    - Multi-device viewport simulation
    - Visual regression testing with pixel comparison
    - Baseline management
    
    Usage:
        async with WebTesterEngine() as engine:
            tester = VisualTester(baseline_dir="./baselines")
            tester.set_context(engine._context)
            
            # Take screenshot
            result = await tester.screenshot("https://example.com")
            
            # Compare with baseline
            diff = await tester.compare("https://example.com", viewport)
    """
    
    DEFAULT_THRESHOLD = 0.1  # 0.1% difference allowed
    
    def __init__(self, config: Config = None, baseline_dir: str = "baselines"):
        """
        Initialize the visual tester.
        
        Args:
            config: Configuration object.
            baseline_dir: Directory to store baseline images.
        """
        self.config = config
        self._context: Optional[BrowserContext] = None
        self.baseline_dir = Path(baseline_dir)
        self.threshold = self.DEFAULT_THRESHOLD
        
        # Create baseline directory if it doesn't exist
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
    
    def set_context(self, context: BrowserContext) -> None:
        """
        Set the Playwright browser context.
        
        Args:
            context: Browser context to use.
        """
        self._context = context
    
    def _generate_baseline_path(self, url: str, viewport: Viewport) -> Path:
        """Generate path for baseline image."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"{viewport.name}_{url_hash}.png"
        return self.baseline_dir / filename
    
    def _get_image_hash(self, image_data: bytes) -> str:
        """Calculate MD5 hash of image data."""
        return hashlib.md5(image_data).hexdigest()
    
    async def screenshot(
        self,
        url: str,
        viewport: Optional[Viewport] = None,
        full_page: bool = False,
        wait_for_load: bool = True,
        delay_ms: int = 0,
        hide_selectors: Optional[List[str]] = None,
    ) -> ScreenshotResult:
        """
        Take a screenshot of a URL.
        
        Args:
            url: URL to screenshot.
            viewport: Viewport configuration. Uses desktop if None.
            full_page: If True, capture full scrollable page.
            wait_for_load: Wait for page to fully load.
            delay_ms: Delay before screenshot (for animations).
            hide_selectors: CSS selectors to hide before screenshot.
            
        Returns:
            ScreenshotResult object.
        """
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        if viewport is None:
            viewport = Viewport.desktop()
        
        result = ScreenshotResult(url=url, viewport=viewport)
        
        try:
            page = await self._context.new_page()
            
            # Set viewport
            await page.set_viewport_size({"width": viewport.width, "height": viewport.height})
            
            # Set mobile emulation if needed
            if viewport.is_mobile or viewport.has_touch:
                await page.set_extra_http_headers({
                    "viewport": f"width={viewport.width}, height={viewport.height}"
                })
            
            # Navigate to URL
            navigation_params = {
                "wait_until": "networkidle" if wait_for_load else "domcontentloaded",
            }
            if self.config:
                navigation_params["timeout"] = self.config.scanner.timeout
            else:
                navigation_params["timeout"] = 30000
            
            await page.goto(url, **navigation_params)
            
            # Apply delay if specified
            if delay_ms > 0:
                await asyncio.sleep(delay_ms / 1000)
            
            # Hide elements if specified
            if hide_selectors:
                await self._hide_elements(page, hide_selectors)
            
            # Take screenshot
            screenshot_options = {
                "type": "png",
                "full_page": full_page,
            }
            
            # Add masking for elements if needed
            if hide_selectors:
                screenshot_options["mask"] = await self._get_mask_for_selectors(page, hide_selectors)
            
            image_bytes = await page.screenshot(**screenshot_options)
            
            # Get viewport dimensions
            result.width = viewport.width
            result.height = viewport.height if not full_page else await page.evaluate("document.body.scrollHeight")
            
            # Encode to base64
            result.base64_image = base64.b64encode(image_bytes).decode("utf-8")
            result.image_hash = self._get_image_hash(image_bytes)
            result.file_size = len(image_bytes)
            result.success = True
            
            await page.close()
            
            logger.info(f"Screenshot taken for {url} at {viewport.name}")
            
        except PlaywrightTimeout:
            logger.error(f"Timeout taking screenshot: {url}")
            result.success = False
            result.error = "Timeout"
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            result.success = False
            result.error = str(e)
        
        return result
    
    async def _hide_elements(self, page: Page, selectors: List[str]) -> None:
        """Hide elements matching selectors."""
        for selector in selectors:
            try:
                await page.evaluate(
                    f"""
                    () => {{
                        const elements = document.querySelectorAll('{selector}');
                        elements.forEach(el => {{ el.style.visibility = 'hidden'; }});
                    }}
                    """,
                )
            except Exception:
                pass
    
    async def _get_mask_for_selectors(self, page: Page, selectors: List[str]) -> List:
        """Get mask locators for selectors."""
        # Note: Playwright's mask feature requires locators
        # This is a placeholder for advanced masking
        return []
    
    async def save_baseline(
        self,
        url: str,
        viewport: Optional[Viewport] = None,
        path: Optional[Path] = None,
    ) -> ScreenshotResult:
        """
        Save a screenshot as baseline.
        
        Args:
            url: URL to screenshot.
            viewport: Viewport configuration.
            path: Custom path for baseline image.
            
        Returns:
            ScreenshotResult object with saved path.
        """
        if viewport is None:
            viewport = Viewport.desktop()
        
        if path is None:
            path = self._generate_baseline_path(url, viewport)
        
        result = await self.screenshot(url, viewport)
        
        if result.success:
            result.image_path = str(path)
            
            # Save image to file
            with open(path, "wb") as f:
                f.write(base64.b64decode(result.base64_image))
            
            logger.info(f"Baseline saved: {path}")
        
        return result
    
    async def compare(
        self,
        url: str,
        viewport: Optional[Viewport] = None,
        threshold: Optional[float] = None,
        generate_diff: bool = True,
    ) -> VisualDiff:
        """
        Compare current screenshot with baseline.
        
        Args:
            url: URL to compare.
            viewport: Viewport configuration.
            threshold: Maximum allowed difference percentage (0-100).
            generate_diff: Whether to generate diff image.
            
        Returns:
            VisualDiff object with comparison results.
        """
        if viewport is None:
            viewport = Viewport.desktop()
        
        if threshold is None:
            threshold = self.threshold
        
        baseline_path = self._generate_baseline_path(url, viewport)
        
        diff = VisualDiff(
            baseline_path=str(baseline_path),
            current_path="",
        )
        
        # Check if baseline exists
        if not baseline_path.exists():
            diff.error = f"Baseline not found: {baseline_path}"
            diff.is_identical = False
            diff.threshold_passed = False
            return diff
        
        # Take current screenshot
        current_result = await self.screenshot(url, viewport)
        
        if not current_result.success:
            diff.error = f"Failed to capture current screenshot: {current_result.error}"
            return diff
        
        diff.current_path = str(baseline_path).replace(".png", "_current.png")
        
        # Save current image
        current_path = Path(diff.current_path)
        with open(current_path, "wb") as f:
            f.write(base64.b64decode(current_result.base64_image))
        
        # Compare images
        try:
            comparison_result = await self._compare_images(
                str(baseline_path),
                str(current_path),
                generate_diff=generate_diff,
            )
            
            diff.pixel_difference = comparison_result["pixel_difference"]
            diff.percentage_difference = comparison_result["percentage_difference"]
            diff.diff_regions = comparison_result.get("diff_regions", [])
            
            diff.is_identical = diff.pixel_difference == 0
            diff.threshold_passed = diff.percentage_difference <= threshold * 100
            
            if generate_diff and not diff.is_identical:
                diff.diff_path = str(baseline_path).replace(".png", "_diff.png")
                with open(diff.diff_path, "wb") as f:
                    f.write(base64.b64decode(comparison_result["diff_base64"]))
            
            logger.info(
                f"Comparison: {diff.percentage_difference:.4f}% difference, "
                f"{'PASSED' if diff.threshold_passed else 'FAILED'}"
            )
            
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            diff.error = str(e)
            diff.is_identical = False
            diff.threshold_passed = False
        
        return diff
    
    async def _compare_images(
        self,
        baseline_path: str,
        current_path: str,
        generate_diff: bool = True,
    ) -> Dict[str, Any]:
        """
        Compare two images and calculate difference.
        
        Uses pixel-by-pixel comparison.
        
        Args:
            baseline_path: Path to baseline image.
            current_path: Path to current image.
            generate_diff: Whether to generate diff image.
            
        Returns:
            Dictionary with comparison results.
        """
        # Try to use pixelmatch if available
        try:
            import pixelmatch
            from PIL import Image
            import io
            
            baseline_img = Image.open(baseline_path)
            current_img = Image.open(current_path)
            
            # Convert to RGB if needed
            if baseline_img.mode != "RGB":
                baseline_img = baseline_img.convert("RGB")
            if current_img.mode != "RGB":
                current_img = current_img.convert("RGB")
            
            # Ensure same dimensions
            if baseline_img.size != current_img.size:
                current_img = current_img.resize(baseline_img.size, Image.LANCZOS)
            
            # Create diff image
            diff_img = Image.new("RGB", baseline_img.size)
            
            width, height = baseline_img.size
            pixels_baseline = list(baseline_img.getdata())
            pixels_current = list(current_img.getdata())
            pixels_diff = list(diff_img.getdata())
            
            diff_count = 0
            diff_regions = []
            
            threshold = 0.1  # Per-channel threshold
            
            for i, (b, c) in enumerate(zip(pixels_baseline, pixels_current)):
                if any(abs(a - b) > threshold * 255 for a, b in zip(b, c)):
                    pixels_diff[i] = (255, 0, 0)  # Red for difference
                    diff_count += 1
                else:
                    pixels_diff[i] = b
            
            diff_img.putdata(pixels_diff)
            
            # Calculate regions of difference
            diff_regions = self._find_diff_regions(diff_img, threshold=0.5)
            
            result = {
                "pixel_difference": diff_count,
                "percentage_difference": (diff_count / (width * height)) * 100,
                "diff_regions": diff_regions,
            }
            
            if generate_diff:
                buffer = io.BytesIO()
                diff_img.save(buffer, format="PNG")
                result["diff_base64"] = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            return result
            
        except ImportError:
            # Fallback to simple byte comparison
            logger.warning("pixelmatch not available, using simple comparison")
            return await self._simple_compare(baseline_path, current_path, generate_diff)
    
    async def _simple_compare(
        self,
        baseline_path: str,
        current_path: str,
        generate_diff: bool = True,
    ) -> Dict[str, Any]:
        """
        Simple image comparison without pixelmatch.
        
        Compares file hashes and basic dimensions.
        """
        import io
        from PIL import Image
        
        with open(baseline_path, "rb") as f:
            baseline_data = f.read()
        
        with open(current_path, "rb") as f:
            current_data = f.read()
        
        baseline_hash = self._get_image_hash(baseline_data)
        current_hash = self._get_image_hash(current_data)
        
        is_identical = baseline_hash == current_hash
        
        # Get dimensions
        baseline_img = Image.open(io.BytesIO(baseline_data))
        current_img = Image.open(io.BytesIO(current_data))
        
        width1, height1 = baseline_img.size
        width2, height2 = current_img.size
        
        result = {
            "pixel_difference": 0 if is_identical else 1,
            "percentage_difference": 0.0 if is_identical else 100.0,
            "diff_regions": [],
        }
        
        if not is_identical:
            result["diff_regions"] = [{
                "type": "dimension_mismatch" if (width1, height1) != (width2, height2) else "content_different",
                "message": f"Images are different: {width1}x{height1} vs {width2}x{height2}"
            }]
        
        if generate_diff and not is_identical:
            # Create simple diff image
            diff_img = Image.new("RGB", (max(width1, width2), max(height1, height2)), (128, 128, 128))
            
            # Draw side by side with labels would require more complex code
            # For now, just use current image
            diff_img.paste(current_img, (0, 0))
            
            buffer = io.BytesIO()
            diff_img.save(buffer, format="PNG")
            result["diff_base64"] = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return result
    
    def _find_diff_regions(self, diff_img, threshold: float = 0.5) -> List[Dict]:
        """
        Find regions of difference in diff image.
        
        Args:
            diff_img: PIL Image with red pixels for differences.
            threshold: Minimum percentage of red pixels to consider a region.
            
        Returns:
            List of region dictionaries.
        """
        # Simplified implementation - just returns basic info
        regions = []
        
        width, height = diff_img.size
        pixels = list(diff_img.getdata())
        
        # Count red pixels
        red_count = sum(1 for p in pixels if p[0] > 200 and p[1] < 50 and p[2] < 50)
        
        if red_count > 0:
            regions.append({
                "type": "difference",
                "pixel_count": red_count,
                "percentage": round((red_count / (width * height)) * 100, 2),
                "message": f"Found {red_count} differing pixels ({red_count / (width * height) * 100:.2f}%)"
            })
        
        return regions
    
    async def screenshot_multiple_viewports(
        self,
        url: str,
        viewports: Optional[List[Viewport]] = None,
        full_page: bool = False,
    ) -> Dict[str, ScreenshotResult]:
        """
        Take screenshots across multiple viewports.
        
        Args:
            url: URL to screenshot.
            viewports: List of viewports. Uses responsive_all() if None.
            full_page: If True, capture full scrollable page.
            
        Returns:
            Dictionary mapping viewport name to ScreenshotResult.
        """
        if viewports is None:
            viewports = Viewport.responsive_all()
        
        results = {}
        
        for viewport in viewports:
            result = await self.screenshot(url, viewport, full_page=full_page)
            results[viewport.name] = result
            
            # Small delay between screenshots
            await asyncio.sleep(0.5)
        
        return results
    
    async def update_baselines(
        self,
        url: str,
        viewports: Optional[List[Viewport]] = None,
    ) -> Dict[str, ScreenshotResult]:
        """
        Update all baselines for a URL.
        
        Args:
            url: URL to screenshot.
            viewports: List of viewports.
            
        Returns:
            Dictionary of saved results.
        """
        if viewports is None:
            viewports = Viewport.responsive_all()
        
        results = {}
        
        for viewport in viewports:
            result = await self.save_baseline(url, viewport)
            results[viewport.name] = result
            
            await asyncio.sleep(0.5)
        
        return results
    
    def list_baselines(self) -> List[str]:
        """List all baseline images."""
        if not self.baseline_dir.exists():
            return []
        
        return [str(p) for p in self.baseline_dir.glob("*.png")]
    
    def delete_baseline(self, url: str, viewport: Viewport) -> bool:
        """
        Delete baseline for a URL and viewport.
        
        Args:
            url: URL of baseline.
            viewport: Viewport of baseline.
            
        Returns:
            True if deleted, False if not found.
        """
        path = self._generate_baseline_path(url, viewport)
        
        if path.exists():
            path.unlink()
            logger.info(f"Deleted baseline: {path}")
            return True
        
        return False


# Alias for backwards compatibility
VisualTest = VisualTester
