# WebTesterPro

**All-in-One Website Testing Tool** - A comprehensive Python framework for website testing, crawling, and analysis using Playwright as the core engine.

## Features

- **Website Crawler**: Depth-limited crawling with robots.txt respect, URL blacklist filtering, and login support
- **Website Scanner**: Scans for forms, links, resources, and accessibility issues
- **Website Analyzer**: Analyzes SEO, performance, and security
- **Website Monitor**: Uptime monitoring with alerts
- **CLI Interface**: Rich command-line interface with progress indicators
- **Async/Await**: Built with async/await for high performance
- **Modular Design**: Clean Architecture for easy extension

## Requirements

- Python 3.11+
- Playwright
- Chrome, Firefox, or WebKit browsers

## Installation

### 1. Clone and Install

```bash
cd webtesterpro
pip install -r requirements.txt
playwright install chromium
```

### 2. Quick Install (from PyPI - coming soon)

```bash
pip install webtesterpro
playwright install chromium
```

## Usage

### CLI Commands

```bash
# Crawl a website
webtesterpro crawl https://example.com --max-depth 3 --max-pages 100

# Scan a website
webtesterpro scan https://example.com

# Analyze a website
webtesterpro analyze https://example.com

# Monitor a website
webtesterpro monitor https://example.com --duration 60

# Show configuration
webtesterpro info
```

### Python API

```python
import asyncio
from webtesterpro.core.engine import WebTesterEngine

async def main():
    async with WebTesterEngine() as engine:
        # Crawl a website
        crawl_results = await engine.crawl_site("https://example.com")
        
        # Scan a website
        scan_results = await engine.scan_site("https://example.com")
        
        # Analyze a website
        analyze_results = await engine.analyze_site("https://example.com")
        
        # Monitor a website
        monitor_results = await engine.monitor_site("https://example.com", duration=60)

asyncio.run(main())
```

### With Login

```python
import asyncio
from webtesterpro.core.engine import WebTesterEngine

async def main():
    async with WebTesterEngine() as engine:
        login_data = {
            "url": "https://example.com/login",
            "username": "user@example.com",
            "password": "secretpassword",
        }
        
        results = await engine.crawl_site(
            "https://example.com/dashboard",
            login_data=login_data
        )

asyncio.run(main())
```

## Project Structure

```
webtesterpro/
├── core/                  # Core engine and configuration
│   ├── config.py         # Configuration management
│   └── engine.py         # Main engine
├── modules/               # Testing modules
│   ├── crawler/          # Website crawler
│   ├── scanner/          # Website scanner
│   ├── analyzer/         # Website analyzer
│   └── monitor/          # Website monitor
├── utils/                 # Utility functions
├── reports/               # Report templates
├── config/                # Configuration files
├── cli/                   # CLI interface
├── dashboard/             # Web dashboard (future)
├── tests/                 # Tests
└── main.py               # Entry point
```

## Configuration

Edit `config.yaml` to customize:

```yaml
crawler:
  max_depth: 3
  max_pages: 1000
  delay_min: 1.0
  delay_max: 3.0
  respect_robots_txt: true
  blacklist:
    - ".*\\.pdf$"
    - ".*\\.zip$"

scanner:
  check_forms: true
  check_links: true
  check_resources: true

analyzer:
  check_seo: true
  check_performance: true
  check_security_headers: true
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
ruff check .
mypy webtesterpro/
```

## License

MIT License

## Contributing

Contributions are welcome! Please read the contributing guidelines first.
