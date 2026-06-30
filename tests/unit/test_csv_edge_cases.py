"""Edge-case tests for CSV: formula injection variants, OSError paths, init modes."""

from __future__ import annotations

from pathlib import Path

import scrape_n_email.csv as csv_mod
from scrape_n_email.csv import _csv_safe, append_row, init_csv


class TestCsvSafeExtended:
    def test_tab_prefix_is_escaped(self) -> None:
        assert _csv_safe("\tdata") == "'\tdata"

    def test_cr_prefix_is_escaped(self) -> None:
        assert _csv_safe("\rdata") == "'\rdata"

    def test_empty_string_passes(self) -> None:
        assert _csv_safe("") == ""

    def test_numeric_passthrough(self) -> None:
        assert _csv_safe(42) == "42"


class TestInitCsvErrors:
    def test_init_csv_oserror(self, tmp_path: Path) -> None:
        orig = csv_mod.CSV_PATH
        try:
            csv_mod.CSV_PATH = tmp_path / "nodir" / "test.csv"
            assert init_csv(force=True) is False
        finally:
            csv_mod.CSV_PATH = orig

    def test_init_csv_exclusive_mode_race(self, tmp_path: Path) -> None:
        orig = csv_mod.CSV_PATH
        try:
            csv_mod.CSV_PATH = tmp_path / "test.csv"
            csv_mod.CSV_PATH.write_text("", encoding="utf-8")
            assert init_csv(force=False) is False
        finally:
            csv_mod.CSV_PATH = orig


class TestAppendRowErrors:
    def test_append_oserror(self, tmp_path: Path) -> None:
        orig = csv_mod.CSV_PATH
        try:
            csv_mod.CSV_PATH = tmp_path / "nodir" / "missing.csv"
            assert append_row("title", "link") is False
        finally:
            csv_mod.CSV_PATH = orig

    def test_append_with_formula_injection_values(self, tmp_path: Path) -> None:
        orig = csv_mod.CSV_PATH
        try:
            csv_mod.CSV_PATH = tmp_path / "test.csv"
            init_csv(force=True)
            assert append_row("=CMD()", "+http://evil.com") is True
            content = csv_mod.CSV_PATH.read_text(encoding="utf-8")
            assert "'=CMD()" in content
            assert "'+http://evil.com" in content
        finally:
            csv_mod.CSV_PATH = orig
