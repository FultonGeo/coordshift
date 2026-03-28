"""Tests for the coordshift CLI (coordshift.cli)."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from coordshift.cli import cli

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture()
def runner() -> CliRunner:
    """Return a Click test runner with UTF-8 charset."""
    return CliRunner(charset="utf-8")


class TestConvertCommand:
    def test_basic_conversion_writes_output(self, runner: CliRunner, tmp_path: Path) -> None:
        """convert writes a file and prints a success message."""
        inp = FIXTURES / "wgs84_points.csv"
        out = tmp_path / "out.csv"
        result = runner.invoke(
            cli,
            ["convert", str(inp), "--from", "wgs84", "--to", "indiana-east", "--out", str(out)],
        )
        assert result.exit_code == 0, result.output
        assert out.is_file()
        assert "Converted" in result.output

    def test_auto_detects_columns(self, runner: CliRunner, tmp_path: Path) -> None:
        """convert succeeds without explicit --x and --y when column names are recognizable."""
        inp = FIXTURES / "wgs84_points.csv"
        out = tmp_path / "out.csv"
        result = runner.invoke(
            cli,
            ["convert", str(inp), "--from", "EPSG:4326", "--to", "EPSG:2965", "--out", str(out)],
        )
        assert result.exit_code == 0, result.output

    def test_suffix_flag_accepted(self, runner: CliRunner, tmp_path: Path) -> None:
        """convert --suffix writes without error and reports converted rows."""
        inp = FIXTURES / "wgs84_points.csv"
        out = tmp_path / "out_suffix.csv"
        result = runner.invoke(
            cli,
            [
                "convert",
                str(inp),
                "--from",
                "wgs84",
                "--to",
                "indiana-east",
                "--suffix",
                "_proj",
                "--out",
                str(out),
            ],
        )
        assert result.exit_code == 0, result.output
        assert out.is_file()

    def test_invalid_from_crs_exits_nonzero(self, runner: CliRunner, tmp_path: Path) -> None:
        """convert exits with code 1 and prints an error for an unresolvable source CRS."""
        inp = FIXTURES / "wgs84_points.csv"
        out = tmp_path / "out.csv"
        result = runner.invoke(
            cli,
            ["convert", str(inp), "--from", "EPSG:9999999999", "--to", "indiana-east", "--out", str(out)],
        )
        assert result.exit_code == 1

    def test_missing_file_exits_nonzero(self, runner: CliRunner) -> None:
        """convert exits with a non-zero code when the input file does not exist."""
        result = runner.invoke(
            cli,
            ["convert", "nonexistent.csv", "--from", "wgs84", "--to", "indiana-east"],
        )
        assert result.exit_code != 0

    def test_row_count_in_output(self, runner: CliRunner, tmp_path: Path) -> None:
        """convert reports the correct number of converted rows."""
        inp = FIXTURES / "wgs84_points.csv"
        out = tmp_path / "out.csv"
        result = runner.invoke(
            cli,
            ["convert", str(inp), "--from", "wgs84", "--to", "indiana-east", "--out", str(out)],
        )
        assert "1 row" in result.output


class TestSearchCommand:
    def test_search_returns_results(self, runner: CliRunner) -> None:
        """search prints matching preset rows for a known keyword."""
        result = runner.invoke(cli, ["search", "indiana"])
        assert result.exit_code == 0
        assert "indiana" in result.output.lower()

    def test_search_no_results(self, runner: CliRunner) -> None:
        """search prints a 'no results' message for an unknown keyword."""
        result = runner.invoke(cli, ["search", "zzznomatch999"])
        assert result.exit_code == 0
        assert "No presets found" in result.output

    def test_search_utm(self, runner: CliRunner) -> None:
        """search finds UTM zone entries."""
        result = runner.invoke(cli, ["search", "utm"])
        assert result.exit_code == 0
        assert "utm" in result.output.lower()


class TestListCrsCommand:
    def test_list_crs_shows_presets(self, runner: CliRunner) -> None:
        """list-crs prints at least one preset line."""
        result = runner.invoke(cli, ["list-crs"])
        assert result.exit_code == 0
        assert len(result.output.strip().splitlines()) >= 1

    def test_list_crs_contains_wgs84(self, runner: CliRunner) -> None:
        """list-crs output includes the wgs84 preset."""
        result = runner.invoke(cli, ["list-crs"])
        assert "wgs84" in result.output.lower()

    def test_list_crs_contains_indiana_east(self, runner: CliRunner) -> None:
        """list-crs output includes the indiana-east preset."""
        result = runner.invoke(cli, ["list-crs"])
        assert "indiana-east" in result.output.lower()


class TestVersionFlag:
    def test_version_flag(self, runner: CliRunner) -> None:
        """--version prints the package version."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
