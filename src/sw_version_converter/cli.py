"""Command-line interface for the SolidWorks version converter."""

from __future__ import annotations

import argparse
from typing import List, Optional, Sequence

from .converter import convert_folder, iter_part_files

DEFAULT_SOURCE_VERSION = "2026"
DEFAULT_TARGET_VERSION = "2024"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sw-version-converter",
        description=(
            "Convert SolidWorks future-version CAD part files (e.g. saved in "
            "SolidWorks 2026) into a format that older SolidWorks versions "
            "(e.g. SolidWorks 2024) can open natively."
        ),
        epilog=(
            "Notes:\n"
            "  * Requires Python 3.10+ and the 'sldprt2xt' package.\n"
            "  * Converts geometry only; the parametric feature tree is not "
            "preserved (see README)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="CAD",
        help="Input folder containing .sldprt files (default: ./CAD)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output folder for converted .x_t files (default: <input>/_converted)",
    )
    parser.add_argument(
        "--source-version",
        default=DEFAULT_SOURCE_VERSION,
        help=f"Source SolidWorks version label (default: {DEFAULT_SOURCE_VERSION})",
    )
    parser.add_argument(
        "--target-version",
        default=DEFAULT_TARGET_VERSION,
        help=f"Target SolidWorks version label (default: {DEFAULT_TARGET_VERSION})",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    import os

    input_dir = args.input
    output_dir = args.output or os.path.join(str(input_dir), "_converted")

    outcomes = convert_folder(
        input_dir=input_dir,
        output_dir=output_dir,
        source_version=args.source_version,
        target_version=args.target_version,
    )

    files = iter_part_files(input_dir)
    print("=" * 60)
    print(f"Source  : {input_dir}")
    print(f"Output  : {output_dir}")
    print(f"Source version : {args.source_version}")
    print(f"Target version : {args.target_version}")
    print(f"Parts   : {len(outcomes)}")
    print("=" * 60)

    ok = failed = skipped = 0
    for outcome in outcomes:
        mark = outcome.status.upper().ljust(7)
        print(f"{mark} {os.path.basename(outcome.source)} -> {os.path.basename(outcome.target)}")
        if outcome.status == "ok":
            ok += 1
        elif outcome.status == "failed":
            failed += 1
            print(f"        error: {outcome.message}")
        elif outcome.status == "skipped":
            skipped += 1

    print("-" * 60)
    print(f"Converted: {ok}   Failed: {failed}   Skipped: {skipped}")

    if failed > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
