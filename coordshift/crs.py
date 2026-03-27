"""
crs.py — CRS resolution and search.

Responsible for turning whatever the user types (EPSG code, PROJ string,
friendly name like "indiana-east") into something pyproj can use.
"""

from pyproj import CRS
from pyproj.exceptions import CRSError as PyprojCRSError

from coordshift.presets import PRESETS


class CRSError(ValueError):
    """Raised when a CRS string cannot be resolved."""
    pass


def _normalize_preset_key(user_input: str) -> str:
    """Normalize user text for lookup in PRESETS (lowercase, hyphenated)."""
    return user_input.strip().lower().replace(" ", "-")


def resolve_crs(crs_input: str) -> str:
    """
    Resolve a CRS input string to a canonical form pyproj can use.

    Accepts:
        - EPSG codes as string: "EPSG:4326" or "4326"
        - PROJ strings: "+proj=longlat +datum=WGS84"
        - Preset names: "wgs84", "indiana-east", "nad83"

    Args:
        crs_input: The CRS string to resolve.

    Returns:
        A CRS string ready for pyproj.

    Raises:
        CRSError: If the CRS cannot be resolved.
    """
    raw = crs_input.strip()
    if not raw:
        raise CRSError(
            "Empty CRS input. Provide an EPSG code, PROJ string, or preset name "
            "(try `coordshift search`)."
        )

    preset_key = _normalize_preset_key(raw)
    if preset_key in PRESETS:
        return str(PRESETS[preset_key]["epsg"])

    try:
        crs = CRS(raw)
    except PyprojCRSError as e:
        raise CRSError(
            f"Could not resolve CRS {raw!r}: {e}. "
            "Try an EPSG code, a PROJ string, or a preset name. "
            "Run `coordshift search` to list presets."
        ) from e

    epsg = crs.to_epsg()
    if epsg is not None:
        return f"EPSG:{epsg}"
    return crs.to_wkt()


def search_crs(query: str) -> list[dict]:
    """
    Search for CRS presets matching a query string.

    Args:
        query: Search term (e.g. "indiana", "state plane", "utm zone 16").

    Returns:
        List of matching preset dicts with keys: name, epsg, description.
    """
    q = query.strip().lower()
    if not q:
        return []

    matches: list[dict] = []
    for name, data in PRESETS.items():
        description = str(data.get("description", ""))
        haystack_name = name.lower()
        haystack_desc = description.lower()
        if q in haystack_name or q in haystack_desc:
            matches.append(
                {
                    "name": name,
                    "epsg": data["epsg"],
                    "description": description,
                }
            )
    return matches
