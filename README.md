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
coordshift convert input.csv --from EPSG:4326 --to EPSG:6458 --x lon --y lat
```

**Python**

```python
from coordshift import convert

df = convert("input.csv", from_crs="EPSG:4326", to_crs="EPSG:6458", x="lon", y="lat")
```

**Browser**

Open `coordshift.html` in any modern browser — no install required.

## Why this exists

Tools like cs2cs, ogr2ogr, and raw pyproj are powerful but assume you already speak PROJ. `coordshift` targets practitioners who need fast, repeatable conversions without wrestling with syntax.

## What's included

- Convert any EPSG/PROJ CRS to any other
- Auto-detect common column names (lat, lon, x, y, easting, northing, etc.)
- Source and target CRS via EPSG code, PROJ string, or anything else PROJ resolves; `coordshift search` finds USA EPSG entries by keyword
- Preserve all columns in output — original X/Y columns are always kept
- Converted coordinates written to new columns placed immediately after the originals
- Customisable output column suffix (default `_converted`, e.g. `lon_converted`, `lat_converted`)
- CLI for one-off conversions
- Python API for scripting and pipelines
- Browser-based converter (`coordshift.html`) with map preview — works offline, supports NAD83(2011)
  geographic (EPSG:6318) for RTK/CORS survey workflows, with datum accuracy warnings for frames that
  proj4.js cannot rigorously transform (e.g. NAD83(2011) ↔ ITRF2014)

## Planned

- Vertical coordinate support (ellipsoidal ↔ orthometric, GEOID)
- Batch conversion across multiple files
- Output to GeoJSON or Shapefile

## Installation

Install from [PyPI](https://pypi.org/project/coordshift/) (Python 3.10+):

```bash
pip install coordshift
```

**From source** (for development or unreleased changes):

```bash
git clone https://github.com/FultonGeo/coordshift.git
cd coordshift
pip install -e .
```

## Usage

### CLI

Basic conversion (original `lon`/`lat` columns are preserved; converted values go into `lon_converted`/`lat_converted` placed right after them):

```bash
coordshift convert input.csv --from EPSG:4326 --to EPSG:6458 --x lon --y lat
```

With output path:

```bash
coordshift convert input.csv --from EPSG:4326 --to EPSG:6458 --x lon --y lat --out output.csv
```

Custom column name suffix (produces `lon_proj`, `lat_proj` instead of the default `lon_converted`, `lat_converted`):

```bash
coordshift convert input.csv --from EPSG:4326 --to EPSG:6458 --suffix _proj
```

PROJ strings (use a single line on Windows, or wrap as your shell allows):

```bash
coordshift convert input.csv \
  --from "+proj=longlat +datum=WGS84" \
  --to "+proj=tmerc +lat_0=37.5 +lon_0=-85.66666667 +k=0.999966667 +x_0=100000 +y_0=250000 +ellps=GRS80" \
  --x longitude --y latitude
```

Search the EPSG database (filtered to USA) — one or more words, all must match:

```bash
coordshift search iowa south
coordshift search indiana east
coordshift search nad83 2011 utm zone 15
```

The browser file `coordshift.html` includes a searchable CRS catalog for convenience. The Python tools rely on EPSG/PROJ plus `search` as above.

### Python API

```python
from coordshift import convert, search_crs

df = convert(
    "field_points.csv",
    from_crs="EPSG:4326",
    to_crs="EPSG:6458",
    x="lon",
    y="lat",
)
# df now has lon, lon_converted, lat, lat_converted (plus any other original columns)
df.to_csv("field_points_converted.csv", index=False)

# Search returns all matching EPSG entries from the PROJ database (USA-filtered)
results = search_crs("indiana east")
for r in results:
    print(r["epsg"], "—", r["name"])
```

See [docs/examples.md](docs/examples.md) for more detailed examples.

### Browser app

Open `coordshift.html` in any modern browser (Chrome, Firefox, Edge, Safari). No server or internet connection required after the page loads.

**How to use** — click **?** in the header to open the step-by-step guide:

![coordshift browser app: How to use (instruction modal)](https://raw.githubusercontent.com/FultonGeo/coordshift/main/docs/images/coordshift_howto_html.png)

**Example** — map preview with input points (blue) and converted sample output (red); when the CRS pair is correct, the preview rings overlap the input dots:

![coordshift browser app: sample conversion preview on the map](https://raw.githubusercontent.com/FultonGeo/coordshift/main/docs/images/coordshift_html_example.png)

Features include:

- Upload a CSV and pick coordinate columns
- Search and select source/target CRS from a built-in catalog that includes:
  - **WGS 84** geographic (EPSG:4326) and Web Mercator (EPSG:3857)
  - **NAD83(2011) geographic lat/lon (EPSG:6318)** — the reference frame reported by RTK GNSS
    receivers observing from U.S. CORS networks; the correct source CRS for professional survey
    fieldwork in the USA
  - **ITRF2014** frame epoch 2010.0 (EPSG:9000)
  - All **NAD83(2011) State Plane** zones for the contiguous U.S. and UTM zones
- **Map preview rings for all target CRS** — sample rings are back-projected to WGS 84 for
  display, so rings land on the input points for projected output (State Plane, UTM) just as they
  do for geographic output. Rings drift visibly if the wrong CRS is chosen.
- **Datum accuracy warnings** — an amber notice appears when the selected CRS pair has an offset
  that proj4.js cannot model:
  - *NAD83(2011) ↔ ITRF2014*: ~1 m (~4 ft) in CONUS due to tectonic plate drift since 1992
  - *WGS 84 ↔ ITRF2014*: <2 cm (current WGS 84 G2139); directs users to EPSG:6318 for the
    survey-grade NAD83 ↔ ITRF workflow
- Download the converted CSV

## Project structure

```text
coordshift/
├── coordshift/         # Python package
│   ├── __init__.py    # Public API
│   ├── core.py        # Conversion (pyproj)
│   ├── cli.py         # CLI (Click)
│   ├── io.py          # CSV I/O, column detection
│   └── crs.py         # CRS resolution and EPSG search
├── tests/
│   ├── test_core.py
│   ├── test_cli.py
│   ├── test_io.py
│   └── fixtures/
├── docs/
│   ├── examples.md
│   └── images/         # README screenshots (browser app)
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

**Links:** [PyPI](https://pypi.org/project/coordshift/) · [GitHub](https://github.com/FultonGeo/coordshift)
