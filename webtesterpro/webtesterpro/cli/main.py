"""
WebTesterPro CLI Module

Command-line interface for WebTesterPro.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from webtesterpro.core.engine import WebTesterEngine
from webtesterpro.core.config import Config

console = Console()


def setup_logging(level: str = "INFO") -> None:
    """Setup logging with rich handler."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@click.group()
@click.version_option(version="0.1.0")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool) -> None:
    """WebTesterPro - All-in-One Website Testing Tool"""
    ctx.ensure_object(dict)
    
    level = "DEBUG" if verbose else "INFO"
    setup_logging(level)
    
    if config:
        ctx.obj["config"] = Config.from_yaml(config)
    else:
        ctx.obj["config"] = Config.load_default()


@cli.command()
@click.argument("url")
@click.option("--max-depth", "-d", type=int, default=None, help="Maximum crawl depth")
@click.option("--max-pages", "-m", type=int, default=None, help="Maximum pages to crawl")
@click.option("--output", "-o", type=click.Path(), help="Output file for results (JSON)")
@click.option("--no-robots", is_flag=True, help="Ignore robots.txt")
@click.pass_context
async def crawl(ctx: click.Context, url: str, max_depth: Optional[int], 
                max_pages: Optional[int], output: Optional[str], no_robots: bool) -> None:
    """Crawl a website."""
    config = ctx.obj["config"]
    
    if no_robots:
        config.crawler.respect_robots_txt = False
    
    console.print(f"[bold blue]Crawling:[/bold blue] {url}")
    
    async with WebTesterEngine(config) as engine:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Crawling...", total=None)
            
            results = await engine.crawl_site(url, max_depth, max_pages)
            
            progress.update(task, completed=True)
        
        stats = results.get("stats", {})
        
        table = Table(title="Crawl Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Pages", str(stats.get("total_pages", 0)))
        table.add_row("Successful", str(stats.get("successful_pages", 0)))
        table.add_row("Failed", str(stats.get("failed_pages", 0)))
        table.add_row("Total Links", str(stats.get("total_links", 0)))
        table.add_row("Duration", f"{stats.get('duration_seconds', 0):.2f}s")
        
        console.print(table)
        
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"[green]Results saved to:[/green] {output_path}")


@cli.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output file for results (JSON)")
@click.pass_context
async def scan(ctx: click.Context, url: str, output: Optional[str]) -> None:
    """Scan a website for forms, links, and resources."""
    config = ctx.obj["config"]
    
    console.print(f"[bold blue]Scanning:[/bold blue] {url}")
    
    async with WebTesterEngine(config) as engine:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning...", total=None)
            
            results = await engine.scan_site(url)
            
            progress.update(task, completed=True)
        
        summary = results.get("summary", {})
        
        table = Table(title="Scan Results")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="green")
        
        table.add_row("Forms", str(summary.get("total_forms", 0)))
        table.add_row("Links", str(summary.get("total_links", 0)))
        table.add_row("Resources", str(summary.get("total_resources", 0)))
        
        console.print(table)
        
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"[green]Results saved to:[/green] {output_path}")


@cli.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output file for results (JSON)")
@click.pass_context
async def analyze(ctx: click.Context, url: str, output: Optional[str]) -> None:
    """Analyze a website for SEO, performance, and security."""
    config = ctx.obj["config"]
    
    console.print(f"[bold blue]Analyzing:[/bold blue] {url}")
    
    async with WebTesterEngine(config) as engine:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing...", total=None)
            
            results = await engine.analyze_site(url)
            
            progress.update(task, completed=True)
        
        summary = results.get("summary", {})
        
        table = Table(title="Analysis Results")
        table.add_column("Category", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Issues", style="yellow")
        
        table.add_row(
            "SEO", 
            f"{summary.get('seo_score', 0)}%", 
            str(len(results.get("seo", {}).get("issues", [])))
        )
        table.add_row(
            "Performance", 
            f"{summary.get('performance_score', 0)}%", 
            str(len(results.get("performance", {}).get("issues", [])))
        )
        table.add_row(
            "Security", 
            f"{summary.get('security_score', 0)}%", 
            str(len(results.get("security", {}).get("issues", [])))
        )
        
        console.print(table)
        
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"[green]Results saved to:[/green] {output_path}")


@cli.command()
@click.argument("url")
@click.option("--interval", "-i", type=int, default=None, help="Check interval in seconds")
@click.option("--duration", "-t", type=int, default=60, help="Monitoring duration in seconds")
@click.option("--output", "-o", type=click.Path(), help="Output file for results (JSON)")
@click.pass_context
async def monitor(ctx: click.Context, url: str, interval: Optional[int],
                  duration: int, output: Optional[str]) -> None:
    """Monitor a website for uptime."""
    config = ctx.obj["config"]
    
    console.print(f"[bold blue]Monitoring:[/bold blue] {url}")
    console.print(f"[dim]Duration: {duration}s, Interval: {interval or config.monitor.interval}s[/dim]")
    
    async with WebTesterEngine(config) as engine:
        results = await engine.monitor_site(url, interval, duration)
        
        table = Table(title="Monitoring Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Uptime", f"{results.get('uptime_percentage', 0):.2f}%")
        table.add_row("Total Checks", str(results.get("total_checks", 0)))
        table.add_row("Successful", str(results.get("successful_checks", 0)))
        table.add_row("Failed", str(results.get("failed_checks", 0)))
        table.add_row("Avg Response Time", f"{results.get('avg_response_time_seconds', 0):.3f}s")
        
        console.print(table)
        
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"[green]Results saved to:[/green] {output_path}")


