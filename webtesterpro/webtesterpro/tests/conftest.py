"""
pytest configuration and fixtures.
"""

import pytest
import asyncio


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def config():
    """Provide a test configuration."""
    from webtesterpro.core.config import Config, CrawlerConfig
    
    return Config(
        crawler=CrawlerConfig(
            max_depth=2,
            max_pages=10,
            delay_min=0.1,
            delay_max=0.2,
        )
    )
