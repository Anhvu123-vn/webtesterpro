"""
WebTesterPro Config Module

Configuration management using YAML files and Pydantic settings.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ProjectConfig(BaseModel):
    """Project metadata configuration."""
    name: str = "WebTesterPro"
    version: str = "0.1.0"
    author: str = "WebTesterPro Team"


class CrawlerConfig(BaseModel):
    """Crawler configuration."""
    max_depth: int = 3
    max_pages: int = 1000
    timeout: int = 30000
    delay_min: float = 1.0
    delay_max: float = 3.0
    respect_robots_txt: bool = True
    user_agent: str = "WebTesterPro/0.1.0 (+https://github.com/webtesterpro)"
    max_concurrent: int = 5
    blacklist: list = Field(default_factory=list)
    allowed_domains: list = Field(default_factory=list)


class ScannerConfig(BaseModel):
    """Scanner configuration."""
    timeout: int = 30000
    follow_redirects: bool = True
    max_redirects: int = 5
    verify_ssl: bool = True
    check_forms: bool = True
    check_links: bool = True
    check_resources: bool = True
    check_accessibility: bool = False


class AnalyzerConfig(BaseModel):
    """Analyzer configuration."""
    check_seo: bool = True
    check_performance: bool = True
    check_security_headers: bool = True
    check_responsive: bool = False
    lighthouse_enabled: bool = False


class MonitorConfig(BaseModel):
    """Monitor configuration."""
    interval: int = 60
    timeout: int = 10
    retry_count: int = 3
    alert_on_down: bool = True


class LoginConfig(BaseModel):
    """Login configuration."""
    method: str = "form"
    wait_for_selectors: list = Field(default_factory=lambda: [
        "#username", "#password",
        "input[name='username']", "input[name='password']"
    ])
    submit_selectors: list = Field(default_factory=lambda: [
        "button[type='submit']", "input[type='submit']"
    ])
    post_login_wait: int = 2000


class ReportsConfig(BaseModel):
    """Reports configuration."""
    output_dir: str = "reports/output"
    format: str = "html"
    include_screenshots: bool = True
    include_network_log: bool = False
    template: str = "default"


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/webtesterpro.log"
    console: bool = True


class DashboardConfig(BaseModel):
    """Dashboard configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


class Config(BaseSettings):
    """
    Main configuration class that loads from YAML file.
    
    Loads configuration from config.yaml file with fallback to defaults.
    """
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    crawler: CrawlerConfig = Field(default_factory=CrawlerConfig)
    scanner: ScannerConfig = Field(default_factory=ScannerConfig)
    analyzer: AnalyzerConfig = Field(default_factory=AnalyzerConfig)
    monitor: MonitorConfig = Field(default_factory=MonitorConfig)
    login: LoginConfig = Field(default_factory=LoginConfig)
    reports: ReportsConfig = Field(default_factory=ReportsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)

    class Config:
        env_prefix = "WEBTESTERPRO_"
        env_nested_delimiter = "__"

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "Config":
        """Load configuration from a YAML file."""
        path = Path(path)
        if not path.exists():
            return cls()
        
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        
        return cls(**data)

    @classmethod
    def load_default(cls) -> "Config":
        """Load configuration from default config.yaml location."""
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        if config_path.exists():
            return cls.from_yaml(config_path)
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()
