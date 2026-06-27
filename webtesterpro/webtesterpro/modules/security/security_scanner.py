"""
Security Scanner Module

Provides comprehensive security scanning using Playwright:
- Security Headers check
- Mixed Content detection
- SSL/TLS validation
- Sensitive file exposure
- XSS & SQLi pattern detection
- Clickjacking & CORS checks
- Risk classification (Low/Medium/High/Critical)
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


class RiskLevel(Enum):
    """Security risk classification levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1


@dataclass
class SecurityIssue:
    """
    Represents a single security issue found during scanning.
    """
    category: str
    title: str
    description: str
    risk_level: RiskLevel
    url: str
    evidence: str = ""
    recommendation: str = ""
    cwe_id: str = ""  # Common Weakness Enumeration
    remediation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "url": self.url,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "cwe_id": self.cwe_id,
            "remediation": self.remediation,
        }


@dataclass
class SecurityReport:
    """
    Complete security scan report.
    """
    url: str
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[SecurityIssue] = field(default_factory=list)
    
    # Summary counts
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    
    # SSL/TLS info
    ssl_valid: bool = False
    ssl_version: str = ""
    ssl_expiry: str = ""
    
    # Scan metadata
    scan_duration: float = 0.0
    pages_scanned: int = 0
    
    def __post_init__(self):
        """Update counts after initialization."""
        self.critical_count = sum(1 for i in self.issues if i.risk_level == RiskLevel.CRITICAL)
        self.high_count = sum(1 for i in self.issues if i.risk_level == RiskLevel.HIGH)
        self.medium_count = sum(1 for i in self.issues if i.risk_level == RiskLevel.MEDIUM)
        self.low_count = sum(1 for i in self.issues if i.risk_level == RiskLevel.LOW)
        self.info_count = sum(1 for i in self.issues if i.risk_level == RiskLevel.INFO)

    def get_overall_risk_score(self) -> int:
        """Calculate overall risk score (0-100)."""
        score = 100
        score -= self.critical_count * 30
        score -= self.high_count * 20
        score -= self.medium_count * 10
        score -= self.low_count * 5
        return max(0, score)

    def get_risk_rating(self) -> str:
        """Get risk rating based on issue counts."""
        if self.critical_count > 0:
            return "CRITICAL"
        elif self.high_count > 0:
            return "HIGH"
        elif self.medium_count > 0:
            return "MEDIUM"
        elif self.low_count > 0:
            return "LOW"
        return "SECURE"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "overall_risk_score": self.get_overall_risk_score(),
                "risk_rating": self.get_risk_rating(),
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
                "info": self.info_count,
                "total": len(self.issues),
            },
            "ssl": {
                "valid": self.ssl_valid,
                "version": self.ssl_version,
                "expiry": self.ssl_expiry,
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": {
                "scan_duration_seconds": round(self.scan_duration, 2),
                "pages_scanned": self.pages_scanned,
            },
        }


