# coordshift

> Universal coordinate system conversion for CSV and tabular data — built for GIS analysts, surveyors, and drone mapping workflows.

---

## What It Does

`coordshift` lets you take any CSV file with coordinate columns and reproject them from one coordinate reference system (CRS) to another — using any system supported by PROJ.

```bash
coordshift convert input.csv --from EPSG:4326 --to EPSG:2965 --x lon --y lat
```

Or in Python:

```python
from coordshift import convert

df = convert("input.csv", from_crs="EPSG:4326", to_crs="EPSG:2965", x="lon", y="lat")
```

---

## Why This Exists

Existing tools (cs2cs, ogr2ogr, pyproj CLI) are powerful but unfriendly. They assume you already know what you're doing. `coordshift` is built for practitioners — surveyors, drone operators, GIS analysts — who need fast, repeatable coordinate conversion without wrestling with PROJ syntax.

---

## Planned Features

- [ ] Convert any EPSG/PROJ CRS to any other
- [ ] Auto-detect common column names (lat, lon, x, y, easting, northing, etc.)
- [ ] Specify source and target CRS by EPSG code, PROJ string, or friendly name
- [ ] Preserve all non-coordinate columns in output
- [ ] CLI for one-off conversions
- [ ] Python API for scripting and pipeline integration
- [ ] Optional vertical coordinate handling (ellipsoidal ↔ orthometric, GEOID support)
- [ ] Batch conversion across multiple files
- [ ] Output to CSV, GeoJSON, or Shapefile
- [ ] Interactive CRS selector (fuzzy search by name or state plane zone)

---

## Installation

> Not yet published — coming to PyPI soon.

```bash
pip install coordshift
```

---

## Usage

### CLI

```bash
# Basic conversion
coordshift convert input.csv --from EPSG:4326 --to EPSG:2965 --x lon --y lat

# Specify output file
coordshift convert input.csv --from EPSG:4326 --to EPSG:2965 --x lon --y lat --out output.csv

# Use PROJ strings instead of EPSG codes
coordshift convert input.csv \
  --from "+proj=longlat +datum=WGS84" \
  --to "+proj=tmerc +lat_0=37.5 +lon_0=-85.66666667 +k=0.999966667 +x_0=100000 +y_0=250000 +ellps=GRS80" \
  --x longitude --y latitude

# List supported CRS presets
coordshift list-crs

# Search for a CRS by name
coordshift search "indiana east"
```

### Python API

```python
from coordshift import convert, list_crs, search_crs

# Convert a CSV file — returns a pandas DataFrame
df = convert(
    "field_points.csv",
    from_crs="EPSG:4326",
    to_crs="EPSG:2965",
    x="lon",
    y="lat"
)

# Save output
df.to_csv("field_points_converted.csv", index=False)

# Search for a CRS
results = search_crs("indiana east")
```

---

## Project Structure

```
coordshift/
├── coordshift/
│   ├── __init__.py         # Public API surface
│   ├── core.py             # Conversion logic (pyproj wrapper)
│   ├── cli.py              # CLI entry point (Click)
│   ├── io.py               # CSV read/write, column detection
│   ├── crs.py              # CRS resolution (EPSG, PROJ string, presets)
│   └── presets.py          # Friendly name → EPSG mappings
├── tests/
│   ├── test_core.py
│   ├── test_cli.py
│   └── fixtures/           # Sample CSVs for testing
├── docs/
│   └── examples.md         # Real-world workflow examples
├── pyproject.toml          # Package config, dependencies, CLI entry point
├── README.md
└── LICENSE
```

---

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/coordshift.git
cd coordshift
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

---

## Dependencies

- [pyproj](https://pyproj4.github.io/pyproj/) — PROJ bindings for Python
- [pandas](https://pandas.pydata.org/) — CSV/tabular data handling
- [click](https://click.palletsprojects.com/) — CLI framework

---

## Contributing

Contributions welcome. Please open an issue before submitting a large PR so we can discuss direction.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Push and open a Pull Request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

Built by [Nick Fulton](https://github.com/YOUR_USERNAME) — Geospatial Manager, FAA Part 107, 11+ years drone/survey experience.