@cli.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output file for results (JSON)")
@click.option("--wait", "-w", type=click.Choice(["load", "domcontentloaded", "networkidle"]),
              default="networkidle", help="Wait until which event")
@click.pass_context
async def perf(ctx: click.Context, url: str, output: Optional[str],
               wait: str) -> None:
    """Test website performance (Core Web Vitals, LCP, CLS, FID, TTFB...)."""
    config = ctx.obj["config"]
    
    console.print(f"[bold blue]Performance Test:[/bold blue] {url}")
    
    async with WebTesterEngine(config) as engine:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Testing performance...", total=None)
            
            results = await engine.test_performance(url, wait_until=wait)
            
            progress.update(task, completed=True)
        
        web_vitals = results.get("web_vitals", {})
        resources = results.get("resources", {})
        
        # Display Core Web Vitals
        table = Table(title="Core Web Vitals")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")
        
        # LCP
        lcp = web_vitals.get("lcp_ms", 0)
        lcp_status = "good" if lcp < 2500 else "needs_improvement" if lcp < 4000 else "poor"
        table.add_row("LCP (Largest Contentful Paint)", f"{lcp:.0f}ms", lcp_status)
        
        # CLS
        cls = web_vitals.get("cls", 0)
        cls_status = "good" if cls < 0.1 else "needs_improvement" if cls < 0.25 else "poor"
        table.add_row("CLS (Cumulative Layout Shift)", f"{cls:.4f}", cls_status)
        
        # FID
        fid = web_vitals.get("fid_ms", 0)
        fid_status = "good" if fid < 100 else "needs_improvement" if fid < 300 else "poor"
        table.add_row("FID (First Input Delay)", f"{fid:.0f}ms", fid_status)
        
        # TTFB
        ttfb = web_vitals.get("ttfb_ms", 0)
        ttfb_status = "good" if ttfb < 800 else "needs_improvement" if ttfb < 1800 else "poor"
        table.add_row("TTFB (Time to First Byte)", f"{ttfb:.0f}ms", ttfb_status)
        
        # FCP
        fcp = web_vitals.get("fcp_ms", 0)
        fcp_status = "good" if fcp < 1800 else "needs_improvement" if fcp < 3000 else "poor"
        table.add_row("FCP (First Contentful Paint)", f"{fcp:.0f}ms", fcp_status)
        
        console.print(table)
        
        # Display Resource Metrics
        res_summary = resources.get("summary", {})
        res_table = Table(title="Resource Metrics")
        res_table.add_column("Metric", style="cyan")
        res_table.add_column("Value", style="green")
        
        res_table.add_row("Total Requests", str(res_summary.get("total_requests", 0)))
        res_table.add_row("Total Size", f"{res_summary.get('total_size_kb', 0):.1f} KB")
        res_table.add_row("Failed Requests", str(res_summary.get("failed_requests", 0)))
        
        console.print(res_table)
        
        # Display Score
        score = results.get("scores", {}).get("overall", 0)
        console.print(f"[bold]Overall Performance Score:[/bold] {score:.0f}/100")
        
        # Display Warnings
        warnings = results.get("warnings", [])
        if warnings:
            console.print("\n[yellow]Recommendations:[/yellow]")
            for warning in warnings[:3]:
                console.print(f"  - {warning}")
        
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"\n[green]Results saved to:[/green] {output_path}")


