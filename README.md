# coordshift

> **⚠ Alpha software — use with caution**
>
> coordshift is in early development (pre-v1.0). APIs and output formats may change without notice.
> **Always verify converted coordinates against a trusted independent source before using them in any survey, legal, safety-critical, or production workflow.**
> The authors provide no warranty and accept no liability for errors in coordinate conversion results. Use at your own risk.

Universal coordinate system conversion for CSV and tabular data — built for GIS analysts, surveyors, and drone mapping workflows.

## What it does

`coordshift` reprojects coordinate columns in CSV files from one CRS to another, using any system supported by PROJ. It ships as both a command-line tool and a Python library, plus a standalone browser-based converter (`coordshift.html`) that works entirely offline.

**CLI**

```bash
coordshift convert input.csv --from EPSG:4326 --to EPSG:2965 --x lon --y lat
```

**Python**

```python
from coordshift import convert

df = convert("input.csv", from_crs="EPSG:4326", to_crs="EPSG:2965", x="lon", y="lat")
```

**Browser**

Open `coordshift.html` in any modern browser — no install required.

## Why this exists

Tools like cs2cs, ogr2ogr, and raw pyproj are powerful but assume you already speak PROJ. `coordshift` targets practitioners who need fast, repeatable conversions without wrestling with syntax.

## What's included

- Convert any EPSG/PROJ CRS to any other
- Auto-detect common column names (lat, lon, x, y, easting, northing, etc.)
- Source and target CRS via EPSG code, PROJ string, or friendly preset name
- Preserve all columns in output — original X/Y columns are always kept
- Converted coordinates written to new columns placed immediately after the originals
- Customisable output column suffix (default `_converted`, e.g. `lon_converted`, `lat_converted`)
- CLI for one-off conversions
- Python API for scripting and pipelines
- Browser-based converter (`coordshift.html`) with map preview — works offline

## Planned

- Vertical coordinate support (ellipsoidal ↔ orthometric, GEOID)
- Batch conversion across multiple files
- Output to GeoJSON or Shapefile

## Installation

Install from source until the first PyPI release:

```bash
git clone https://github.com/FultonGeo/coordshift.git
cd coordshift
pip install -e .
```

Or, once published:

```bash
pip install coordshift
```

## Usage

### CLI

Basic conversion (original `lon`/`lat` columns are preserved; converted values go into `lon_converted`/`lat_converted` placed right after them):

```bash
coordshift convert input.csv --from EPSG:4326 --to EPSG:2965 --x lon --y lat
```

With output path:

```bash
coordshift convert input.csv --from EPSG:4326 --to EPSG:2965 --x lon --y lat --out output.csv
```

Custom column name suffix (produces `lon_proj`, `lat_proj` instead of the default `lon_converted`, `lat_converted`):

```bash
coordshift convert input.csv --from EPSG:4326 --to EPSG:2965 --suffix _proj
```

PROJ strings (use a single line on Windows, or wrap as your shell allows):

```bash
coordshift convert input.csv \
  --from "+proj=longlat +datum=WGS84" \
  --to "+proj=tmerc +lat_0=37.5 +lon_0=-85.66666667 +k=0.999966667 +x_0=100000 +y_0=250000 +ellps=GRS80" \
  --x longitude --y latitude
```

List presets and search CRS:

```bash
coordshift list-crs
coordshift search "indiana east"
```

### Python API

```python
from coordshift import convert, search_crs

df = convert(
    "field_points.csv",
    from_crs="EPSG:4326",
    to_crs="EPSG:2965",
    x="lon",
    y="lat",
)
# df now has lon, lon_converted, lat, lat_converted (plus any other original columns)
df.to_csv("field_points_converted.csv", index=False)

results = search_crs("indiana east")
```

See [docs/examples.md](docs/examples.md) for more detailed examples.

### Browser app

Open `coordshift.html` in any modern browser (Chrome, Firefox, Edge, Safari). No server or internet connection required after the page loads. Features include:

- Upload a CSV and pick coordinate columns
- Search and select source/target CRS from a built-in catalog of State Plane zones, UTM, and common geographic systems
- Preview converted points on an interactive map
- Download the converted CSV

## Project structure

```text
coordshift/
├── coordshift/         # Python package
│   ├── __init__.py    # Public API
│   ├── core.py        # Conversion (pyproj)
│   ├── cli.py         # CLI (Click)
│   ├── io.py          # CSV I/O, column detection
│   ├── crs.py         # CRS resolution
│   └── presets.py     # Friendly name → EPSG
├── tests/
│   ├── test_core.py
│   ├── test_cli.py
│   ├── test_io.py
│   └── fixtures/
├── docs/
│   └── examples.md
├── scripts/           # Developer tooling (regenerate HTML catalog)
├── coordshift.html    # Standalone browser-based converter
├── pyproject.toml
├── README.md
└── LICENSE
```

## Development setup

```bash
git clone https://github.com/FultonGeo/coordshift.git
cd coordshift
python -m venv venv
```

Activate the virtual environment:

- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **macOS / Linux:** `source venv/bin/activate`

Then:

```bash
pip install -e ".[dev]"
pytest
```

Run the linter:

```bash
ruff check coordshift/
```

## Dependencies

- [pyproj](https://pyproj4.github.io/pyproj/) — PROJ bindings
- [pandas](https://pandas.pydata.org/) — tabular data
- [click](https://click.palletsprojects.com/) — CLI

## Contributing

Contributions welcome. Open an issue before large changes so direction stays aligned.

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit and push
4. Open a pull request

## Disclaimer

coordshift is alpha software provided **as-is**, without warranty of any kind, express or implied. Coordinate conversion results depend on the accuracy of the underlying PROJ library, the correctness of the CRS definitions used, and the quality of the input data. Always double-check converted coordinates against an authoritative source before using them in any survey, engineering, legal, or safety-critical context. The authors and contributors are not responsible for errors, losses, or damages arising from the use of this software.

## License

MIT. See [LICENSE](LICENSE).

## Author

Nick Fulton — geospatial work, FAA Part 107, drone and survey experience.

Repository: [FultonGeo/coordshift](https://github.com/FultonGeo/coordshift).
