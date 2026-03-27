"""
cli.py — Command line interface for coordshift.

Built with Click. This file is intentionally thin — it parses arguments
and calls functions from core.py and io.py. No conversion logic lives here.

Entry point is defined in pyproject.toml:
    [project.scripts]
    coordshift = "coordshift.cli:cli"
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from pandas.errors import EmptyDataError, ParserError

from coordshift import __version__
from coordshift.core import convert as convert_file
from coordshift.crs import CRSError, search_crs
from coordshift.presets import PRESETS


def _configure_utf8_stdio() -> None:
    """Use UTF-8 for stdout/stderr when possible (Windows consoles often default to cp1252)."""
    for stream in (getattr(sys, "stdout", None), getattr(sys, "stderr", None)):
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            continue


_configure_utf8_stdio()


def _default_output_path(input_path: str) -> str:
    """Return input path with ``_converted`` inserted before the file extension."""
    p = Path(input_path)
    if p.suffix:
        return str(p.with_name(f"{p.stem}_converted{p.suffix}"))
    return str(p.with_name(f"{p.name}_converted"))


def _format_preset_line(name: str, epsg: str, description: str) -> str:
    """Format one preset for terminal output."""
    return f"{name}  →  {epsg}  —  {description}"


@click.group()
@click.version_option(version=__version__)
def cli():
    """coordshift — Universal coordinate system conversion for CSV data."""
    pass


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--from", "from_crs", required=True, help="Source CRS (e.g. EPSG:4326, wgs84)")
@click.option("--to", "to_crs", required=True, help="Target CRS (e.g. EPSG:2965, indiana-east)")
@click.option("--x", default=None, help="X/longitude/easting column name (auto-detected if omitted)")
@click.option("--y", default=None, help="Y/latitude/northing column name (auto-detected if omitted)")
@click.option("--out", default=None, help="Output file path (default: input_converted.csv)")
def convert(filepath, from_crs, to_crs, x, y, out):
    """Convert coordinate columns in a CSV file from one CRS to another."""
    output_path = out if out else _default_output_path(filepath)
    x_col = x if x else None
    y_col = y if y else None

    try:
        df = convert_file(
            filepath,
            from_crs,
            to_crs,
            x=x_col,
            y=y_col,
            output=output_path,
        )
    except (
        CRSError,
        ValueError,
        KeyError,
        OSError,
        TypeError,
        EmptyDataError,
        ParserError,
        FileNotFoundError,
    ) as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1) from e

    n = len(df)
    click.echo(
        f"Converted {n} row(s) from {from_crs!r} to {to_crs!r}. "
        f"Output: {output_path}"
    )


@cli.command()
@click.argument("query")
def search(query):
    """Search for a CRS by name or keyword. Example: coordshift search 'indiana'"""
    results = search_crs(query)
    if not results:
        click.echo(f"No presets found matching: {query}")
        return
    for row in sorted(results, key=lambda r: r["name"]):
        click.echo(
            _format_preset_line(
                row["name"],
                str(row["epsg"]),
                str(row["description"]),
            )
        )


@cli.command()
def list_crs():
    """List all built-in CRS presets."""
    for name in sorted(PRESETS.keys()):
        data = PRESETS[name]
        click.echo(
            _format_preset_line(
                name,
                str(data["epsg"]),
                str(data.get("description", "")),
            )
        )
