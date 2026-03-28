"""Tests for coordshift.io (CSV read, column detection, write)."""

from pathlib import Path

import pandas as pd
import pytest

from coordshift.io import X_COLUMN_HINTS, Y_COLUMN_HINTS, detect_columns, read_csv, write_csv

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestReadCsv:
    def test_reads_fixture_file(self) -> None:
        """read_csv returns a DataFrame for the fixture CSV."""
        df = read_csv(str(FIXTURES / "wgs84_points.csv"))
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 1

    def test_fixture_has_expected_columns(self) -> None:
        """Fixture CSV has lon, lat, site columns."""
        df = read_csv(str(FIXTURES / "wgs84_points.csv"))
        assert "lon" in df.columns
        assert "lat" in df.columns

    def test_fixture_values(self) -> None:
        """Fixture first row matches known WGS84 test point."""
        df = read_csv(str(FIXTURES / "wgs84_points.csv"))
        assert df["lon"].iloc[0] == pytest.approx(-86.15)
        assert df["lat"].iloc[0] == pytest.approx(39.77)

    def test_missing_file_raises(self) -> None:
        """read_csv raises an OSError-family exception for a non-existent file."""
        with pytest.raises((FileNotFoundError, OSError)):
            read_csv("does_not_exist_12345.csv")

    def test_roundtrip_preserves_data(self, tmp_path: Path) -> None:
        """Writing then reading a DataFrame produces identical values."""
        df_orig = read_csv(str(FIXTURES / "wgs84_points.csv"))
        out = tmp_path / "rt.csv"
        write_csv(df_orig, str(out))
        df_rt = read_csv(str(out))
        assert list(df_orig.columns) == list(df_rt.columns)
        assert df_orig["lon"].iloc[0] == pytest.approx(df_rt["lon"].iloc[0])


class TestDetectColumns:
    def _df(self, cols: list[str]) -> pd.DataFrame:
        return pd.DataFrame({c: [0.0] for c in cols})

    def test_detects_lon_lat(self) -> None:
        df = self._df(["lon", "lat", "site"])
        x, y = detect_columns(df)
        assert x == "lon"
        assert y == "lat"

    def test_detects_longitude_latitude(self) -> None:
        df = self._df(["longitude", "latitude"])
        x, y = detect_columns(df)
        assert x == "longitude"
        assert y == "latitude"

    def test_detects_easting_northing(self) -> None:
        df = self._df(["easting", "northing", "id"])
        x, y = detect_columns(df)
        assert x == "easting"
        assert y == "northing"

    def test_detects_x_y(self) -> None:
        df = self._df(["x", "y"])
        x, y = detect_columns(df)
        assert x == "x"
        assert y == "y"

    def test_case_insensitive(self) -> None:
        df = self._df(["LON", "LAT"])
        x, y = detect_columns(df)
        assert x == "LON"
        assert y == "LAT"

    def test_returns_none_for_unrecognized_columns(self) -> None:
        df = self._df(["alpha", "beta", "gamma"])
        x, y = detect_columns(df)
        assert x is None
        assert y is None

    def test_returns_none_x_when_only_y_found(self) -> None:
        df = self._df(["lat", "site"])
        x, y = detect_columns(df)
        assert x is None
        assert y == "lat"

    def test_returns_none_y_when_only_x_found(self) -> None:
        df = self._df(["lon", "site"])
        x, y = detect_columns(df)
        assert x == "lon"
        assert y is None

    def test_hints_constants_are_nonempty(self) -> None:
        """X_COLUMN_HINTS and Y_COLUMN_HINTS must have at least one entry each."""
        assert len(X_COLUMN_HINTS) >= 1
        assert len(Y_COLUMN_HINTS) >= 1


class TestWriteCsv:
    def test_creates_file(self, tmp_path: Path) -> None:
        """write_csv creates the output file."""
        df = pd.DataFrame({"lon": [-86.15], "lat": [39.77]})
        out = tmp_path / "out.csv"
        write_csv(df, str(out))
        assert out.is_file()

    def test_no_index_column(self, tmp_path: Path) -> None:
        """write_csv does not include an unnamed index column."""
        df = pd.DataFrame({"lon": [-86.15], "lat": [39.77]})
        out = tmp_path / "out.csv"
        write_csv(df, str(out))
        content = out.read_text()
        assert content.startswith("lon,lat")

    def test_preserves_all_columns(self, tmp_path: Path) -> None:
        """write_csv preserves all columns including non-coordinate ones."""
        df = pd.DataFrame({"lon": [-86.15], "lat": [39.77], "site": ["test"]})
        out = tmp_path / "out.csv"
        write_csv(df, str(out))
        df_back = read_csv(str(out))
        assert "site" in df_back.columns
        assert df_back["site"].iloc[0] == "test"
