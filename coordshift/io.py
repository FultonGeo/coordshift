"""
io.py — File reading, column detection, and output writing.

Handles everything related to getting data in and out of coordshift.
Kept separate from core.py so conversion logic stays clean and testable
without needing actual files.
"""

import pandas as pd

# Common column name patterns we'll try to auto-detect
X_COLUMN_HINTS = ["lon", "longitude", "long", "x", "easting", "x_coord", "lng"]
Y_COLUMN_HINTS = ["lat", "latitude", "y", "northing", "y_coord"]


def _first_column_matching_hints(df: pd.DataFrame, hints: list[str]) -> str | None:
    """Return the first DataFrame column whose normalized name matches a hint."""
    hint_set = {h.lower() for h in hints}
    for col in df.columns:
        normalized = str(col).strip().lower()
        if normalized in hint_set:
            return str(col)
    return None


def read_csv(filepath: str) -> pd.DataFrame:
    """
    Read a CSV file into a pandas DataFrame.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pandas DataFrame.
    """
    return pd.read_csv(filepath)


def detect_columns(df: pd.DataFrame) -> tuple[str | None, str | None]:
    """
    Try to auto-detect which columns contain X and Y coordinates.

    Checks column names against known patterns (lon, lat, easting, etc.)
    Case-insensitive. Returns None for either if it can't find a match.

    Args:
        df: The input DataFrame.

    Returns:
        Tuple of (x_column_name, y_column_name). Either may be None.
    """
    x_col = _first_column_matching_hints(df, X_COLUMN_HINTS)
    y_col = _first_column_matching_hints(df, Y_COLUMN_HINTS)
    return x_col, y_col


def write_csv(df: pd.DataFrame, filepath: str) -> None:
    """
    Write a DataFrame to a CSV file.

    Args:
        df: The DataFrame to write.
        filepath: Output file path.
    """
    df.to_csv(filepath, index=False)
