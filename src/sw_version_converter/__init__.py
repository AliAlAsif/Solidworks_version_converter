"""SolidWorks future-version to older-version CAD converter."""

from .converter import ConversionOutcome, convert_folder, convert_part, iter_part_files

__all__ = [
    "ConversionOutcome",
    "convert_folder",
    "convert_part",
    "iter_part_files",
]

__version__ = "1.0.0"
