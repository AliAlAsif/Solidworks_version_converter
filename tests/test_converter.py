"""Tests for the SolidWorks version converter."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from sw_version_converter import converter


def _touch(root: Path, rel: str, content: str = "x") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_iter_part_files_finds_sldprt(tmp_path: Path) -> None:
    _touch(tmp_path, "part1.SLDPRT")
    _touch(tmp_path, "sub/part2.SLDPRT")
    _touch(tmp_path, "notes.txt")
    _touch(tmp_path, "~$lock.SLDPRT")  # temp lock file must be ignored
    found = converter.iter_part_files(str(tmp_path))
    assert len(found) == 2
    assert any(f.endswith("part1.SLDPRT") for f in found)
    assert any(f.endswith("part2.SLDPRT") for f in found)


def test_convert_folder_reports_outcomes(tmp_path: Path) -> None:
    _touch(tmp_path / "in", "A.SLDPRT", "data")
    _touch(tmp_path / "in", "B.SLDPRT", "data")
    outcomes = converter.convert_folder(
        input_dir=str(tmp_path / "in"),
        output_dir=str(tmp_path / "out"),
        source_version="2026",
        target_version="2024",
    )
    assert len(outcomes) == 2
    statuses = sorted(o.status for o in outcomes)
    # Both files converted to .x_t -> both should be ok in a working env, or failed.
    # We only assert the structure here.
    assert all(o.source.endswith(".SLDPRT") for o in outcomes)
    assert all(o.target.endswith(".x_t") for o in outcomes)
    assert all(o.status in ("ok", "failed") for o in outcomes)
