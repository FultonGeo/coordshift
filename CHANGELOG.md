# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Changed

- **Breaking:** `convert()` and `coordshift convert` no longer overwrite the original X/Y columns. Converted values are now always written to new columns placed immediately after the originals.
- Default output column names are now `{x}_converted` / `{y}_converted` (e.g. `lon_converted`, `lat_converted`). Previously, no suffix meant in-place replacement.
- `--suffix` (CLI) / `suffix=` (API) now controls the column name suffix only; the default is `"_converted"`. Passing `--suffix _proj` produces `lon_proj`, `lat_proj`.
- Same behaviour in `coordshift.html`: converted columns are inserted right after the originals in the downloaded CSV.

---

## [0.1.0] - 2026-03-27

Initial release.

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
