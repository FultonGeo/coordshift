"""
presets.py — Friendly name to EPSG mappings.

Lets users type "indiana-east" instead of "EPSG:2965". Add more as needed.
Organized by category. All EPSG codes reference NAD83(2011) where applicable.
"""

PRESETS: dict[str, dict] = {
    # --- Geographic (lat/lon) ---
    "wgs84": {
        "epsg": "EPSG:4326",
        "description": "WGS84 Geographic (lat/lon) — GPS default",
    },
    "nad83": {
        "epsg": "EPSG:4269",
        "description": "NAD83 Geographic (lat/lon) — North America",
    },

    # --- Indiana State Plane ---
    "indiana-east": {
        "epsg": "EPSG:2965",
        "description": "Indiana State Plane East (NAD83, meters)",
    },
    "indiana-west": {
        "epsg": "EPSG:2966",
        "description": "Indiana State Plane West (NAD83, meters)",
    },

    # --- Arizona State Plane ---
    "arizona-east": {
        "epsg": "EPSG:2223",
        "description": "Arizona State Plane East (NAD83, feet)",
    },
    "arizona-central": {
        "epsg": "EPSG:2224",
        "description": "Arizona State Plane Central (NAD83, feet)",
    },
    "arizona-west": {
        "epsg": "EPSG:2225",
        "description": "Arizona State Plane West (NAD83, feet)",
    },

    # --- UTM (NAD83) ---
    "utm-15n": {
        "epsg": "EPSG:26915",
        "description": "UTM Zone 15N (NAD83) — Central US",
    },
    "utm-16n": {
        "epsg": "EPSG:26916",
        "description": "UTM Zone 16N (NAD83) — Indiana/Ohio area",
    },
    "utm-17n": {
        "epsg": "EPSG:26917",
        "description": "UTM Zone 17N (NAD83) — Eastern US",
    },

    # --- Web / Mapping ---
    "web-mercator": {
        "epsg": "EPSG:3857",
        "description": "Web Mercator — Google Maps, OpenStreetMap",
    },
}
