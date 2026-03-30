# coordshift — Examples

> **⚠ Alpha software — always verify results**
>
> coordshift is in early development. Always cross-check converted coordinates against a trusted independent source before using them in any survey, legal, safety-critical, or production context. The authors accept no liability for errors in conversion results.

Worked examples for the CLI, Python API, and browser app.

## Installation

```bash
pip install coordshift
```

See the package on PyPI: https://pypi.org/project/coordshift/

---

## CLI

### Basic conversion: WGS 84 to Indiana State Plane East

```bash
coordshift convert survey_points.csv --from EPSG:4326 --to EPSG:6458 --x lon --y lat
```

### RTK/CORS survey data: NAD83(2011) geographic to State Plane (meters)

For field data collected with an RTK receiver observing against U.S. CORS networks, use
EPSG:6318 (NAD83(2011) geographic) as the source rather than WGS 84:

```bash
# NAD83(2011) lat/lon → Indiana East State Plane NAD83(2011) meters
coordshift convert rtk_field_points.csv --from EPSG:6318 --to EPSG:6458 --x lon --y lat

# NAD83(2011) lat/lon → Indiana East State Plane NAD83(2011) US survey feet
coordshift convert rtk_field_points.csv --from EPSG:6318 --to EPSG:6459 --x lon --y lat
```

The original `lon` and `lat` columns are always preserved. Converted values are written to `lon_converted` and `lat_converted`, placed immediately after their originals. Output is saved to `survey_points_converted.csv` by default. Use `--out` to choose a path:

```bash
coordshift convert survey_points.csv --from EPSG:4326 --to EPSG:6458 --out projected.csv
```

### Finding the right EPSG code

Search the full EPSG database (filtered to the USA) by keyword. One or more words — all must match:

```bash
coordshift search iowa south
coordshift search indiana east
coordshift search nad83 2011 iowa north ftus
coordshift search utm zone 15
coordshift search colorado north
```

Example output for `coordshift search iowa south`:

```
EPSG:2795  —  NAD83(HARN) / Iowa South
EPSG:3418  —  NAD83 / Iowa South (ftUS)
EPSG:3426  —  NAD83(HARN) / Iowa South (ftUS)
EPSG:3538  —  NAD83(NSRS2007) / Iowa South
EPSG:3539  —  NAD83(NSRS2007) / Iowa South (ftUS)
EPSG:6464  —  NAD83(2011) / Iowa South
EPSG:6465  —  NAD83(2011) / Iowa South (ftUS)
EPSG:8738  —  NAD83 / Iowa South (ftUS) + NAVD88 height (ftUS)
EPSG:26776  —  NAD27 / Iowa South
EPSG:26976  —  NAD83 / Iowa South
```

### CRS inputs (Python and CLI)

Use **EPSG codes** (e.g. `EPSG:4326`), **PROJ strings**, or any other form **PROJ** resolves without ambiguity. There are no short name presets in the package—if you know a zone by name, run `coordshift search` (or `search_crs()` in Python) and paste the EPSG code from the results.

The **browser app** (`coordshift.html`) still ships a large embedded catalog for client-side search only.

```bash
coordshift convert survey_points.csv --from EPSG:4326 --to EPSG:6458
```

### Custom column name suffix with `--suffix`

By default converted columns are named `lon_converted` and `lat_converted`. Use `--suffix` to customise:

```bash
coordshift convert survey_points.csv --from EPSG:4326 --to EPSG:6458 --suffix _proj
```

Original `lon`, `lat` columns are preserved. Converted values go into `lon_proj` and `lat_proj`, placed immediately after them.

### PROJ strings

Use any PROJ string your version of PROJ supports:

```bash
coordshift convert input.csv \
  --from "+proj=longlat +datum=WGS84" \
  --to "+proj=tmerc +lat_0=37.5 +lon_0=-85.66666667 +k=0.999966667 +x_0=100000 +y_0=250000 +ellps=GRS80" \
  --x longitude --y latitude
```

On Windows PowerShell, combine onto one line or use backtick line continuation.

### Auto-detection of coordinate columns

If your CSV has columns named `lon`/`lat`, `longitude`/`latitude`, `x`/`y`, `easting`/`northing`, or similar, you can omit `--x` and `--y`:

```bash
coordshift convert survey_points.csv --from EPSG:4326 --to EPSG:6458
```

---

## Python API

### Simple conversion

```python
from coordshift import convert

df = convert(
    "survey_points.csv",
    from_crs="EPSG:4326",
    to_crs="EPSG:6458",
    x="lon",
    y="lat",
)
# Columns: lon, lon_converted, lat, lat_converted, <other original columns>
print(df.head())
df.to_csv("survey_points_projected.csv", index=False)
```

### Round-trip check

```python
from coordshift.core import transform_points

xs_proj, ys_proj = transform_points([-86.15], [39.77], "EPSG:4326", "EPSG:6458")
xs_back, ys_back = transform_points(xs_proj, ys_proj, "EPSG:6458", "EPSG:4326")

print(f"Original:   {-86.15}, {39.77}")
print(f"Round-trip: {xs_back[0]:.6f}, {ys_back[0]:.6f}")
```

### Custom suffix programmatically

