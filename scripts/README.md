# scripts/

Developer tooling for regenerating the CRS catalog embedded in `coordshift.html`.

These scripts are **not** part of the `coordshift` Python package. Run them only when you need to update the NAD83(2011) State Plane / UTM catalog that ships inside the browser app.

---

## Scripts

### `gen_nad83_2011_spcs_js.py`

Fetches and formats the full NAD83(2011) State Plane Coordinate System catalog from the PROJ database and writes it as a JSON file.

**Output:** `docs/_nad83_2011_spcs.json`

```bash
python scripts/gen_nad83_2011_spcs_js.py
```

### `merge_spcs_into_index.py`

Reads `docs/_nad83_2011_spcs.json` and embeds it into the `<script type="application/json">` block inside `coordshift.html`. On first run it performs an initial inject; on subsequent runs it replaces the existing block.

**Prerequisite:** `gen_nad83_2011_spcs_js.py` must have run first.

```bash
python scripts/merge_spcs_into_index.py
```

---

## Typical workflow

```bash
# 1. Regenerate the catalog JSON
python scripts/gen_nad83_2011_spcs_js.py

# 2. Embed it into the browser app
python scripts/merge_spcs_into_index.py
```

Run both scripts from the project root. After step 2, open `coordshift.html` in a browser to verify the updated catalog loads correctly.

---

## When to re-run

- When adding or correcting CRS entries in the catalog
- After a PROJ version upgrade that changes EPSG definitions
- When the `coordshift.html` app JavaScript is restructured in a way that changes the injection anchor point
