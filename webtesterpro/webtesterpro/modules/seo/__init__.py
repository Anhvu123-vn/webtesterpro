"""
SEO Testing Module

SEO analysis for websites:
- Title, Meta tags
- Headings structure
- Open Graph, Schema.org
- Image optimization
- Link analysis
- Page speed metrics
"""

from webtesterpro.modules.seo.seo_analyzer import (
    SEOAnalyzer,
    SEOIssue,
    SEOReport,
    SEOScore,
)

__all__ = [
    "SEOAnalyzer",
    "SEOIssue",
    "SEOReport",
    "SEOScore",
]
