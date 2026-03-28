# coordshift — Examples

Worked examples for the CLI, Python API, and browser app.

---

## CLI

### Basic conversion: WGS84 to Indiana State Plane East

```bash
coordshift convert survey_points.csv --from EPSG:4326 --to EPSG:2965 --x lon --y lat
```

The original `lon` and `lat` columns are always preserved. Converted values are written to `lon_converted` and `lat_converted`, placed immediately after their originals. Output is saved to `survey_points_converted.csv` by default. Use `--out` to choose a path:

```bash
coordshift convert survey_points.csv --from EPSG:4326 --to EPSG:2965 --out projected.csv
```

### Using friendly preset names

Instead of EPSG codes you can use built-in preset names:

```bash
coordshift convert survey_points.csv --from wgs84 --to indiana-east
```

List all available presets:

```bash
coordshift list-crs
```

Search by keyword:

```bash
coordshift search "indiana"
coordshift search "utm zone 16"
```

### Custom column name suffix with `--suffix`

By default converted columns are named `lon_converted` and `lat_converted`. Use `--suffix` to customise:

```bash
coordshift convert survey_points.csv --from wgs84 --to indiana-east --suffix _proj
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
coordshift convert survey_points.csv --from wgs84 --to indiana-east
```

---

## Python API

### Simple conversion

```python
from coordshift import convert

df = convert(
    "survey_points.csv",
    from_crs="EPSG:4326",
    to_crs="EPSG:2965",
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
from coordshift.crs import resolve_crs

wgs84 = resolve_crs("wgs84")
ind_e = resolve_crs("indiana-east")

xs_proj, ys_proj = transform_points([-86.15], [39.77], wgs84, ind_e)
xs_back, ys_back = transform_points(xs_proj, ys_proj, ind_e, wgs84)

print(f"Original:  {-86.15}, {39.77}")
print(f"Round-trip: {xs_back[0]:.6f}, {ys_back[0]:.6f}")
```

### Custom suffix programmatically

```python
from coordshift import convert

df = convert(
    "survey_points.csv",
    from_crs="wgs84",
    to_crs="indiana-east",
    suffix="_proj",
    output="survey_points_with_proj.csv",
)
# Columns: lon, lon_proj, lat, lat_proj, <other originals>
print(df.columns.tolist())
```

### Searching presets

```python
from coordshift import search_crs

results = search_crs("indiana")
for r in results:
    print(r["name"], "→", r["epsg"], "—", r["description"])
```

### Working with DataFrames directly

`convert()` returns a pandas DataFrame, so you can chain it with any pandas workflow:

```python
import pandas as pd
from coordshift import convert

df = convert("gps_log.csv", from_crs="wgs84", to_crs="utm-16n")
# Filter points inside a bounding box using the converted (projected) coords
df_clipped = df[(df["lon_converted"] > 500000) & (df["lon_converted"] < 600000)]
df_clipped.to_csv("clipped.csv", index=False)
```

---

## Browser App (`coordshift.html`)

1. Open `coordshift.html` in Chrome, Firefox, Edge, or Safari.
2. Click **Choose File** and upload a CSV.
3. Select the source CRS from the dropdown or type to search (e.g. "indiana east", "utm 16").
4. Select the target CRS.
5. Pick X (easting/longitude) and Y (northing/latitude) columns if they were not auto-detected.
6. Click **Convert** — points appear on the map preview.
7. Click **Download CSV** to save the result.

The app embeds a full catalog of NAD83(2011) State Plane zones, UTM zones, and common geographic CRS. It uses [proj4js](https://github.com/proj4js/proj4js) for in-browser reprojection and works entirely offline once the page is loaded.

---

## Sample fixture

`tests/fixtures/wgs84_points.csv`:

```csv
lon,lat,site
-86.15,39.77,Bloomington vicinity
```

Expected output after converting to Indiana State Plane East (EPSG:2965):

| lon | lon_converted | lat | lat_converted | site |
|-----|---------------|-----|----------------|------|
| -86.15 | 192222.22 | 39.77 | 1647282.68 | Bloomington vicinity |
