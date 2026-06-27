"""
WebTesterPro - All-in-One Website Testing Tool

Main entry point for the WebTesterPro application.
"""

import asyncio
import sys
from pathlib import Path

from webtesterpro.cli.main import cli


def main():
    """Main entry point."""
    from webtesterpro.cli.main import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
