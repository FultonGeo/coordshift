"""
core.py — The main conversion logic.

This is the heart of coordshift. Everything else (CLI, file I/O) calls
functions from here. Keeping conversion logic here means it can be used
both from the command line and from Python scripts.
"""

import pandas as pd
from pyproj import Transformer
from pyproj.exceptions import CRSError as PyprojCRSError

from coordshift.crs import CRSError, resolve_crs

from . import io


def transform_points(
    xs: list[float],
    ys: list[float],
    from_crs: str,
    to_crs: str,
) -> tuple[list[float], list[float]]:
    """
    Transform a list of X/Y points from one CRS to another.

    Args:
        xs: List of X values (longitude or easting).
        ys: List of Y values (latitude or northing).
        from_crs: Source CRS string (e.g. from ``resolve_crs`` or an EPSG code).
        to_crs: Target CRS string in the same forms as ``from_crs``.

    Returns:
        Tuple of (transformed_xs, transformed_ys).
    """
    try:
        transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)
    except PyprojCRSError as e:
        raise CRSError(
            f"Could not build coordinate transform from {from_crs!r} to {to_crs!r}: {e}. "
            "Use resolvable CRS strings or preset names. "
            "Run `coordshift search` to list presets."
        ) from e
    tx, ty = transformer.transform(xs, ys)
    return [float(v) for v in tx], [float(v) for v in ty]


def convert(
    filepath: str,
    from_crs: str,
    to_crs: str,
    x: str | None = None,
    y: str | None = None,
    output: str | None = None,
    suffix: str = "_converted",
) -> pd.DataFrame:
    """
    Convert coordinate columns in a CSV file from one CRS to another.

    The original X/Y columns are always preserved. Converted values are written
    to new columns named ``{x}{suffix}`` and ``{y}{suffix}``, inserted immediately
    after their respective originals.

    Args:
        filepath: Path to the input CSV file.
        from_crs: Source CRS — EPSG code (e.g. "EPSG:4326"), PROJ string, or preset name.
        to_crs: Target CRS — same formats accepted.
        x: Name of the X/longitude/easting column. Auto-detected if not provided.
        y: Name of the Y/latitude/northing column. Auto-detected if not provided.
        output: Path to save the output CSV. If None, returns DataFrame only.
        suffix: Suffix appended to X/Y column names to form the output column names
            (default ``"_converted"``). For example, with ``x="lon"`` and
            ``suffix="_proj"``, the output column is ``"lon_proj"``.

    Returns:
        pandas DataFrame with original coordinate columns preserved and new converted
        columns inserted immediately after them. All other columns are unchanged.
    """
    from_resolved = resolve_crs(from_crs)
    to_resolved = resolve_crs(to_crs)

    df_in = io.read_csv(filepath)
    x_col = x
    y_col = y
    if x_col is None or y_col is None:
        auto_x, auto_y = io.detect_columns(df_in)
        if x_col is None:
            x_col = auto_x
        if y_col is None:
            y_col = auto_y

    if x_col is None or y_col is None:
        raise ValueError(
            "Could not determine X/Y columns. "
            "Pass x= and y= with column names, or use recognizable names such as "
            f"lon/lat (hints: {io.X_COLUMN_HINTS}, {io.Y_COLUMN_HINTS})."
        )

    x_out = f"{x_col}{suffix}"
    y_out = f"{y_col}{suffix}"
    for name in (x_out, y_out):
        if name in df_in.columns:
            raise ValueError(
                f"Column {name!r} already exists. Choose a different --suffix or rename the input column."
            )

    out = df_in.copy()
    xs = out[x_col].astype(float).tolist()
    ys = out[y_col].astype(float).tolist()
    new_xs, new_ys = transform_points(xs, ys, from_resolved, to_resolved)

    out[x_out] = new_xs
    out[y_out] = new_ys

    # Insert the new columns immediately after their originals
    cols = [c for c in out.columns if c not in (x_out, y_out)]
    x_idx = cols.index(x_col)
    cols.insert(x_idx + 1, x_out)
    y_idx = cols.index(y_col)
    cols.insert(y_idx + 1, y_out)
    out = out[cols]

    if output is not None:
        io.write_csv(out, output)

    return out
