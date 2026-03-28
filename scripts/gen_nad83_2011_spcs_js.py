"""Emit NAD83(2011) zone catalog for docs/index.html (run from repo root)."""

import json
from pathlib import Path

from pyproj.database import query_crs_info


def collect_spcs_rows() -> list[dict[str, object]]:
    rows = list(query_crs_info(auth_name="EPSG", pj_types="PROJECTED_CRS"))
    banned_substrings = (
        "EPSG Arctic",
        "Amtrak",
        "ICS83",
        "San Francisco SFO",
        "Adjusted Jackson",
        "NECCS",
    )

    def good(r: object) -> bool:
        n = getattr(r, "name", None) or ""
        if "NAD83(2011)" not in n or " / " not in n:
            return False
        if any(b in n for b in banned_substrings):
            return False
        try:
            c = int(getattr(r, "code", 0))
        except (TypeError, ValueError):
            return False
        return 6300 <= c <= 6999

    items = [(int(r.code), r.name) for r in rows if good(r)]
    items.sort(key=lambda x: x[1])
    out_rows = []
    for code, name in items:
        short = name.split(" / ", 1)[1]
        out_rows.append({"code": code, "label": f"{short} — EPSG:{code}"})
    return out_rows


def main() -> None:
    out_rows = collect_spcs_rows()
    compact = json.dumps(out_rows, separators=(",", ":"))
    Path("docs/_nad83_2011_spcs.json").write_text(compact, encoding="utf-8")
    print(f"wrote {len(out_rows)} entries to docs/_nad83_2011_spcs.json")


if __name__ == "__main__":
    main()