@cli.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output file for results (JSON)")
@click.option("--no-xss", is_flag=True, help="Skip XSS pattern detection")
@click.option("--no-sqli", is_flag=True, help="Skip SQL injection detection")
@click.option("--no-sensitive", is_flag=True, help="Skip sensitive file checks")
@click.pass_context
async def security(ctx: click.Context, url: str, output: Optional[str],
                   no_xss: bool, no_sqli: bool, no_sensitive: bool) -> None:
    """Scan website for security vulnerabilities."""
    config = ctx.obj["config"]
    
    console.print(f"[bold blue]Security Scan:[/bold blue] {url}")
    
    async with WebTesterEngine(config) as engine:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning for vulnerabilities...", total=None)
            
            results = await engine.scan_security(
                url,
                check_xss=not no_xss,
                check_sqli=not no_sqli,
                check_sensitive=not no_sensitive,
            )
            
            progress.update(task, completed=True)
        
        summary = results.get("summary", {})
        
        # Display Risk Summary
        rating = summary.get("risk_rating", "UNKNOWN")
        rating_color = {
            "CRITICAL": "red",
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "green",
            "SECURE": "green",
        }.get(rating, "white")
        
        console.print(f"\n[bold]Risk Rating:[/bold] [{rating_color}]{rating}[/{rating_color}]")
        console.print(f"[bold]Risk Score:[/bold] {summary.get('overall_risk_score', 0)}/100")
        
        # Display Issue Counts
        counts_table = Table(title="Issues by Severity")
        counts_table.add_column("Severity", style="cyan")
        counts_table.add_column("Count", style="green")
        
        counts_table.add_row("Critical", str(summary.get("critical", 0)))
        counts_table.add_row("High", str(summary.get("high", 0)))
        counts_table.add_row("Medium", str(summary.get("medium", 0)))
        counts_table.add_row("Low", str(summary.get("low", 0)))
        counts_table.add_row("Info", str(summary.get("info", 0)))
        
        console.print(counts_table)
        
        # Display Issues by Category
        issues = results.get("issues", [])
        if issues:
            cat_table = Table(title="Issues by Category")
            cat_table.add_column("Category", style="cyan")
            cat_table.add_column("Count", style="green")
            
            categories = {}
            for issue in issues:
                cat = issue.get("category", "Unknown")
                categories[cat] = categories.get(cat, 0) + 1
            
            for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
                cat_table.add_row(cat, str(count))
            
            console.print(cat_table)
            
            # Display top issues
            console.print("\n[yellow]Top Issues:[/yellow]")
            for issue in issues[:5]:
                risk = issue.get("risk_level", "Unknown")
                risk_color = {
                    "Critical": "red",
                    "High": "red",
                    "Medium": "yellow",
                    "Low": "green",
                    "Info": "blue",
                }.get(risk, "white")
                
                console.print(f"  [{risk_color}]{risk}[/{risk_color}] - {issue.get('title', 'Unknown')}")
        
        # Display scan info
        metadata = results.get("metadata", {})
        console.print(f"\n[dim]Scan completed in {metadata.get('scan_duration_seconds', 0):.2f}s[/dim]")
        
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"[green]Results saved to:[/green] {output_path}")


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output file (JSON)")
@click.pass_context
async def info(ctx: click.Context, output: Optional[str]) -> None:
    """Show WebTesterPro configuration."""
    config = ctx.obj["config"]
    
    table = Table(title="WebTesterPro Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Version", "0.1.0")
    table.add_row("Crawler Max Depth", str(config.crawler.max_depth))
    table.add_row("Crawler Max Pages", str(config.crawler.max_pages))
    table.add_row("Crawler Delay", f"{config.crawler.delay_min}-{config.crawler.delay_max}s")
    table.add_row("Respect robots.txt", str(config.crawler.respect_robots_txt))
    
    console.print(table)
    
    if output:
        output_path = Path(output)
        with open(output_path, "w") as f:
            json.dump(config.to_dict(), f, indent=2, default=str)
        console.print(f"[green]Config saved to:[/green] {output_path}")


@cli.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output file for results (JSON)")
@click.option("--no-axe", is_flag=True, help="Skip axe-core automated checks")
@click.pass_context
async def a11y(ctx: click.Context, url: str, output: Optional[str],
               no_axe: bool) -> None:
    """Check website accessibility (WCAG 2.1/2.2 AA)."""
    config = ctx.obj["config"]
    
    console.print(f"[bold blue]Accessibility Check:[/bold blue] {url}")
    
    async with WebTesterEngine(config) as engine:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running accessibility checks...", total=None)
            
            results = await engine.check_accessibility(
                url,
                run_axe=not no_axe,
                run_manual=True,
            )
            
            progress.update(task, completed=True)
        
        summary = results.get("summary", {})
        page_info = results.get("page_info", {})
        
        # Display Accessibility Score
        score = summary.get("accessibility_score", 0)
        score_color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
        
        console.print(f"\n[bold]Accessibility Score:[/bold] [{score_color}]{score}/100[/{score_color}]")
        
        # Display Conformance Level
        level = summary.get("conformance_level", "Unknown")
        level_color = "green" if level in ["AA", "AAA"] else "yellow" if level == "A" else "red"
        console.print(f"[bold]WCAG Conformance:[/bold] [{level_color}]{level}[/{level_color}]")
        
        # Display Issue Counts
        counts_table = Table(title="Issues by Severity")
        counts_table.add_column("Severity", style="cyan")
        counts_table.add_column("Count", style="green")
        
        counts_table.add_row("Critical", str(summary.get("critical", 0)))
        counts_table.add_row("Serious", str(summary.get("serious", 0)))
        counts_table.add_row("Moderate", str(summary.get("moderate", 0)))
        counts_table.add_row("Minor", str(summary.get("minor", 0)))
        
        console.print(counts_table)
        
        # Display Page Info
        info_table = Table(title="Page Information")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="green")
        
        info_table.add_row("Title", page_info.get("title", "No title")[:50] or "No title")
        info_table.add_row("Has Title", "Yes" if page_info.get("has_title") else "No")
        info_table.add_row("Has Lang", "Yes" if page_info.get("has_lang") else "No")
        info_table.add_row("Total Elements", str(page_info.get("total_elements", 0)))
        
        console.print(info_table)
        
        # Display Issues by Rule
        issues = results.get("issues", [])
        if issues:
            rule_table = Table(title="Top Issues")
            rule_table.add_column("Rule ID", style="cyan")
            rule_table.add_column("Impact", style="yellow")
            rule_table.add_column("WCAG", style="green")
            rule_table.add_column("Description", style="white")
            
            for issue in issues[:8]:
                impact = issue.get("impact", "unknown")
                wcag = issue.get("wcag_criterion", "-")
                desc = issue.get("description", "")[:50]
                
                rule_table.add_row(
                    issue.get("rule_id", "")[:25],
                    impact.upper(),
                    wcag,
                    desc + "..." if len(desc) >= 50 else desc,
                )
            
            console.print(rule_table)
        
        # Display scan info
        metadata = results.get("metadata", {})
        console.print(f"\n[dim]Scan completed in {metadata.get('scan_duration_seconds', 0):.2f}s[/dim]")
        
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"[green]Results saved to:[/green] {output_path}")


