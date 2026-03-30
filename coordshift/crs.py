"""
crs.py — CRS resolution and search.

Turns EPSG codes and PROJ strings into a canonical form pyproj accepts.
"""

from pyproj import CRS
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_crs_info
from pyproj.exceptions import CRSError as PyprojCRSError

# Bounding box that covers the contiguous US, Alaska, Hawaii, and territories.
_USA_AOI = AreaOfInterest(
    west_lon_degree=-180.0,
    south_lat_degree=15.0,
    east_lon_degree=-60.0,
    north_lat_degree=72.0,
)


class CRSError(ValueError):
    """Raised when a CRS string cannot be resolved."""
    pass


def resolve_crs(crs_input: str) -> str:
    """
    Resolve a CRS input string to a canonical form pyproj can use.

    Accepts:
        - EPSG codes as string: "EPSG:4326" or "4326"
        - Other strings PROJ can parse unambiguously (PROJ definitions, authority names, etc.)

    Args:
        crs_input: The CRS string to resolve.

    Returns:
        A CRS string ready for pyproj (preferably ``EPSG:xxxx`` when available).

    Raises:
        CRSError: If the CRS cannot be resolved.
    """
    raw = crs_input.strip()
    if not raw:
        raise CRSError(
            "Empty CRS input. Provide an EPSG code or PROJ string "
            "(use `coordshift search` to find EPSG codes for the USA)."
        )

    try:
        crs = CRS(raw)
    except PyprojCRSError as e:
        raise CRSError(
            f"Could not resolve CRS {raw!r}: {e}. "
            "Use an EPSG code, a PROJ string, or another form PROJ accepts unambiguously. "
            "Run `coordshift search` to find EPSG codes by name (USA-filtered)."
        ) from e

    epsg = crs.to_epsg()
    if epsg is not None:
        return f"EPSG:{epsg}"
    return crs.to_wkt()


def search_crs(query: str) -> list[dict]:
    """
    Search the EPSG database for CRS whose names contain all query words.

    Results are filtered to the USA bounding box so common projected CRS
    (State Plane, UTM zones, etc.) for the US are returned without noise
    from unrelated global entries.  All words must match (AND logic), so
    multi-word queries like "iowa south" work correctly.

    Args:
        query: One or more keywords (e.g. "iowa south", "utm zone 15").

    Returns:
        List of dicts with keys: epsg, name, type, area_of_use.
        Sorted by EPSG code (ascending).
    """
    words = query.strip().lower().split()
    if not words:
        return []

    db_results = query_crs_info(
        auth_name="EPSG",
        area_of_interest=_USA_AOI,
        allow_deprecated=False,
    )

    matches: list[dict] = []
    for info in db_results:
        name_lower = info.name.lower()
        if all(w in name_lower for w in words):
            matches.append(
                {
                    "epsg": f"EPSG:{info.code}",
                    "name": info.name,
                    "type": info.type.name if info.type else "",
                    "area_of_use": info.area_of_use or "",
                }
            )

    matches.sort(key=lambda r: int(r["epsg"].split(":")[1]))
    return matches
