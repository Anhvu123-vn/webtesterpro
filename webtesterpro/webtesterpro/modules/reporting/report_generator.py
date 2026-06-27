"""
Report Generator Module

Provides comprehensive report generation using Jinja2:
- HTML reports with Bootstrap 5
- PDF export capabilities
- JSON export
- Dashboard summary with Chart.js
- Test history tracking
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from webtesterpro.core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    output_dir: str = "reports"
    template_name: str = "default"
    include_screenshots: bool = False
    include_charts: bool = True
    open_on_complete: bool = False
    pdf_enabled: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "output_dir": self.output_dir,
            "template_name": self.template_name,
            "include_screenshots": self.include_screenshots,
            "include_charts": self.include_charts,
            "open_on_complete": self.open_on_complete,
            "pdf_enabled": self.pdf_enabled,
        }


@dataclass
class ReportData:
    """
    Container for all report data.
    """
    url: str = ""
    test_name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Module results
    crawl_results: Dict[str, Any] = field(default_factory=dict)
    scan_results: Dict[str, Any] = field(default_factory=dict)
    seo_results: Dict[str, Any] = field(default_factory=dict)
    security_results: Dict[str, Any] = field(default_factory=dict)
    accessibility_results: Dict[str, Any] = field(default_factory=dict)
    performance_results: Dict[str, Any] = field(default_factory=dict)
    visual_results: Dict[str, Any] = field(default_factory=dict)
    
    # Summary scores
    overall_score: int = 0
    scores: Dict[str, int] = field(default_factory=dict)
    
    # Metadata
    test_duration: float = 0.0
    modules_run: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "test_name": self.test_name,
            "timestamp": self.timestamp.isoformat(),
            "crawl_results": self.crawl_results,
            "scan_results": self.scan_results,
            "seo_results": self.seo_results,
            "security_results": self.security_results,
            "accessibility_results": self.accessibility_results,
            "performance_results": self.performance_results,
            "visual_results": self.visual_results,
            "overall_score": self.overall_score,
            "scores": self.scores,
            "test_duration": self.test_duration,
            "modules_run": self.modules_run,
            "errors": self.errors,
        }


class ReportGenerator:
    """
    Report generator using Jinja2 templates.
    
    Generates comprehensive reports in multiple formats:
    - HTML with Bootstrap 5 styling
    - JSON for programmatic access
    - PDF (via HTML conversion)
    
    Usage:
        generator = ReportGenerator(config)
        generator.generate(data, format="html")
    """
    
    DEFAULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebTesterPro Report - {{ data.url }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background: #f8f9fa; }
        .report-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; margin-bottom: 2rem; }
        .score-card { border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .score-excellent { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
        .score-good { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .score-warning { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        .score-poor { background: linear-gradient(135deg, #ff0844 0%, #ffb199 100%); }
        .section-card { border-radius: 12px; margin-bottom: 1.5rem; }
        .badge-issue { font-size: 0.85rem; padding: 0.35em 0.65em; }
        .chart-container { position: relative; height: 300px; }
        .metric-value { font-size: 2.5rem; font-weight: bold; }
        .metric-label { font-size: 0.9rem; color: #6c757d; }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- Header -->
        <div class="report-header text-center">
            <div class="container">
                <h1 class="display-4 mb-2">WebTesterPro Report</h1>
                <p class="lead">{{ data.url }}</p>
                <p class="small mb-0">{{ data.timestamp }}</p>
            </div>
        </div>
        
        <div class="container">
            <!-- Score Overview -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card score-card text-white score-excellent h-100">
                        <div class="card-body text-center">
                            <div class="metric-value">{{ data.overall_score }}</div>
                            <div class="metric-label">Overall Score</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card score-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value">{{ data.scores|length }}</div>
                            <div class="metric-label">Modules Tested</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card score-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value">{{ "%.1f"|format(data.test_duration) }}s</div>
                            <div class="metric-label">Test Duration</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Score Breakdown Chart -->
            {% if data.scores and data.include_charts|default(true) %}
            <div class="card section-card mb-4">
                <div class="card-header bg-white">
                    <h5 class="mb-0">Score Breakdown</h5>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <canvas id="scoreChart"></canvas>
                    </div>
                </div>
            </div>
            {% endif %}
            
            <!-- Module Results -->
            <div class="row">
                <!-- SEO Results -->
                {% if data.seo_results and data.seo_results.scores %}
                <div class="col-lg-6 mb-4">
                    <div class="card section-card h-100">
                        <div class="card-header bg-white d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">SEO Analysis</h5>
                            <span class="badge bg-{{ 'success' if data.seo_results.scores.overall >= 80 else 'warning' if data.seo_results.scores.overall >= 60 else 'danger' }}">
                                {{ data.seo_results.scores.overall }}/100
                            </span>
                        </div>
                        <div class="card-body">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Title</span>
                                    <span>{{ data.seo_results.scores.title }}/100</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Meta Tags</span>
                                    <span>{{ data.seo_results.scores.meta_tags }}/100</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Headings</span>
                                    <span>{{ data.seo_results.scores.headings }}/100</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                {% endif %}
                
                <!-- Security Results -->
                {% if data.security_results and data.security_results.summary %}
                <div class="col-lg-6 mb-4">
                    <div class="card section-card h-100">
                        <div class="card-header bg-white d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Security Scan</h5>
                            <span class="badge bg-{{ 'success' if data.security_results.summary.risk_rating == 'SECURE' else 'danger' }}">
                                {{ data.security_results.summary.risk_rating }}
                            </span>
                        </div>
                        <div class="card-body">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Critical</span>
                                    <span class="badge bg-danger">{{ data.security_results.summary.critical }}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>High</span>
                                    <span class="badge bg-warning">{{ data.security_results.summary.high }}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Medium</span>
                                    <span class="badge bg-info">{{ data.security_results.summary.medium }}</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                {% endif %}
                
                <!-- Performance Results -->
                {% if data.performance_results and data.performance_results.web_vitals %}
                <div class="col-lg-6 mb-4">
                    <div class="card section-card h-100">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Performance</h5>
                        </div>
                        <div class="card-body">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>LCP</span>
                                    <span>{{ data.performance_results.web_vitals.lcp_ms|int }}ms</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>CLS</span>
                                    <span>{{ data.performance_results.web_vitals.cls }}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>FID</span>
                                    <span>{{ data.performance_results.web_vitals.fid_ms|int }}ms</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                {% endif %}
                
                <!-- Accessibility Results -->
                {% if data.accessibility_results and data.accessibility_results.summary %}
                <div class="col-lg-6 mb-4">
                    <div class="card section-card h-100">
                        <div class="card-header bg-white d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Accessibility</h5>
                            <span class="badge bg-{{ 'success' if data.accessibility_results.summary.accessibility_score >= 80 else 'warning' if data.accessibility_results.summary.accessibility_score >= 50 else 'danger' }}">
                                {{ data.accessibility_results.summary.accessibility_score }}/100
                            </span>
                        </div>
                        <div class="card-body">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Violations</span>
                                    <span>{{ data.accessibility_results.summary.total_violations }}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Conformance</span>
                                    <span>{{ data.accessibility_results.summary.conformance_level }}</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>
            
            <!-- Footer -->
            <div class="text-center text-muted py-4">
                <p class="mb-0">Generated by WebTesterPro</p>
                <small>{{ data.timestamp }}</small>
            </div>
        </div>
    </div>
    
    {% if data.scores and data.include_charts|default(true) %}
    <script>
        // Score breakdown chart
        const ctx = document.getElementById('scoreChart').getContext('2d');
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys({{ data.scores|tojson }}),
                datasets: [{
                    label: 'Score',
                    data: Object.values({{ data.scores|tojson }}),
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    </script>
    {% endif %}
</body>
</html>
"""
    
    def __init__(self, config: Config = None, output_dir: str = "reports"):
        """
        Initialize the report generator.
        
        Args:
            config: Configuration object.
            output_dir: Directory to save reports.
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(searchpath=[str(self.output_dir)]),
            autoescape=select_autoescape(['html', 'xml']),
        )
        
        # Register template
        self.env.template_string = self.DEFAULT_TEMPLATE
        
        # History file
        self.history_file = self.output_dir / "history.json"
    
    def _get_score_color(self, score: int) -> str:
        """Get color class based on score."""
        if score >= 90:
            return "success"
        elif score >= 70:
            return "info"
        elif score >= 50:
            return "warning"
        return "danger"
    
    def _get_risk_color(self, rating: str) -> str:
        """Get color class based on risk rating."""
        rating = rating.upper()
        if rating == "SECURE":
            return "success"
        elif rating == "LOW":
            return "info"
        elif rating == "MEDIUM":
            return "warning"
        elif rating == "HIGH":
            return "danger"
        return "dark"
    
    def _calculate_overall_score(self, data: ReportData) -> int:
        """Calculate overall score from all module results."""
        scores = []
        
        # SEO score
        if data.seo_results and "scores" in data.seo_results:
            scores.append(data.seo_results["scores"].get("overall", 0))
        
        # Performance score
        if data.performance_results and "scores" in data.performance_results:
            scores.append(data.performance_results["scores"].get("overall", 0))
        
        # Accessibility score
        if data.accessibility_results and "summary" in data.accessibility_results:
            scores.append(data.accessibility_results["summary"].get("accessibility_score", 0))
        
        # Security inverse score (100 - risk penalty)
        if data.security_results and "summary" in data.security_results:
            summary = data.security_results["summary"]
            penalty = (summary.get("critical", 0) * 30 + 
                      summary.get("high", 0) * 20 + 
                      summary.get("medium", 0) * 10)
            scores.append(max(0, 100 - penalty))
        
        # Crawl coverage
        if data.crawl_results and "stats" in data.crawl_results:
            stats = data.crawl_results["stats"]
            pages = stats.get("total_pages", 0)
            success_rate = stats.get("successful_pages", 0) / max(pages, 1)
            scores.append(int(success_rate * 100))
        
        return int(sum(scores) / len(scores)) if scores else 0
    
    def _extract_scores(self, data: ReportData) -> Dict[str, int]:
        """Extract individual module scores."""
        scores = {}
        
        if data.seo_results and "scores" in data.seo_results:
            scores["SEO"] = data.seo_results["scores"].get("overall", 0)
        
        if data.performance_results and "scores" in data.performance_results:
            scores["Performance"] = data.performance_results["scores"].get("overall", 0)
        
        if data.accessibility_results and "summary" in data.accessibility_results:
            scores["Accessibility"] = data.accessibility_results["summary"].get("accessibility_score", 0)
        
        if data.security_results and "summary" in data.security_results:
            summary = data.security_results["summary"]
            penalty = (summary.get("critical", 0) * 30 + 
                      summary.get("high", 0) * 20 + 
                      summary.get("medium", 0) * 10)
            scores["Security"] = max(0, 100 - penalty)
        
        return scores
    
    def generate_html(self, data: ReportData) -> str:
        """
        Generate HTML report.
        
        Args:
            data: Report data.
            
        Returns:
            Path to generated HTML file.
        """
        # Calculate scores
        data.overall_score = self._calculate_overall_score(data)
        data.scores = self._extract_scores(data)
        
        # Prepare template context
        context = {
            "data": {
                "url": data.url,
                "test_name": data.test_name,
                "timestamp": data.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "overall_score": data.overall_score,
                "scores": data.scores,
                "test_duration": data.test_duration,
                "modules_run": data.modules_run,
                "crawl_results": data.crawl_results,
                "scan_results": data.scan_results,
                "seo_results": data.seo_results,
                "security_results": data.security_results,
                "accessibility_results": data.accessibility_results,
                "performance_results": data.performance_results,
                "visual_results": data.visual_results,
                "include_charts": True,
            }
        }
        
        # Render template
        template = self.env.from_string(self.DEFAULT_TEMPLATE)
        html_content = template.render(**context)
        
        # Save HTML file
        timestamp_str = data.timestamp.strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() else "_" for c in data.url.replace("https://", "").replace("http://", ""))
        filename = f"report_{safe_name}_{timestamp_str}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {filepath}")
        
        return str(filepath)
    
    def generate_json(self, data: ReportData) -> str:
        """
        Generate JSON report.
        
        Args:
            data: Report data.
            
        Returns:
            Path to generated JSON file.
        """
        data_dict = data.to_dict()
        
        # Calculate scores
        data_dict["overall_score"] = self._calculate_overall_score(data)
        data_dict["scores"] = self._extract_scores(data)
        
        # Save JSON file
        timestamp_str = data.timestamp.strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() else "_" for c in data.url.replace("https://", "").replace("http://", ""))
        filename = f"report_{safe_name}_{timestamp_str}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=2, default=str)
        
        logger.info(f"JSON report generated: {filepath}")
        
        return str(filepath)
    
    def generate_pdf(self, data: ReportData) -> Optional[str]:
        """
        Generate PDF report.
        
        Args:
            data: Report data.
            
        Returns:
            Path to generated PDF file, or None if weasyprint not available.
        """
        # First generate HTML
        html_path = self.generate_html(data)
        
        try:
            from weasyprint import HTML
            from weasyprint.text.fonts import FontConfiguration
            
            # Convert HTML to PDF
            timestamp_str = data.timestamp.strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c if c.isalnum() else "_" for c in data.url.replace("https://", "").replace("http://", ""))
            pdf_filename = f"report_{safe_name}_{timestamp_str}.pdf"
            pdf_path = self.output_dir / pdf_filename
            
            font_config = FontConfiguration()
            HTML(html_path).write_pdf(
                pdf_path,
                font_config=font_config,
                presentational_hints=True,
            )
            
            logger.info(f"PDF report generated: {pdf_path}")
            return str(pdf_path)
            
        except ImportError:
            logger.warning("weasyprint not installed, PDF generation skipped")
            return html_path  # Return HTML path as fallback
    
    def generate(
        self,
        data: ReportData,
        formats: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Generate reports in multiple formats.
        
        Args:
            data: Report data.
            formats: List of formats to generate ("html", "json", "pdf").
                    Defaults to ["html", "json"].
            
        Returns:
            Dictionary mapping format to file path.
        """
        if formats is None:
            formats = ["html", "json"]
        
        results = {}
        
        for fmt in formats:
            if fmt.lower() == "html":
                results["html"] = self.generate_html(data)
            elif fmt.lower() == "json":
                results["json"] = self.generate_json(data)
            elif fmt.lower() == "pdf":
                results["pdf"] = self.generate_pdf(data)
        
        # Save to history
        self._save_history(data)
        
        return results
    
    def _save_history(self, data: ReportData) -> None:
        """Save test results to history."""
        history = self.get_history()
        
        # Calculate scores
        overall_score = self._calculate_overall_score(data)
        scores = self._extract_scores(data)
        
        entry = {
            "id": len(history) + 1,
            "url": data.url,
            "test_name": data.test_name,
            "timestamp": data.timestamp.isoformat(),
            "overall_score": overall_score,
            "scores": scores,
            "test_duration": data.test_duration,
            "modules_run": data.modules_run,
        }
        
        history.append(entry)
        
        # Keep only last 100 entries
        history = history[-100:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"History saved: {len(history)} entries")
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get test history.
        
        Args:
            limit: Maximum number of entries to return.
            
        Returns:
            List of historical test entries.
        """
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            return history[-limit:]
        except Exception as e:
            logger.error(f"Error reading history: {e}")
            return []
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for dashboard visualization.
        
        Returns:
            Dictionary with dashboard data including trends and statistics.
        """
        history = self.get_history(limit=100)
        
        if not history:
            return {
                "total_tests": 0,
                "average_score": 0,
                "trend": [],
                "by_module": {},
            }
        
        # Calculate statistics
        total_tests = len(history)
        average_score = sum(h.get("overall_score", 0) for h in history) / total_tests
        
        # Trend data (last 10 tests)
        trend = [
            {
                "x": i,
                "y": h.get("overall_score", 0),
                "label": h.get("url", "")[:30],
                "timestamp": h.get("timestamp", ""),
            }
            for i, h in enumerate(history[-10:])
        ]
        
        # Module averages
        by_module = {}
        for entry in history:
            for module, score in entry.get("scores", {}).items():
                if module not in by_module:
                    by_module[module] = []
                by_module[module].append(score)
        
        module_averages = {
            module: sum(scores) / len(scores) if scores else 0
            for module, scores in by_module.items()
        }
        
        return {
            "total_tests": total_tests,
            "average_score": round(average_score, 1),
            "trend": trend,
            "by_module": module_averages,
            "latest_test": history[-1] if history else None,
            "history": history[-20:],  # Last 20 for table display
        }
    
    def generate_dashboard(self) -> str:
        """
        Generate dashboard HTML page.
        
        Returns:
            Path to generated dashboard HTML file.
        """
        dashboard_data = self.get_dashboard_data()
        
        template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebTesterPro Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background: #f5f5f5; }
        .stat-card { border-radius: 12px; transition: transform 0.2s; }
        .stat-card:hover { transform: translateY(-5px); }
        .chart-container { position: relative; height: 300px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand mb-0 h1">WebTesterPro Dashboard</span>
        </div>
    </nav>
    
    <div class="container py-4">
        <!-- Stats Cards -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card stat-card bg-primary text-white">
                    <div class="card-body text-center">
                        <h3 class="mb-0">{{ dashboard.total_tests }}</h3>
                        <small>Total Tests</small>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stat-card bg-success text-white">
                    <div class="card-body text-center">
                        <h3 class="mb-0">{{ dashboard.average_score }}%</h3>
                        <small>Average Score</small>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stat-card bg-info text-white">
                    <div class="card-body text-center">
                        <h3 class="mb-0">{{ dashboard.by_module|length }}</h3>
                        <small>Modules Tracked</small>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="row mb-4">
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Score Trend</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="trendChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Module Performance</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="moduleChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Recent Tests -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Recent Tests</h5>
            </div>
            <div class="card-body">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>URL</th>
                            <th>Score</th>
                            <th>Modules</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for test in dashboard.history %}
                        <tr>
                            <td><small>{{ test.url[:50] }}</small></td>
                            <td>
                                <span class="badge bg-{{ 'success' if test.overall_score >= 80 else 'warning' if test.overall_score >= 60 else 'danger' }}">
                                    {{ test.overall_score }}
                                </span>
                            </td>
                            <td>{{ test.scores|length }}</td>
                            <td><small>{{ test.timestamp[:10] }}</small></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        // Trend Chart
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: [{% for t in dashboard.trend %}'{{ t.label }}'{% if not loop.last %}, {% endif %}{% endfor %}],
                datasets: [{
                    label: 'Score',
                    data: [{% for t in dashboard.trend %}{{ t.y }}{% if not loop.last %}, {% endif %}{% endfor %}],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.3,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
        
        // Module Chart
        const moduleCtx = document.getElementById('moduleChart').getContext('2d');
        new Chart(moduleCtx, {
            type: 'bar',
            data: {
                labels: {{ dashboard.by_module.keys()|list|tojson }},
                datasets: [{
                    label: 'Avg Score',
                    data: {{ dashboard.by_module.values()|list|tojson }},
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, max: 100 } }
            }
        });
    </script>
</body>
</html>
"""
        
        env = Environment(autoescape=select_autoescape(['html', 'xml']))
        template = env.from_string(template)
        html_content = template.render(dashboard=dashboard_data)
        
        filepath = self.output_dir / "dashboard.html"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Dashboard generated: {filepath}")
        return str(filepath)
    
    def list_reports(self) -> List[Dict[str, str]]:
        """
        List all generated reports.
        
        Returns:
            List of report information.
        """
        reports = []
        
        for filepath in self.output_dir.glob("report_*.html"):
            reports.append({
                "type": "html",
                "filename": filepath.name,
                "path": str(filepath),
                "size": filepath.stat().st_size,
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            })
        
        for filepath in self.output_dir.glob("report_*.json"):
            reports.append({
                "type": "json",
                "filename": filepath.name,
                "path": str(filepath),
                "size": filepath.stat().st_size,
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            })
        
        for filepath in self.output_dir.glob("report_*.pdf"):
            reports.append({
                "type": "pdf",
                "filename": filepath.name,
                "path": str(filepath),
                "size": filepath.stat().st_size,
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            })
        
        return sorted(reports, key=lambda x: x["modified"], reverse=True)