@cli.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output file for results (JSON)")
@click.option("--keyword-density", is_flag=True, help="Include keyword density analysis")
@click.pass_context
async def seo(ctx: click.Context, url: str, output: Optional[str],
               keyword_density: bool) -> None:
    """Analyze website SEO (title, meta, headings, schema, images...)."""
    config = ctx.obj["config"]
    
    console.print(f"[bold blue]SEO Analysis:[/bold blue] {url}")
    
    async with WebTesterEngine(config) as engine:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing SEO...", total=None)
            
            results = await engine.analyze_seo(
                url,
                check_keyword_density=keyword_density,
            )
            
            progress.update(task, completed=True)
        
        scores = results.get("scores", {})
        summary = results.get("summary", {})
        page_info = results.get("page_info", {})
        headings = results.get("headings", {})
        links = results.get("links", {})
        images = results.get("images", {})
        social = results.get("social", {})
        schema = results.get("schema", {})
        
        # Display SEO Score
        score = scores.get("overall", 0)
        score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        
        console.print(f"\n[bold]SEO Score:[/bold] [{score_color}]{score}/100[/{score_color}]")
        
        # Display Score Breakdown
        score_table = Table(title="Score Breakdown")
        score_table.add_column("Category", style="cyan")
        score_table.add_column("Score", style="green")
        
        score_table.add_row("Title", f"{scores.get('title', 0)}/100")
        score_table.add_row("Meta Tags", f"{scores.get('meta_tags', 0)}/100")
        score_table.add_row("Headings", f"{scores.get('headings', 0)}/100")
        score_table.add_row("Content", f"{scores.get('content', 0)}/100")
        score_table.add_row("Images", f"{scores.get('images', 0)}/100")
        score_table.add_row("Links", f"{scores.get('links', 0)}/100")
        score_table.add_row("Technical", f"{scores.get('technical', 0)}/100")
        
        console.print(score_table)
        
        # Display Page Info
        info_table = Table(title="Page Information")
        info_table.add_column("Element", style="cyan")
        info_table.add_column("Value", style="white")
        
        title = page_info.get("title", "No title")
        info_table.add_row("Title", title[:60] + "..." if len(title) > 60 else title)
        
        desc = page_info.get("meta_description", "No description")
        info_table.add_row("Description", desc[:80] + "..." if len(desc) > 80 else desc)
        
        info_table.add_row("H1 Count", str(headings.get("total_h1", 0)))
        info_table.add_row("H2 Count", str(headings.get("total_h2", 0)))
        info_table.add_row("Word Count", str(summary.get("word_count", 0)))
        
        console.print(info_table)
        
        # Display Social & Schema
        og_tags = social.get("open_graph", {})
        twitter_tags = social.get("twitter", {})
        
        social_table = Table(title="Social & Structured Data")
        social_table.add_column("Type", style="cyan")
        social_table.add_column("Status", style="green")
        
        social_table.add_row("Open Graph", "Present" if og_tags else "Missing")
        social_table.add_row("Twitter Cards", "Present" if twitter_tags else "Missing")
        social_table.add_row("Schema.org", f"{schema.get('count', 0)} type(s)")
        
        console.print(social_table)
        
        # Display Issues
        issues = results.get("issues", [])
        if issues:
            issue_table = Table(title=f"Issues ({len(issues)} found)")
            issue_table.add_column("Impact", style="yellow")
            issue_table.add_column("Category", style="cyan")
            issue_table.add_column("Issue", style="white")
            
            for issue in issues[:8]:
                impact = issue.get("impact", "unknown")
                impact_color = "red" if impact == "high" else "yellow" if impact == "medium" else "green"
                
                issue_table.add_row(
                    f"[{impact_color}]{impact.upper()}[/{impact_color}]",
                    issue.get("category", ""),
                    issue.get("title", "")[:50],
                )
            
            console.print(issue_table)
        
        # Display scan info
        metadata = results.get("metadata", {})
        console.print(f"\n[dim]Analysis completed in {metadata.get('scan_duration_seconds', 0):.2f}s[/dim]")
        
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"[green]Results saved to:[/green] {output_path}")


