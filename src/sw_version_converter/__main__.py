"""Allow running the converter via ``python -m sw_version_converter``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
