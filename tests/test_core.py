"""Tests for coordshift.core (transforms and CSV conversion)."""

from pathlib import Path

import pytest

from coordshift.core import convert, transform_points
from coordshift.crs import CRSError, resolve_crs

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_wgs84_to_indiana_east_transform_points() -> None:
    """Known WGS84 lon/lat projects to Indiana State Plane East (EPSG:2965)."""
    from_crs = resolve_crs("EPSG:4326")
    to_crs = resolve_crs("EPSG:2965")
    xs, ys = transform_points(
        xs=[-86.15],
        ys=[39.77],
        from_crs=from_crs,
        to_crs=to_crs,
    )
    assert xs[0] == pytest.approx(192222.22, abs=1.0)
    assert ys[0] == pytest.approx(1647282.68, abs=1.0)


def test_wgs84_indiana_east_round_trip() -> None:
    """WGS84 → Indiana East → WGS84 closes within 0.0001 degrees."""
    lon0, lat0 = -86.1525, 39.7689
    wgs84 = resolve_crs("EPSG:4326")
    ind_e = resolve_crs("EPSG:2965")

    xe, ye = transform_points([lon0], [lat0], wgs84, ind_e)
    lon1, lat1 = transform_points(xe, ye, ind_e, wgs84)

    assert lon1[0] == pytest.approx(lon0, abs=0.0001)
    assert lat1[0] == pytest.approx(lat0, abs=0.0001)


def test_invalid_crs_raises_crerror() -> None:
    """Invalid CRS text must raise CRSError (not a bare pyproj error)."""
    with pytest.raises(CRSError, match="coordshift search"):
        resolve_crs("EPSG:999999999")


def test_convert_reads_and_writes(tmp_path: Path) -> None:
    """convert() auto-detects columns, preserves originals, and adds converted cols after them."""
    inp = FIXTURES / "wgs84_points.csv"
    outp = tmp_path / "out.csv"
    df = convert(
        str(inp),
        from_crs="EPSG:4326",
        to_crs="EPSG:2965",
        output=str(outp),
    )
    assert outp.is_file()
    # Originals preserved unchanged
    assert df["lon"].iloc[0] == pytest.approx(-86.15, abs=1e-6)
    assert df["lat"].iloc[0] == pytest.approx(39.77, abs=1e-6)
    # Converted columns added with default _converted suffix
    assert "lon_converted" in df.columns and "lat_converted" in df.columns
    assert df["lon_converted"].iloc[0] == pytest.approx(192222.22, abs=1.0)
    assert df["lat_converted"].iloc[0] == pytest.approx(1647282.68, abs=1.0)
    # Converted columns sit immediately after the originals
    cols = list(df.columns)
    assert cols.index("lon_converted") == cols.index("lon") + 1
    assert cols.index("lat_converted") == cols.index("lat") + 1


def test_convert_with_suffix_keeps_original_columns(tmp_path: Path) -> None:
    """With suffix=, new columns hold projected coords and lon/lat stay as WGS84."""
    inp = FIXTURES / "wgs84_points.csv"
    outp = tmp_path / "out_suffix.csv"
    df = convert(
        str(inp),
        from_crs="EPSG:4326",
        to_crs="EPSG:2965",
        suffix="_converted",
        output=str(outp),
    )
    assert outp.is_file()
    assert df["lon"].iloc[0] == pytest.approx(-86.15, abs=1e-6)
    assert df["lat"].iloc[0] == pytest.approx(39.77, abs=1e-6)
    assert "lon_converted" in df.columns and "lat_converted" in df.columns
    assert df["lon_converted"].iloc[0] == pytest.approx(192222.22, abs=1.0)
    assert df["lat_converted"].iloc[0] == pytest.approx(1647282.68, abs=1.0)
