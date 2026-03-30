# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

## [0.2.0] - 2026-03-29

**Breaking (Python / CLI):** Preset aliases (`wgs84`, `nad83`, `indiana-east`, etc.), the
`coordshift list-crs` command, and the `coordshift.presets` module are removed. Use EPSG codes,
PROJ strings, and `coordshift search` / `search_crs()` instead. The browser app (`coordshift.html`)
still ships an embedded CRS catalog. This release also includes the browser improvements and fixes
listed below.

### Removed

- **Python / CLI:** Built-in CRS name presets (`wgs84`, `nad83`, `indiana-east`, etc.), the
  **`coordshift.presets`** module, and the **`coordshift list-crs`** command. Pass **EPSG
  codes**, **PROJ strings**, or other PROJ-resolvable text; use **`coordshift search`** /
  **`search_crs()`** to look up USA EPSG entries by keyword. The **`coordshift.html`** browser
  app still embeds a full client-side catalog.

### Added

- `coordshift.html`: **NAD83(2011) geographic lat/lon (EPSG:6318)** added to the global CRS
  catalog. This is the reference frame reported by RTK GNSS receivers observing against U.S.
  CORS networks — the correct source CRS for most professional survey fieldwork in the USA.
  Previously users had to substitute WGS 84 (EPSG:4326), which introduces an unmodeled ~1 m
  datum shift.

- `coordshift.html`: **Datum-accuracy warnings** now appear in amber below the CRS selectors
  whenever a conversion pair involves frames that differ by more than a few centimetres but
  cannot be rigorously transformed by proj4.js:
  - *NAD83(2011) ↔ ITRF2014* — warns of the ~1 m (~4 ft) CONUS offset caused by 30+ years
    of North American tectonic plate motion since the 1992 NAD83 adjustment epoch (requires
    NADCON5 or a 14-parameter Helmert transformation).
  - *WGS 84 ↔ ITRF2014* — warns that the shift is <2 cm for current WGS 84 (G2139) but
    still cannot be modelled; directs users to EPSG:6318 if they actually need NAD83↔ITRF.

### Fixed

- `coordshift.html`: **Output sample rings now appear on the map preview for projected target
  CRS** (State Plane, UTM, Web Mercator, etc.). Previously, the preview only plotted rings
  when the converted output coordinates fell inside the lat/lon bounding box (±90°/±180°);
  projected metre/foot values always failed that check and no rings appeared. The preview now
  uses `toLeafletLatLng()` (the same back-projection path the full Convert handler uses),
  which reprojects converted output back to WGS 84 before plotting. Rings now land on the blue
  input dots for any CRS when the conversion is correct, and drift visibly when the wrong CRS
  is chosen.

- `coordshift.html`: **Projected coordinate sample values shown in status bar** alongside the
  ring count when the target CRS is a projected system, so users can verify numeric output
  (e.g. `Projected: 192222.47 m, 501034.12 m`) without having to click an individual ring.

- `coordshift.html`: `toLeafletLatLng()` now treats NAD83(2011) (EPSG:6318) and ITRF2014
  (EPSG:9000) as directly-plottable geographic CRS alongside WGS 84, avoiding an unnecessary
  proj4 round-trip that could fail if the EPSG definition had not yet been fetched from
  epsg.io.

---

## [0.1.2] - 2026-03-29

Browser app improvements only; Python library and CLI unchanged.

### Added

- `coordshift.html`: **State Plane zones** help callout in the sidebar with a direct link to the
  [USA State Plane Zones NAD83](https://hub.arcgis.com/datasets/esri::usa-state-plane-zones-nad83/)
  Esri Hub map so users can look up SPCS zone names (e.g. Indiana East) and confirm the correct
  zone for their project location. Link opens in a new tab (`target="_blank"`) so the app page is
  not lost.

### Changed

- `coordshift.html`: default map view now centers on the geographic center of the contiguous U.S.
  (39.83°N, 98.58°W, zoom 4 / full lower-48 view) instead of Indiana. After a conversion the map
  still auto-fits to the plotted points.

---

## [0.1.1] - 2026-03-28

Documentation and packaging metadata only; runtime code unchanged.

### Changed

- README and `docs/examples.md`: PyPI as the primary install path.
- `pyproject.toml`: `[project.urls]` for PyPI project page links.

---

## [0.1.0] - 2026-03-28

Initial alpha release.

> **Alpha software.** Always verify converted coordinates against a trusted independent source.
> The authors provide no warranty and accept no liability for errors in conversion results.

### Added

**Python library**

- `coordshift.core.convert()` — reads a CSV, reprojects coordinate columns, and returns a pandas DataFrame. Supports in-place replacement or new columns via `suffix`.
- `coordshift.core.transform_points()` — low-level list-to-list coordinate transform using `pyproj.Transformer` with `always_xy=True`.
- `coordshift.crs.resolve_crs()` — resolves EPSG codes, PROJ strings, and (in early releases) preset names to a canonical CRS string.
- `coordshift.crs.search_crs()` — searches the EPSG database by keyword (USA-filtered).
- `coordshift.crs.CRSError` — custom exception for unresolvable CRS inputs.
- `coordshift.io.read_csv()` / `write_csv()` — thin wrappers around pandas CSV I/O.
- `coordshift.io.detect_columns()` — auto-detects X/Y columns from common name patterns (lon, lat, easting, northing, x, y, etc.).
- `coordshift.presets` / `PRESETS` — built-in friendly name → EPSG mappings *(module removed in a later release)*.

**CLI** (`coordshift` entry point)

- `coordshift convert` — convert a CSV file from one CRS to another.
- `coordshift search` — search EPSG entries by keyword.
- `coordshift list-crs` — list built-in preset aliases *(removed in a later release)*.
- UTF-8 console output on Windows.
- Progress indication for large files (>10k rows).

**Browser app**

- `coordshift.html` — standalone single-file browser-based converter.
  - CSV upload with automatic column detection.
  - CRS search across a full NAD83(2011) State Plane, UTM, and geographic catalog.
  - In-browser reprojection via proj4js (no server required, works offline).
  - Leaflet map preview of converted points.
  - CSV download.

**Developer tooling**

- `scripts/gen_nad83_2011_spcs_js.py` — fetches and formats the NAD83(2011) SPCS catalog as JSON.
- `scripts/merge_spcs_into_index.py` — embeds the generated JSON catalog into `coordshift.html`.

### Distribution

- Published on PyPI as [`coordshift`](https://pypi.org/project/coordshift/) (`pip install coordshift`).

### Design notes

- Original X/Y columns are always preserved in output. Converted values are written to new columns placed immediately after the originals (e.g. `lon` → `lon_converted`, `lat` → `lat_converted`).
- `--suffix` / `suffix=` controls the appended column name suffix; default is `_converted`.
- Same behaviour applies in `coordshift.html`: converted columns appear right after the originals in the downloaded CSV.
