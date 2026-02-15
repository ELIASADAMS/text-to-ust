"""
Launcher script for Hiro UST Generator GUI.

This script adds src/ to sys.path and launches the GUI application.
Can be run directly: python scripts/hiro_ust_dev.py
"""

# Thin launcher script to start the package entrypoint
import sys
import os
from pathlib import Path

# Ensure 'src' is on sys.path regardless of CWD
HERE = Path(__file__).resolve().parents[1]  # repository root
SRC = HERE / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Launch package CLI
from hiro_ust.cli import main

if __name__ == "__main__":
    debug = False
    if "--debug-gui" in sys.argv or "--debug" in sys.argv:
        debug = True
    main(debug=debug)
