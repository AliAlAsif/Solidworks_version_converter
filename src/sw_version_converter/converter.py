"""Batch converter: SolidWorks future-version parts -> older-version formats.

The converter turns SolidWorks part files (``.sldprt``) saved in a *newer*
release (e.g. 2026) into a neutral, older-version-friendly format (Parasolid
``.x_t``) that SolidWorks 2024 and older can open natively.

It is implemented on top of the free, offline ``sldprt2xt`` package, which reads
the SolidWorks container (both known generations) and transcribes the embedded
Parasolid transmit without needing SolidWorks itself.

IMPORTANT
--------
This path preserves GEOMETRY but not the parametric feature tree. The feature
tree lives in version-specific internal data readable only by the version that
created it; see :func:`convert_feature_tree_with_solidworks` for the method that
keeps it (requires SolidWorks 2026+).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

PART_EXTENSION = ".sldprt"
TEMP_LOCK_PREFIX = "~$"

SUPPORTED_PART_EXTENSIONS = (PART_EXTENSION,)


@dataclass
class ConversionOutcome:
    """Result of converting one file."""

    source: str
    target: str
    status: str  # "ok" | "failed" | "skipped"
    message: str = ""


def iter_part_files(root: str) -> List[str]:
    """Recursively collect ``.sldprt`` files under ``root`` (sorted)."""
    root = str(root)
    found: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip temporary SolidWorks lock files/directories.
        dirnames[:] = sorted(
            d for d in dirnames if not d.startswith(TEMP_LOCK_PREFIX)
        )
        for name in sorted(filenames):
            if Path(name).suffix.lower() == PART_EXTENSION:
                found.append(os.path.join(dirpath, name))
    return found


def convert_part(source: str, output_dir: str) -> ConversionOutcome:
    """Convert a single ``.sldprt`` into a ``.x_t`` Parasolid file."""
    from sldprt2xt import ConversionError, to_x_t

    target_name = Path(source).stem + ".x_t"
    out_path = os.path.join(str(output_dir), target_name)

    try:
        to_x_t(str(source), str(output_dir))
    except ConversionError as exc:  # noqa: BLE001
        return ConversionOutcome(source, out_path, "failed", f"ConversionError: {exc}")
    except Exception as exc:  # noqa: BLE001
        return ConversionOutcome(source, out_path, "failed", f"{type(exc).__name__}: {exc}")

    return ConversionOutcome(source, out_path, "ok", "")


def convert_folder(
    input_dir: str,
    output_dir: str,
    source_version: Optional[str] = None,
    target_version: Optional[str] = None,
) -> List[ConversionOutcome]:
    """Convert every ``.sldprt`` under ``input_dir`` into ``output_dir``.

    Args:
        input_dir: Folder containing source SolidWorks part files.
        output_dir: Folder that receives the ``.x_t`` files.
        source_version: Optional label of the source SolidWorks release
            (e.g. ``"2026"``). Informational / reporting only.
        target_version: Optional label of the target SolidWorks release
            (e.g. ``"2024"``). Informational / reporting only.

    Returns:
        List of outcomes, one per source file.
    """
    os.makedirs(str(output_dir), exist_ok=True)
    files = iter_part_files(input_dir)
    outcomes: List[ConversionOutcome] = []
    for src in files:
        outcome = convert_part(src, output_dir)
        if source_version or target_version:
            outcome.message = (
                f"source={source_version or '?'} target={target_version or '?'}"
                f" | {outcome.message}"
            ).strip(" |")
        outcomes.append(outcome)
    return outcomes


def convert_feature_tree_with_solidworks(input_dir: str) -> str:
    """Feature-tree-preserving conversion requires SolidWorks 2026+.

    The native "Save As Previous Version" capability must be run inside a
    SolidWorks 2026+ installation; it cannot be executed from a 2024-only
    machine. See ``BatchDownsaveTo2024.swb`` in the repository root.
    """
    raise NotImplementedError(
        "Feature-tree-preserving conversion requires SolidWorks 2026+ and can "
        "only be run there. Use the BatchDownsaveTo2024.swb macro in that case."
    )