@cli.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output directory for screenshots")
@click.option("--viewport", "-v", type=click.Choice([
    "desktop", "laptop", "tablet-landscape", "tablet-portrait",
    "mobile-landscape", "mobile-portrait"
]), default="desktop", help="Viewport size")
@click.option("--full-page", is_flag=True, help="Capture full scrollable page")
@click.pass_context
async def screenshot(ctx: click.Context, url: str, output: Optional[str],
                     viewport: str, full_page: bool) -> None:
    """Capture screenshots of a website."""
    from webtesterpro.modules.visual.visual_tester import Viewport, VisualTester
    
    config = ctx.obj["config"]
    baseline_dir = output or "screenshots"
    
    console.print(f"[bold blue]Screenshot:[/bold blue] {url}")
    console.print(f"[dim]Viewport: {viewport}, Full page: {full_page}[/dim]")
    
    viewport_map = {
        "desktop": Viewport.desktop,
        "laptop": Viewport.laptop,
        "tablet-landscape": Viewport.tablet_landscape,
        "tablet-portrait": Viewport.tablet_portrait,
        "mobile-landscape": Viewport.mobile_landscape,
        "mobile-portrait": Viewport.mobile_portrait,
    }
    
    async with WebTesterEngine(config) as engine:
        tester = VisualTester(baseline_dir=baseline_dir)
        tester.set_context(engine._context)
        
        vp = viewport_map[viewport]()
        result = await tester.screenshot(url, vp, full_page=full_page)
        
        if result.success:
            console.print(f"\n[green]Screenshot captured successfully![/green]")
            
            table = Table(title="Screenshot Info")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("URL", result.url)
            table.add_row("Viewport", f"{result.viewport.width}x{result.viewport.height}")
            table.add_row("File Size", f"{result.file_size / 1024:.1f} KB")
            table.add_row("Hash", result.image_hash[:16] + "...")
            
            console.print(table)
            
            if result.image_path:
                console.print(f"[green]Saved to:[/green] {result.image_path}")
        else:
            console.print(f"[red]Screenshot failed:[/red] {result.error}")


@cli.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--update", is_flag=True, help="Update baselines (save current as baseline)")
@click.pass_context
async def visual(ctx: click.Context, url: str, output: Optional[str],
                 update: bool) -> None:
    """Visual regression testing - compare with baselines."""
    from webtesterpro.modules.visual.visual_tester import Viewport, VisualTester
    
    config = ctx.obj["config"]
    baseline_dir = output or "baselines"
    
    console.print(f"[bold blue]Visual Regression:[/bold blue] {url}")
    
    async with WebTesterEngine(config) as engine:
        tester = VisualTester(baseline_dir=baseline_dir)
        tester.set_context(engine._context)
        
        if update:
            console.print("[yellow]Updating baselines...[/yellow]")
            results = await tester.update_baselines(url)
            
            table = Table(title="Baselines Updated")
            table.add_column("Viewport", style="cyan")
            table.add_column("Status", style="green")
            
            for name, result in results.items():
                table.add_row(name, "Saved" if result.success else "Failed")
            
            console.print(table)
        else:
            console.print("Comparing with baselines...")
            
            results = await tester.compare(url, Viewport.desktop())
            
            if results.error:
                if "not found" in results.error:
                    console.print(f"[yellow]No baseline found. Use --update to create one.[/yellow]")
                else:
                    console.print(f"[red]Error:[/red] {results.error}")
            else:
                table = Table(title="Visual Comparison")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Pixel Difference", str(results.pixel_difference))
                table.add_row("Percentage", f"{results.percentage_difference:.4f}%")
                table.add_row("Threshold", f"{tester.threshold * 100:.1f}%")
                table.add_row("Status", "[green]PASSED[/green]" if results.threshold_passed else "[red]FAILED[/red]")
                
                console.print(table)
                
                if results.diff_path:
                    console.print(f"[yellow]Diff image:[/yellow] {results.diff_path}")