```python
from coordshift import convert

df = convert(
    "survey_points.csv",
    from_crs="EPSG:4326",
    to_crs="EPSG:6458",
    suffix="_proj",
    output="survey_points_with_proj.csv",
)
# Columns: lon, lon_proj, lat, lat_proj, <other originals>
print(df.columns.tolist())
```

### Searching the EPSG database

```python
from coordshift import search_crs

# All words must match — works with single or multi-word queries
results = search_crs("iowa south")
for r in results:
    print(r["epsg"], "—", r["name"])
# EPSG:2795  —  NAD83(HARN) / Iowa South
# EPSG:3418  —  NAD83 / Iowa South (ftUS)
# ...
# EPSG:6464  —  NAD83(2011) / Iowa South
# EPSG:6465  —  NAD83(2011) / Iowa South (ftUS)
```

Each result dict contains: `epsg`, `name`, `type`, `area_of_use`.

### Working with DataFrames directly

`convert()` returns a pandas DataFrame, so you can chain it with any pandas workflow:

```python
import pandas as pd
from coordshift import convert

df = convert("gps_log.csv", from_crs="EPSG:4326", to_crs="EPSG:26916")
# Filter points inside a bounding box using the converted (projected) coords
df_clipped = df[(df["lon_converted"] > 500000) & (df["lon_converted"] < 600000)]
df_clipped.to_csv("clipped.csv", index=False)
```

---

## Browser App (`coordshift.html`)

1. Open `coordshift.html` in Chrome, Firefox, Edge, or Safari.
2. Click **Open CSV** (or drag a CSV onto the toolbar) to load your file.
3. Select the **source CRS** — type to search (e.g. `"nad83 2011"`, `"indiana east"`, `"utm 16"`).
4. Select the **target CRS**.
5. Pick X (longitude/easting) and Y (latitude/northing) columns if they were not auto-detected.
6. A preview of sample output rings appears on the map. Rings should overlap the blue input dots
   when the correct CRS pair is chosen. For projected output (State Plane, UTM) the rings are
   back-projected to WGS 84 for display — they still land on the input dots.
7. Click **Convert** to reproject all rows.
8. Click **⬇ Download** to save the result CSV.

The app embeds a full catalog of NAD83(2011) State Plane zones, UTM zones, and common geographic
CRS (see the header for the full list). It uses [proj4js](https://github.com/proj4js/proj4js) for
in-browser reprojection and works entirely offline once the page is loaded.

### RTK / CORS survey workflow (NAD83(2011) → State Plane)

RTK GNSS receivers observing against U.S. CORS networks (NGS CORS, Leica SmartNet, Trimble VRS,
etc.) report coordinates in **NAD83(2011)** — not WGS 84. Use **EPSG:6318** as the source CRS.

Example: field points collected in Indiana with a Trimble R12, stored as lat/lon in NAD83(2011),
converted to Indiana East State Plane (NAD83(2011), meters):

| Source CRS | `NAD83(2011) geographic lat/lon — EPSG:6318` |
|---|---|
| Target CRS | `Indiana East — EPSG:6458` |
| X column | `lon` (or `longitude`) |
| Y column | `lat` (or `latitude`) |

Output columns added: `lon_converted` (easting, metres), `lat_converted` (northing, metres).

**Why not WGS 84?** WGS 84 (EPSG:4326) and NAD83(2011) (EPSG:6318) differ by roughly 1 m (~4 ft)
in CONUS because WGS 84 tracks the ITRF global frame while NAD83 is fixed to the North American
tectonic plate. For projected output in State Plane metres/feet the difference is negligible in
many workflows, but for the most accurate results always use the correct datum.

### NAD83(2011) ↔ ITRF2014 — rigorous datum shift (Python CLI only)

The ~1 m offset between NAD83(2011) and ITRF2014 requires a **14-parameter time-dependent
Helmert transformation** (plate-motion parameters from the IERS ITRF2014 combination). PROJ
has these parameters built in — no external grids, no network access, no extra downloads.

The browser tool (`coordshift.html`) uses proj4.js, which does not include this transformation,
so it will display an amber warning and produce near-identical coordinates for this pair. Use
the Python CLI or API for accurate results.

```bash
coordshift convert survey.csv --from EPSG:6318 --to EPSG:9000 --x lon --y lat
```

```python
from coordshift.core import transform_points

# NAD83(2011) → ITRF2014 using PROJ's built-in 14-parameter Helmert (epoch 2010.0)
# Expected shift in CONUS: ~0.4–1 m depending on location and direction
xs_itrf, ys_itrf = transform_points(
    xs=[-86.15],
    ys=[39.77],
    from_crs="EPSG:6318",
    to_crs="EPSG:9000",
)
print(xs_itrf, ys_itrf)
# → [-86.15000768...], [39.77000769...]  (~0.86 m northing shift near Indianapolis)
```

Reverse conversion:

```bash
coordshift convert itrf_points.csv --from EPSG:9000 --to EPSG:6318 --x lon --y lat
```

---

## Sample fixture

`tests/fixtures/wgs84_points.csv`:

```csv
lon,lat,site
-86.15,39.77,Bloomington vicinity
```

Expected output after converting to Indiana State Plane East NAD83(2011) (EPSG:6458):

| lon | lon_converted | lat | lat_converted | site |
|-----|---------------|-----|----------------|------|
| -86.15 | 192222.22 | 39.77 | 1647282.68 | Bloomington vicinity |
