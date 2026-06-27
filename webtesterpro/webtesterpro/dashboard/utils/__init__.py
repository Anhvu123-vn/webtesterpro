"""Dashboard utilities."""

from webtesterpro.dashboard.utils.results_parser import (
    build_recommendations,
    parse_issues,
    score_color,
    score_ring_color,
)

__all__ = ["parse_issues", "build_recommendations", "score_color", "score_ring_color"]
