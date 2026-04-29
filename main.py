"""Compatibility launcher for running the project from a source checkout."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Start the newspaper restoration command-line application."""
    src_dir = Path(__file__).resolve().parent / "src"
    src_path = str(src_dir)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    from newspaper_restoration.app import main as app_main

    app_main()


if __name__ == "__main__":
    main()