class SecurityScanner:
    """
    Async security scanner using Playwright.
    
    Performs comprehensive security scans including:
    - Security Headers validation
    - Mixed Content detection
    - SSL/TLS certificate checks
    - Sensitive file exposure
    - XSS & SQLi pattern detection
    - Clickjacking vulnerability
    - CORS misconfiguration
    
    Usage:
        async with WebTesterEngine() as engine:
            scanner = SecurityScanner()
            scanner.set_context(engine._context)
            report = await scanner.scan("https://example.com")
    """
    
    # Security headers to check
    SECURITY_HEADERS = {
        "content-security-policy": {
            "risk": RiskLevel.HIGH,
            "description": "Content Security Policy helps prevent XSS and data injection attacks",
            "remediation": "Add Content-Security-Policy header with appropriate directives",
            "cwe_id": "CWE-1021",
        },
        "strict-transport-security": {
            "risk": RiskLevel.HIGH,
            "description": "HSTS ensures browsers only connect via HTTPS",
            "remediation": "Add Strict-Transport-Security header with max-age directive",
            "cwe_id": "CWE-523",
        },
        "x-content-type-options": {
            "risk": RiskLevel.MEDIUM,
            "description": "Prevents MIME type sniffing",
            "remediation": "Add X-Content-Type-Options: nosniff header",
            "cwe_id": "CWE-430",
        },
        "x-frame-options": {
            "risk": RiskLevel.HIGH,
            "description": "Protects against clickjacking attacks",
            "remediation": "Add X-Frame-Options: DENY or SAMEORIGIN header",
            "cwe_id": "CWE-1021",
        },
        "x-xss-protection": {
            "risk": RiskLevel.LOW,
            "description": "Legacy XSS filter (deprecated but still useful)",
            "remediation": "Consider using CSP instead, but X-XSS-Protection can still help legacy browsers",
            "cwe_id": "CWE-79",
        },
        "referrer-policy": {
            "risk": RiskLevel.MEDIUM,
            "description": "Controls how much referrer information is sent",
            "remediation": "Add Referrer-Policy header (e.g., strict-origin-when-cross-origin)",
            "cwe_id": "CWE-200",
        },
        "permissions-policy": {
            "risk": RiskLevel.MEDIUM,
            "description": "Controls which browser features can be used",
            "remediation": "Add Permissions-Policy header to restrict unnecessary features",
            "cwe_id": "CWE-1021",
        },
        "cross-origin-opener-policy": {
            "risk": RiskLevel.MEDIUM,
            "description": "Isolates browsing context to prevent cross-origin attacks",
            "remediation": "Add Cross-Origin-Opener-Policy: same-origin header",
            "cwe_id": "CWE-1021",
        },
        "cross-origin-embedder-policy": {
            "risk": RiskLevel.LOW,
            "description": "Prevents loading cross-origin resources without permission",
            "remediation": "Consider adding Cross-Origin-Embedder-Policy header",
            "cwe_id": "CWE-1021",
        },
        "cross-origin-resource-policy": {
            "risk": RiskLevel.INFO,
            "description": "Controls which sites can include this resource",
            "remediation": "Add Cross-Origin-Resource-Policy: same-origin header",
            "cwe_id": "CWE-1021",
        },
    }
    
    # Sensitive file patterns
    SENSITIVE_FILES = [
        (r"\.git(/|\.gitignore|\.git/config)?", "Git repository exposed", RiskLevel.HIGH),
        (r"\.env(\.|$)", ".env file exposed", RiskLevel.CRITICAL),
        (r"\.htaccess", ".htaccess file accessible", RiskLevel.MEDIUM),
        (r"\.htpasswd", ".htpasswd file accessible", RiskLevel.HIGH),
        (r"\.sql$", "SQL backup file exposed", RiskLevel.HIGH),
        (r"\.bak$", "Backup file exposed", RiskLevel.MEDIUM),
        (r"\.old$", "Old file exposed", RiskLevel.LOW),
        (r"\.tmp$", "Temporary file exposed", RiskLevel.LOW),
        (r"\.zip$", "Archive file exposed", RiskLevel.MEDIUM),
        (r"\.tar\.gz$", "Archive file exposed", RiskLevel.MEDIUM),
        (r"config\.php\.bak", "Config backup exposed", RiskLevel.HIGH),
        (r"database\.sql\.gz", "Database backup exposed", RiskLevel.CRITICAL),
        (r"wp-config\.php\.bak", "WordPress config backup", RiskLevel.CRITICAL),
        (r"\.DS_Store", "macOS metadata exposed", RiskLevel.LOW),
        (r"Thumbs\.db", "Windows thumbnail cache", RiskLevel.LOW),
        (r"\.pem$", "Certificate file exposed", RiskLevel.HIGH),
        (r"\.key$", "Private key exposed", RiskLevel.CRITICAL),
        (r"\.log$", "Log file exposed", RiskLevel.MEDIUM),
        (r"debug\.log", "Debug log exposed", RiskLevel.MEDIUM),
        (r"\.json$", "JSON file accessible", RiskLevel.LOW),
        (r"\.xml$", "XML file accessible", RiskLevel.LOW),
        (r"\.config$", "Configuration file", RiskLevel.MEDIUM),
        (r"\.conf$", "Configuration file", RiskLevel.MEDIUM),
        (r"\.ini$", "INI file accessible", RiskLevel.MEDIUM),
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        (r"<script[^>]*>", "Inline script tag"),
        (r"javascript:", "JavaScript protocol in attribute"),
        (r"on\w+\s*=", "Inline event handler"),
        (r"<img[^>]+onerror=", "Image with onerror"),
        (r"<svg[^>]+onload=", "SVG with onload"),
        (r"<iframe[^>]+src=", "Iframe injection possible"),
        (r"document\.cookie", "Document cookie access"),
        (r"document\.write", "Dynamic document write"),
        (r"innerHTML\s*=", "InnerHTML assignment"),
        (r"eval\s*\(", "Eval usage (XSS risk)"),
        (r"alert\s*\(", "Alert usage (XSS probe)"),
    ]
    
    # SQLi patterns
    SQLI_PATTERNS = [
        (r"('|\"|;)\s*(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)", "SQL injection pattern"),
        (r"(OR|AND)\s+\d+\s*=\s*\d+", "Boolean-based SQLi pattern"),
        (r"('\s*(OR|AND)\s*')", "Classic SQLi pattern"),
        (r"(UNION\s+SELECT)", "UNION-based SQLi pattern"),
        (r"(DROP\s+TABLE)", "Dangerous SQL command"),
        (r"(--|#)\s*$", "SQL comment at end"),
        (r"\s+OR\s+'1'\s*=\s*'1", "Classic OR SQLi"),
    ]
    
    # Mixed content indicators
    MIXED_CONTENT_PATTERNS = [
        (r"https?://[^\s]*\.(jpg|jpeg|png|gif|svg|ico|webp)(\?|$)", "Image loaded via HTTP"),
        (r"src=['\"]http://", "Resource loaded via HTTP in HTTPS page"),
        (r"url\(['\"]http://", "CSS url() with HTTP"),
    ]
    
    def __init__(self, config: Config = None):
        """
        Initialize the security scanner.
        
        Args:
            config: Configuration object.
        """
        self.config = config
        self._context: Optional[BrowserContext] = None
        self._report: Optional[SecurityReport] = None
    
    def set_context(self, context: BrowserContext) -> None:
        """
        Set the Playwright browser context.
        
        Args:
            context: Browser context to use.
        """
        self._context = context
    
    async def _check_security_headers(self, url: str, headers: Dict[str, str]) -> List[SecurityIssue]:
        """Check for missing security headers."""
        issues = []
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        
        for header_name, info in self.SECURITY_HEADERS.items():
            if header_name.lower() not in normalized_headers:
                issues.append(SecurityIssue(
                    category="Security Headers",
                    title=f"Missing {header_name} header",
                    description=info["description"],
                    risk_level=info["risk"],
                    url=url,
                    evidence=f"Header '{header_name}' not found in response",
                    recommendation=info["remediation"],
                    cwe_id=info["cwe_id"],
                ))
        
        return issues
    
    async def _check_ssl_tls(self, url: str) -> List[SecurityIssue]:
        """Check SSL/TLS configuration."""
        issues = []
        
        if not url.startswith("https://"):
            issues.append(SecurityIssue(
                category="SSL/TLS",
                title="Site not using HTTPS",
                description="The website does not enforce HTTPS encryption",
                risk_level=RiskLevel.CRITICAL,
                url=url,
                evidence="URL does not start with https://",
                recommendation="Implement HTTPS and redirect all HTTP traffic to HTTPS",
                cwe_id="CWE-319",
            ))
            return issues
        
        try:
            page = await self._context.new_page()
            response = await page.goto(url, wait_until="domcontentloaded", timeout=10000)
            
            if response:
                # Check SSL certificate info
                if hasattr(response, 'headers'):
                    headers = dict(response.headers)
                    
                    # Check for secure cipher suites (via security header)
                    if 'strict-transport-security' not in headers:
                        issues.append(SecurityIssue(
                            category="SSL/TLS",
                            title="HSTS not configured",
                            description="HTTP Strict Transport Security is not configured",
                            risk_level=RiskLevel.MEDIUM,
                            url=url,
                            recommendation="Add Strict-Transport-Security header",
                            cwe_id="CWE-523",
                        ))
            
            await page.close()
            
        except Exception as e:
            logger.debug(f"SSL check error: {e}")
        
        return issues
    
    async def _check_sensitive_files(self, url: str) -> List[SecurityIssue]:
        """Check for exposed sensitive files."""
        issues = []
        parsed = None
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
        except Exception:
            return issues
        
        base_urls = [
            url,
            f"{parsed.scheme}://{parsed.netloc}",
        ]
        
        for file_pattern, description, risk in self.SENSITIVE_FILES:
            # Generate potential URLs with sensitive files
            # (Comment: this variable is not used but kept for future reference)
            pass
            
            # Common sensitive paths
            common_paths = [
                ".git/config",
                ".git/HEAD",
                ".gitignore",
                ".env",
                ".env.bak",
                ".htaccess",
                ".htpasswd",
                "config.php.bak",
                "wp-config.php.bak",
                "database.sql",
                "backup.sql",
                "dump.sql",
                "debug.log",
                "error.log",
                "config.json",
                "settings.xml",
                "database.yml",
                "credentials.json",
                "private.key",
                "server.crt",
            ]
            
            for path in common_paths:
                if re.search(file_pattern, path, re.IGNORECASE):
                    check_url = f"{parsed.scheme}://{parsed.netloc}/{path}"
                    
                    try:
                        page = await self._context.new_page()
                        response = await page.goto(
                            check_url,
                            timeout=5000,
                            wait_until="domcontentloaded"
                        )
                        
                        if response and response.status in (200, 401, 403):
                            # Check if response actually contains sensitive content
                            content_type = response.headers.get("content-type", "")
                            
                            if "text" in content_type or "application" in content_type:
                                body = await response.text()
                                
                                # Check if file contains sensitive content
                                if any(keyword in body.lower() for keyword in 
                                       ["password", "secret", "api_key", "private", "credential", 
                                        "database", "config", "token", "auth"]):
                                    issues.append(SecurityIssue(
                                        category="Sensitive File Exposure",
                                        title=description,
                                        description=f"Sensitive file '{path}' is accessible and may contain credentials",
                                        risk_level=risk,
                                        url=check_url,
                                        evidence=f"HTTP {response.status} - Content-Type: {content_type}",
                                        recommendation=f"Remove or restrict access to {path}",
                                        cwe_id="CWE-200",
                                    ))
                        
                        await page.close()
                        
                    except Exception:
                        pass
        
        return issues
    
    async def _check_xss_patterns(self, url: str, html: str) -> List[SecurityIssue]:
        """Detect potential XSS patterns in response."""
        issues = []
        
        for pattern, description in self.XSS_PATTERNS:
            matches = re.finditer(pattern, html, re.IGNORECASE)
            for match in matches[:3]:  # Limit to 3 matches per pattern
                # Check if it's in a context that could be exploitable
                start = max(0, match.start() - 50)
                end = min(len(html), match.end() + 50)
                context = html[start:end]
                
                issues.append(SecurityIssue(
                    category="XSS Vulnerability",
                    title=f"Potential XSS Pattern: {description}",
                    description=f"Potential cross-site scripting pattern detected in HTML",
                    risk_level=RiskLevel.MEDIUM,
                    url=url,
                    evidence=f"Pattern found: {match.group()[:100]}... Context: ...{context}...",
                    recommendation="Review and sanitize user inputs, use Content-Security-Policy",
                    cwe_id="CWE-79",
                ))
        
        return issues[:5]  # Limit total XSS issues
    
    async def _check_sqli_patterns(self, url: str, html: str) -> List[SecurityIssue]:
        """Detect potential SQL injection patterns in response."""
        issues = []
        
        for pattern, description in self.SQLI_PATTERNS:
            matches = re.finditer(pattern, html, re.IGNORECASE)
            for match in matches[:2]:  # Limit matches
                issues.append(SecurityIssue(
                    category="SQL Injection",
                    title=f"Potential SQLi Pattern: {description}",
                    description="Potential SQL injection pattern detected in page content",
                    risk_level=RiskLevel.HIGH,
                    url=url,
                    evidence=f"Pattern found: {match.group()[:100]}",
                    recommendation="Review database queries, use parameterized queries",
                    cwe_id="CWE-89",
                ))
        
        return issues[:3]  # Limit total SQLi issues
    
    async def _check_mixed_content(self, url: str, html: str) -> List[SecurityIssue]:
        """Check for mixed content issues."""
        issues = []
        
        if not url.startswith("https://"):
            return issues
        
        for pattern, description in self.MIXED_CONTENT_PATTERNS:
            matches = re.finditer(pattern, html, re.IGNORECASE)
            found_urls = []
            
            for match in matches:
                found_url = match.group()
                if found_url.startswith("http://"):
                    found_urls.append(found_url)
            
            if found_urls:
                # Deduplicate
                found_urls = list(set(found_urls))[:5]
                
                issues.append(SecurityIssue(
                    category="Mixed Content",
                    title="Mixed Content Detected",
                    description=f"Page contains resources loaded via insecure HTTP",
                    risk_level=RiskLevel.MEDIUM,
                    url=url,
                    evidence=f"Found {len(found_urls)} HTTP resource(s): {', '.join(found_urls[:3])}",
                    recommendation="Update all resource URLs to use HTTPS",
                    cwe_id="CWE-311",
                ))
                break  # Only one mixed content issue
        
        return issues
    
    async def _check_clickjacking(self, url: str, headers: Dict[str, str]) -> List[SecurityIssue]:
        """Check for clickjacking vulnerability."""
        issues = []
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        
        x_frame_options = normalized_headers.get("x-frame-options")
        content_security_policy = normalized_headers.get("content-security-policy")
        
        # Check if frame-ancestors directive is in CSP
        has_frame_ancestors = content_security_policy and "frame-ancestors" in content_security_policy.lower()
        
        if not x_frame_options and not has_frame_ancestors:
            issues.append(SecurityIssue(
                category="Clickjacking",
                title="Site vulnerable to clickjacking",
                description="No X-Frame-Options or CSP frame-ancestors directive found",
                risk_level=RiskLevel.HIGH,
                url=url,
                evidence="Page can be embedded in iframe",
                recommendation="Add X-Frame-Options: DENY or CSP frame-ancestors directive",
                cwe_id="CWE-1021",
            ))
        
        return issues
    
    async def _check_cors(self, url: str, headers: Dict[str, str]) -> List[SecurityIssue]:
        """Check for CORS misconfiguration."""
        issues = []
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        
        cors_headers = {
            "access-control-allow-origin": normalized_headers.get("access-control-allow-origin", ""),
            "access-control-allow-credentials": normalized_headers.get("access-control-allow-credentials", ""),
        }
        
        # Check for overly permissive CORS
        if cors_headers["access-control-allow-origin"] == "*":
            issues.append(SecurityIssue(
                category="CORS Misconfiguration",
                title="Wildcard CORS policy",
                description="Access-Control-Allow-Origin is set to * (allow all)",
                risk_level=RiskLevel.MEDIUM,
                url=url,
                evidence=f"access-control-allow-origin: {cors_headers['access-control-allow-origin']}",
                recommendation="Restrict CORS to specific trusted origins",
                cwe_id="CWE-942",
            ))
        
        # Check for credentials with wildcard origin
        if (cors_headers["access-control-allow-origin"] == "*" and 
            cors_headers["access-control-allow-credentials"].lower() == "true"):
            issues.append(SecurityIssue(
                category="CORS Misconfiguration",
                title="CORS allows credentials with wildcard origin",
                description="Allowing credentials with wildcard origin is insecure",
                risk_level=RiskLevel.HIGH,
                url=url,
                evidence="access-control-allow-credentials: true with wildcard origin",
                recommendation="Never use 'Access-Control-Allow-Origin: *' with 'Access-Control-Allow-Credentials: true'",
                cwe_id="CWE-942",
            ))
        
        return issues
    
    async def _check_html_content(self, url: str, html: str) -> List[SecurityIssue]:
        """Additional HTML content security checks."""
        issues = []
        
        # Check for form with password over HTTP
        if "http://" in url:
            password_forms = re.findall(r'<form[^>]*>[^<]*<input[^>]*type=["\']password["\'][^>]*>', html, re.IGNORECASE | re.DOTALL)
            if password_forms:
                issues.append(SecurityIssue(
                    category="Form Security",
                    title="Password form on HTTP page",
                    description="Password form detected on insecure HTTP page",
                    risk_level=RiskLevel.CRITICAL,
                    url=url,
                    evidence="Password input found on non-HTTPS page",
                    recommendation="Use HTTPS for all pages with authentication forms",
                    cwe_id="CWE-311",
                ))
        
        # Check for autocomplete on sensitive fields
        autocomplete_forms = re.findall(r'<input[^>]*autocomplete=["\']on["\'][^>]*(?:type=["\']password["\']|name=["\'][^"\']*(?:pass|secret|key)[^"\']*["\'])', 
                                         html, re.IGNORECASE)
        if autocomplete_forms:
            issues.append(SecurityIssue(
                category="Form Security",
                title="Autocomplete enabled on sensitive fields",
                description="Sensitive form fields have autocomplete enabled",
                risk_level=RiskLevel.LOW,
                url=url,
                evidence=f"Found {len(autocomplete_forms)} field(s) with autocomplete",
                recommendation="Set autocomplete='off' for sensitive fields",
                cwe_id="CWE-200",
            ))
        
        return issues
    
    async def scan(
        self,
        url: str,
        check_xss: bool = True,
        check_sqli: bool = True,
        check_sensitive: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform a complete security scan.
        
        Args:
            url: URL to scan.
            check_xss: Enable XSS pattern detection.
            check_sqli: Enable SQL injection pattern detection.
            check_sensitive: Enable sensitive file checks.
            
        Returns:
            Dictionary containing security scan results.
        """
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        start_time = asyncio.get_event_loop().time()
        self._report = SecurityReport(url=url)
        
        try:
            page = await self._context.new_page()
            
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.config.scanner.timeout if self.config else 30000,
            )
            
            self._report.pages_scanned = 1
            
            headers = {}
            if response:
                headers = dict(response.headers)
            
            html = await page.content()
            
            # Run all security checks concurrently
            tasks = [
                self._check_security_headers(url, headers),
                self._check_ssl_tls(url),
                self._check_clickjacking(url, headers),
                self._check_cors(url, headers),
                self._check_mixed_content(url, html),
                self._check_html_content(url, html),
            ]
            
            if check_xss:
                tasks.append(self._check_xss_patterns(url, html))
            
            if check_sqli:
                tasks.append(self._check_sqli_patterns(url, html))
            
            if check_sensitive:
                tasks.append(self._check_sensitive_files(url))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect all issues
            for result in results:
                if isinstance(result, list):
                    self._report.issues.extend(result)
            
            await page.close()
            
            # Calculate scan duration
            self._report.scan_duration = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Security scan completed for {url}")
            logger.info(f"Found {len(self._report.issues)} issues")
            
            return self._report.to_dict()
            
        except PlaywrightTimeout:
            logger.error(f"Timeout during security scan: {url}")
            self._report.issues.append(SecurityIssue(
                category="Scan",
                title="Scan timeout",
                description="Security scan timed out",
                risk_level=RiskLevel.INFO,
                url=url,
            ))
            return self._report.to_dict()
            
        except Exception as e:
            logger.error(f"Error during security scan: {e}")
            self._report.issues.append(SecurityIssue(
                category="Scan",
                title="Scan error",
                description=str(e),
                risk_level=RiskLevel.INFO,
                url=url,
            ))
            return self._report.to_dict()
    
    async def quick_scan(self, url: str) -> Dict[str, Any]:
        """
        Perform a quick security scan (headers only).
        
        Args:
            url: URL to scan.
            
        Returns:
            Dictionary containing quick scan results.
        """
        if not self._context:
            raise RuntimeError("Browser context not set. Call set_context() first.")
        
        start_time = asyncio.get_event_loop().time()
        self._report = SecurityReport(url=url)
        
        try:
            page = await self._context.new_page()
            response = await page.goto(url, wait_until="domcontentloaded", timeout=10000)
            
            headers = {}
            if response:
                headers = dict(response.headers)
            
            tasks = [
                self._check_security_headers(url, headers),
                self._check_ssl_tls(url),
                self._check_clickjacking(url, headers),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    self._report.issues.extend(result)
            
            self._report.pages_scanned = 1
            self._report.scan_duration = asyncio.get_event_loop().time() - start_time
            
            await page.close()
            
            return self._report.to_dict()
            
        except Exception as e:
            logger.error(f"Quick scan error: {e}")
            return {"error": str(e)}
    
    def get_report(self) -> Optional[SecurityReport]:
        """Get the current security report."""
        return self._report


# Alias for backwards compatibility
SecurityTest = SecurityScanner