def main():
    """Main entry point."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(cli.main(standalone_mode=False, obj={}))
        finally:
            loop.close()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)


# Additional Commands

@cli.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output directory for reports")
@click.option("--format", "-f", type=click.Choice(["html", "json", "pdf", "all"]), default="all", help="Report format")
@click.pass_context
async def report(ctx: click.Context, url: str, output: Optional[str], format: str) -> None:
    """Generate comprehensive test report."""
    from webtesterpro.modules.reporting import ReportGenerator, ReportData
    
    config = ctx.obj["config"]
    output_dir = output or "reports"
    
    console.print(f"[bold blue]Generating Report:[/bold blue] {url}")
    
    formats = ["html", "json"] if format == "all" else [format]
    
    async with WebTesterEngine(config) as engine:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running all tests...", total=None)
            
            # Run all tests
            seo_results = await engine.analyze_seo(url)
            perf_results = await engine.test_performance(url)
            sec_results = await engine.scan_security(url)
            a11y_results = await engine.check_accessibility(url)
            
            progress.update(task, completed=True)
        
        # Create report data
        data = ReportData(
            url=url,
            test_name=f"Full Test - {url}",
            seo_results=seo_results,
            performance_results=perf_results,
            security_results=sec_results,
            accessibility_results=a11y_results,
        )
        
        # Generate reports
        generator = ReportGenerator(config, output_dir=output_dir)
        results = generator.generate(data, formats=formats)
        
        console.print("\n[bold green]Reports generated:[/bold green]")
        for fmt, path in results.items():
            console.print(f"  [{fmt.upper()}] {path}")
        
        # Generate dashboard
        dashboard_path = generator.generate_dashboard()
        console.print(f"  [DASHBOARD] {dashboard_path}")


@cli.command(name="report-list")
@click.option("--limit", "-n", type=int, default=20, help="Number of reports to show")
@click.pass_context
def report_list(ctx: click.Context, limit: int) -> None:
    """List all generated reports."""
    from webtesterpro.modules.reporting import ReportGenerator
    
    generator = ReportGenerator()
    reports = generator.list_reports()[:limit]
    
    if not reports:
        console.print("[yellow]No reports found.[/yellow]")
        return
    
    table = Table(title=f"Reports (showing {len(reports)} of {len(reports)})")
    table.add_column("Type", style="cyan")
    table.add_column("Filename", style="white")
    table.add_column("Size", style="green")
    table.add_column("Modified", style="dim")
    
    for report in reports:
        size_kb = report["size"] / 1024
        table.add_row(
            report["type"].upper(),
            report["filename"][:50],
            f"{size_kb:.1f} KB",
            report["modified"][:19],
        )
    
    console.print(table)


@cli.command()
@click.pass_context
def dashboard(ctx: click.Context) -> None:
    """Generate and open dashboard."""
    from webtesterpro.modules.reporting import ReportGenerator
    import webbrowser
    
    generator = ReportGenerator()
    path = generator.generate_dashboard()
    
    console.print(f"[green]Dashboard generated:[/green] {path}")
    
    # Try to open in browser
    try:
        webbrowser.open(f"file://{path}")
    except Exception:
        console.print("[dim]Run 'open {path}' to view[/dim]")


@cli.command()
@click.pass_context
def history(ctx: click.Context) -> None:
    """Show test history."""
    from webtesterpro.modules.reporting import ReportGenerator
    
    generator = ReportGenerator()
    history_data = generator.get_history(limit=20)
    
    if not history_data:
        console.print("[yellow]No test history found.[/yellow]")
        return
    
    table = Table(title="Test History")
    table.add_column("ID", style="cyan")
    table.add_column("URL", style="white")
    table.add_column("Score", style="green")
    table.add_column("Modules", style="yellow")
    table.add_column("Date", style="dim")
    
    for entry in reversed(history_data):
        score = entry.get("overall_score", 0)
        score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        modules = len(entry.get("scores", {}))
        date = entry.get("timestamp", "")[:10]
        
        table.add_row(
            str(entry.get("id", "-")),
            entry.get("url", "")[:40],
            f"[{score_color}]{score}[/{score_color}]",
            str(modules),
            date,
        )
    
    console.print(table)


@cli.command()
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output directory for reports")
@click.pass_context
async def full(ctx: click.Context, url: str, output: Optional[str]) -> None:
    """Run full test suite (all modules)."""
    config = ctx.obj["config"]
    output_dir = output or "reports"
    
    console.print(f"[bold blue]Chạy kiểm thử toàn diện:[/bold blue] {url}")
    console.print("[dim]Đang chạy tất cả các bài kiểm tra...[/dim]\n")
    
    async with WebTesterEngine(config) as engine:
        # Run all tests
        tasks = {
            "SEO": engine.analyze_seo(url),
            "Performance": engine.test_performance(url),
            "Security": engine.scan_security(url),
            "Accessibility": engine.check_accessibility(url),
            "Scanner": engine.scan_site(url),
        }
        
        results = {}
        start_time = asyncio.get_event_loop().time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_descriptions = {
                "SEO": "Đang phân tích SEO...",
                "Performance": "Đang kiểm tra hiệu năng...",
                "Security": "Đang quét bảo mật...",
                "Accessibility": "Đang kiểm tra truy cập...",
                "Scanner": "Đang quét trang web...",
            }
            for name, task in tasks.items():
                t = progress.add_task(task_descriptions[name], total=None)
                results[name] = await task
                progress.update(t, completed=True)
        
        duration = asyncio.get_event_loop().time() - start_time
        
        # Generate report
        from webtesterpro.modules.reporting import ReportGenerator, ReportData
        
        data = ReportData(
            url=url,
            test_name=f"Full Test - {url}",
            seo_results=results.get("SEO", {}),
            performance_results=results.get("Performance", {}),
            security_results=results.get("Security", {}),
            accessibility_results=results.get("Accessibility", {}),
            scan_results=results.get("Scanner", {}),
            test_duration=duration,
            modules_run=list(tasks.keys()),
        )
        
        generator = ReportGenerator(config, output_dir=output_dir)
        report_paths = generator.generate(data, formats=["html", "json"])
        
        # ========== HIEN THI KET QUA CHI TIET ==========
        
        console.print("\n" + "=" * 60)
        console.print("[bold green]KET QUA KIEM THU[/bold green]")
        console.print("=" * 60)
        
        # === SEO RESULTS ===
        if "error" not in results.get("SEO", {}):
            seo_results = results.get("SEO", {})
            seo_scores = seo_results.get("scores", {})
            seo_summary = seo_results.get("summary", {})
            
            console.print("\n[bold cyan]1. PHAN TICH SEO[/bold cyan]")
            score = seo_scores.get("overall", 0)
            score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
            console.print(f"[bold]Diem SEO:[/bold] [{score_color}]{score}/100[/{score_color}]")
            
            seo_table = Table(title="Chi tiet diem SEO")
            seo_table.add_column("Muc", style="cyan")
            seo_table.add_column("Diem", style="green")
            seo_table.add_row("Tieu de", f"{seo_scores.get('title', 0)}/100")
            seo_table.add_row("The meta", f"{seo_scores.get('meta_tags', 0)}/100")
            seo_table.add_row("Cac the (Headings)", f"{seo_scores.get('headings', 0)}/100")
            seo_table.add_row("Noi dung", f"{seo_scores.get('content', 0)}/100")
            seo_table.add_row("Hinh anh", f"{seo_scores.get('images', 0)}/100")
            seo_table.add_row("Lien ket", f"{seo_scores.get('links', 0)}/100")
            seo_table.add_row("Ky thuat", f"{seo_scores.get('technical', 0)}/100")
            console.print(seo_table)
            
            seo_issues = seo_results.get("issues", [])
            if seo_issues:
                console.print(f"[yellow]Van de: {len(seo_issues)} van de tim thay[/yellow]")
        
        # === PERFORMANCE RESULTS ===
        if "error" not in results.get("Performance", {}):
            perf_results = results.get("Performance", {})
            web_vitals = perf_results.get("web_vitals", {})
            
            console.print("\n[bold cyan]2. KIEM TRA HIEU NANG[/bold cyan]")
            
            perf_table = Table(title="Core Web Vitals")
            perf_table.add_column("Chi so", style="cyan")
            perf_table.add_column("Gia tri", style="green")
            perf_table.add_column("Danh gia", style="yellow")
            
            lcp = web_vitals.get("lcp_ms", 0)
            lcp_status = "[green]Tot[/green]" if lcp < 2500 else "[yellow]Can cai thien[/yellow]" if lcp < 4000 else "[red]Kem[/red]"
            perf_table.add_row("LCP (Largest Contentful Paint)", f"{lcp:.0f}ms", lcp_status)
            
            cls = web_vitals.get("cls", 0)
            cls_status = "[green]Tot[/green]" if cls < 0.1 else "[yellow]Can cai thien[/yellow]" if cls < 0.25 else "[red]Kem[/red]"
            perf_table.add_row("CLS (Cumulative Layout Shift)", f"{cls:.4f}", cls_status)
            
            fid = web_vitals.get("fid_ms", 0)
            fid_status = "[green]Tot[/green]" if fid < 100 else "[yellow]Can cai thien[/yellow]" if fid < 300 else "[red]Kem[/red]"
            perf_table.add_row("FID (First Input Delay)", f"{fid:.0f}ms", fid_status)
            
            ttfb = web_vitals.get("ttfb_ms", 0)
            ttfb_status = "[green]Tot[/green]" if ttfb < 800 else "[yellow]Can cai thien[/yellow]" if ttfb < 1800 else "[red]Kem[/red]"
            perf_table.add_row("TTFB (Time to First Byte)", f"{ttfb:.0f}ms", ttfb_status)
            
            fcp = web_vitals.get("fcp_ms", 0)
            fcp_status = "[green]Tot[/green]" if fcp < 1800 else "[yellow]Can cai thien[/yellow]" if fcp < 3000 else "[red]Kem[/red]"
            perf_table.add_row("FCP (First Contentful Paint)", f"{fcp:.0f}ms", fcp_status)
            
            console.print(perf_table)
            
            perf_score = perf_results.get("scores", {}).get("overall", 0)
            console.print(f"[bold]Diem hieu nang:[/bold] {perf_score:.0f}/100")
        
        # === SECURITY RESULTS ===
        if "error" not in results.get("Security", {}):
            sec_results = results.get("Security", {})
            sec_summary = sec_results.get("summary", {})
            
            console.print("\n[bold cyan]3. QUET BAO MAT[/bold cyan]")
            
            rating = sec_summary.get("risk_rating", "UNKNOWN")
            rating_color = {
                "CRITICAL": "red",
                "HIGH": "red",
                "MEDIUM": "yellow",
                "LOW": "green",
                "SECURE": "green",
            }.get(rating, "white")
            
            console.print(f"[bold]Muc do rui ro:[/bold] [{rating_color}]{rating}[/{rating_color}]")
            console.print(f"[bold]Diem rui ro:[/bold] {sec_summary.get('overall_risk_score', 0)}/100")
            
            sec_table = Table(title="So luong van de theo muc do")
            sec_table.add_column("Muc do", style="cyan")
            sec_table.add_column("So luong", style="green")
            sec_table.add_row("Nghiem trong", str(sec_summary.get("critical", 0)))
            sec_table.add_row("Cao", str(sec_summary.get("high", 0)))
            sec_table.add_row("Trung binh", str(sec_summary.get("medium", 0)))
            sec_table.add_row("Thap", str(sec_summary.get("low", 0)))
            sec_table.add_row("Thong tin", str(sec_summary.get("info", 0)))
            console.print(sec_table)
            
            sec_issues = sec_results.get("issues", [])
            if sec_issues:
                console.print(f"[yellow]Tong cong: {len(sec_issues)} van de bao mat[/yellow]")
        
        # === ACCESSIBILITY RESULTS ===
        if "error" not in results.get("Accessibility", {}):
            a11y_results = results.get("Accessibility", {})
            a11y_summary = a11y_results.get("summary", {})
            
            console.print("\n[bold cyan]4. KIEM TRA TRUY CAP[/bold cyan]")
            
            a11y_table = Table(title="So luong van de theo muc do")
            a11y_table.add_column("Muc do", style="cyan")
            a11y_table.add_column("So luong", style="green")
            a11y_table.add_row("Nghiem trong", str(a11y_summary.get("critical", 0)))
            a11y_table.add_row("Nghien cam", str(a11y_summary.get("serious", 0)))
            a11y_table.add_row("Trung binh", str(a11y_summary.get("moderate", 0)))
            a11y_table.add_row("Thap", str(a11y_summary.get("minor", 0)))
            console.print(a11y_table)
            
            a11y_issues = a11y_results.get("issues", [])
            if a11y_issues:
                console.print(f"[yellow]Tong cong: {len(a11y_issues)} van de truy cap[/yellow]")
        
        # === SCANNER RESULTS ===
        if "error" not in results.get("Scanner", {}):
            scan_results = results.get("Scanner", {})
            scan_summary = scan_results.get("summary", {})
            
            console.print("\n[bold cyan]5. QUET TRANG WEB[/bold cyan]")
            
            scan_table = Table(title="Ket qua quet")
            scan_table.add_column("Loai", style="cyan")
            scan_table.add_column("So luong", style="green")
            scan_table.add_row("Bieu mau (Forms)", str(scan_summary.get("total_forms", 0)))
            scan_table.add_row("Lien ket (Links)", str(scan_summary.get("total_links", 0)))
            scan_table.add_row("Tai nguyen (Resources)", str(scan_summary.get("total_resources", 0)))
            console.print(scan_table)
        
        # === TONG KET ===
        console.print("\n" + "=" * 60)
        console.print("[bold green]TONG KET[/bold green]")
        console.print("=" * 60)
        
        summary_table = Table(title="Trang thai cac module")
        summary_table.add_column("Module", style="cyan")
        summary_table.add_column("Trang thai", style="green")
        summary_table.add_column("Chi tiet", style="white")
        
        module_names = {
            "SEO": "Phan tich SEO",
            "Performance": "Hieu nang",
            "Security": "Bao mat",
            "Accessibility": "Truy cap",
            "Scanner": "Quet web",
        }
        
        for name, result in results.items():
            has_error = isinstance(result, dict) and "error" in result
            status = "[green]Hoan thanh[/green]" if not has_error else "[red]Loi[/red]"
            
            detail = ""
            if not has_error:
                if name == "SEO":
                    detail = f"Diem: {result.get('scores', {}).get('overall', 0)}/100"
                elif name == "Performance":
                    detail = f"Diem: {result.get('scores', {}).get('overall', 0)}/100"
                elif name == "Security":
                    detail = f"Muc do: {result.get('summary', {}).get('risk_rating', 'N/A')}"
                elif name == "Accessibility":
                    detail = f"{len(result.get('issues', []))} van de"
                elif name == "Scanner":
                    detail = f"{result.get('summary', {}).get('total_resources', 0)} resources"
            
            summary_table.add_row(module_names.get(name, name), status, detail)
        
        console.print(summary_table)
        
        console.print(f"\n[bold]Thoi gian:[/bold] {duration:.1f}s")
        console.print(f"[bold green]Bao cao da luu vao:[/bold green] {output_dir}/")


if __name__ == "__main__":
    main()
