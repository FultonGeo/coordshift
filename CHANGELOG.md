# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

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
- `coordshift.crs.resolve_crs()` — resolves EPSG codes, PROJ strings, and friendly preset names to a canonical CRS string.
- `coordshift.crs.search_crs()` — searches the preset catalog by keyword.
- `coordshift.crs.CRSError` — custom exception for unresolvable CRS inputs.
- `coordshift.io.read_csv()` / `write_csv()` — thin wrappers around pandas CSV I/O.
- `coordshift.io.detect_columns()` — auto-detects X/Y columns from common name patterns (lon, lat, easting, northing, x, y, etc.).
- `coordshift.presets.PRESETS` — built-in catalog of friendly name → EPSG mappings: WGS84, NAD83, Indiana East/West, Iowa North, Arizona East/Central/West, UTM zones 15–17N, Web Mercator.

**CLI** (`coordshift` entry point)

- `coordshift convert` — convert a CSV file from one CRS to another.
- `coordshift search` — search presets by keyword.
- `coordshift list-crs` — list all built-in presets.
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
