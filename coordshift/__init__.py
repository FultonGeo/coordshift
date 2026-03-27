"""
coordshift — Universal coordinate system conversion for CSV and tabular data.

Basic usage:
    from coordshift import convert
    df = convert("input.csv", from_crs="EPSG:4326", to_crs="EPSG:2965", x="lon", y="lat")
"""

from coordshift.core import convert
from coordshift.crs import resolve_crs, search_crs

__version__ = "0.1.0"
__all__ = ["convert", "resolve_crs", "search_crs"]
