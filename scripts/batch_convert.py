#!/usr/bin/env python
"""Convenience wrapper around the sw_version_converter package."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running directly from a source checkout without installing.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from sw_version_converter import cli  # noqa: E402


def main() -> int:
    here = Path(__file__).resolve().parent.parent
    inp = sys.argv[1] if len(sys.argv) > 1 else str(here / "CAD")
    out = sys.argv[2] if len(sys.argv) > 2 else None
    args = ["--help"]
    # Parse through the real CLI to honor flags.
    import argparse

    parser = cli._build_parser()
    parsed, _unknown = parser.parse_known_args([inp] + ([out] if out else []))
    return cli.main(
        [
            inp,
            "-o",
            out or parsed.output or str(Path(inp) / "_converted"),
            "--source-version",
            parsed.source_version,
            "--target-version",
            parsed.target_version,
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
