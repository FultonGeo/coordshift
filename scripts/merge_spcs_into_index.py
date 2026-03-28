"""Refresh embedded NAD83(2011) catalog JSON inside coordshift.html.

Run after: python scripts/gen_nad83_2011_spcs_js.py
(which writes docs/_nad83_2011_spcs.json).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCK = re.compile(
    r'(<script type="application/json" id="nad83-2011-spcs-data">)(.*?)(</script>\s*\n  <script>\n\(function \(\) \{)',
    re.DOTALL,
)


def main() -> None:
    json_path = ROOT / "docs/_nad83_2011_spcs.json"
    idx = ROOT / "coordshift.html"
    json_txt = json_path.read_text(encoding="utf-8")
    html = idx.read_text(encoding="utf-8")
    m = BLOCK.search(html)
    if m:

        def repl(match: re.Match[str]) -> str:
            return match.group(1) + json_txt + match.group(3)

        idx.write_text(BLOCK.sub(repl, html, count=1), encoding="utf-8")
        print("updated embedded catalog in coordshift.html")
        return
    needle = "  <script>\n(function () {"
    inject = (
        '  <script type="application/json" id="nad83-2011-spcs-data">'
        + json_txt
        + "</script>\n  <script>\n(function () {"
    )
    if needle not in html:
        raise SystemExit("needle not found for first-time inject")
    idx.write_text(html.replace(needle, inject, 1), encoding="utf-8")
    print("first-time inject of catalog into coordshift.html")


if __name__ == "__main__":
    main()
