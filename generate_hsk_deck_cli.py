#!/usr/bin/env python3
"""Backward compatible CLI shim delegating to ``tian-hanzi deck build``."""
from __future__ import annotations

import sys

from src.tian_hanzi.cli import main as cli_main


def main() -> None:
    print("This entry point is deprecated. Use `tian-hanzi deck build` instead.\n")
    cli_main()


if __name__ == "__main__":
    sys.exit(main())
