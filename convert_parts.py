#!/usr/bin/env python
"""Batch-convert SolidWorks future-version parts to older-version formats.

Thin CLI wrapper around the ``sw_version_converter`` package.

Examples
--------
    python convert_parts.py
    python convert_parts.py ./CAD ./converted_2024
    python convert_parts.py ./CAD -o ./converted_2024
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from sw_version_converter import cli as _cli  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    raw = list(sys.argv[1:]) if argv is None else list(argv)

    positional: list[str] = []
    source_version = "2026"
    target_version = "2024"
    output_dir: str | None = None

    i = 0
    while i < len(raw):
        a = raw[i]
        if a == "--source-version":
            source_version = raw[i + 1]
            i += 2
            continue
        if a == "--target-version":
            target_version = raw[i + 1]
            i += 2
            continue
        if a in ("-o", "--output"):
            output_dir = raw[i + 1]
            i += 2
            continue
        if not a.startswith("-"):
            positional.append(a)
        i += 1

    input_dir = positional[0] if positional else str(here / "CAD")
    if len(positional) > 1 and output_dir is None:
        output_dir = positional[1]

    return _cli.main(
        [
            input_dir,
            "-o",
            output_dir or str(Path(input_dir) / "_converted"),
            "--source-version",
            source_version,
            "--target-version",
            target_version,
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
