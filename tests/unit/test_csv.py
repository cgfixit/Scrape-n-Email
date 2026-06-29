"""Tests for CSV helper utilities."""

from __future__ import annotations

from pathlib import Path

from scrape_n_email.csv import _csv_safe, append_row, init_csv


class TestCsvSafe:
    def test_passes_through_normal_text(self) -> None:
        assert _csv_safe("hello") == "hello"

    def test_null_becomes_empty(self) -> None:
        assert _csv_safe(None) == ""

    def test_formula_injection_prefixes_apostrophe(self) -> None:
        assert _csv_safe("=CMD()") == "'=CMD()"
        assert _csv_safe("+1") == "'+1"
        assert _csv_safe("-1") == "'-1"
        assert _csv_safe("@ref") == "'@ref"


class TestInitCsv:
    def test_creates_file_with_header(self, tmp_path: Path) -> None:
        import scrape_n_email.csv as csv_mod

        orig_path = csv_mod.CSV_PATH
        try:
            csv_mod.CSV_PATH = tmp_path / "test.csv"
            assert init_csv(force=True) is True
            assert "HEADLINE,URL" in csv_mod.CSV_PATH.read_text(encoding="utf-8")
        finally:
            csv_mod.CSV_PATH = orig_path

    def test_refuses_to_overwrite_without_force(self, tmp_path: Path) -> None:
        import scrape_n_email.csv as csv_mod

        orig_path = csv_mod.CSV_PATH
        try:
            csv_mod.CSV_PATH = tmp_path / "test.csv"
            csv_mod.CSV_PATH.write_text("existing,data\n", encoding="utf-8")
            assert init_csv(force=False) is False
            assert csv_mod.CSV_PATH.read_text(encoding="utf-8") == "existing,data\n"
        finally:
            csv_mod.CSV_PATH = orig_path

    def test_append_row(self, tmp_path: Path) -> None:
        import scrape_n_email.csv as csv_mod

        orig_path = csv_mod.CSV_PATH
        try:
            csv_mod.CSV_PATH = tmp_path / "test.csv"
            assert init_csv(force=True) is True
            assert append_row("Title", "https://example.com") is True
            assert "Title,https://example.com" in csv_mod.CSV_PATH.read_text(encoding="utf-8")
        finally:
            csv_mod.CSV_PATH = orig_path
