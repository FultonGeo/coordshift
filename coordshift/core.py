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
) -> pd.DataFrame:
    """
    Convert coordinate columns in a CSV file from one CRS to another.

    Args:
        filepath: Path to the input CSV file.
        from_crs: Source CRS — EPSG code (e.g. "EPSG:4326"), PROJ string, or preset name.
        to_crs: Target CRS — same formats accepted.
        x: Name of the X/longitude/easting column. Auto-detected if not provided.
        y: Name of the Y/latitude/northing column. Auto-detected if not provided.
        output: Path to save the output CSV. If None, returns DataFrame only.

    Returns:
        pandas DataFrame with converted coordinate columns. All other columns preserved.
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

    out = df_in.copy()
    xs = out[x_col].astype(float).tolist()
    ys = out[y_col].astype(float).tolist()
    new_xs, new_ys = transform_points(xs, ys, from_resolved, to_resolved)
    out[x_col] = new_xs
    out[y_col] = new_ys

    if output is not None:
        io.write_csv(out, output)

    return out
