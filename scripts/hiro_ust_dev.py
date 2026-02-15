"""
Launcher script for Hiro UST Generator GUI.

This script adds src/ to sys.path and launches the GUI application.
Can be run directly: python scripts/hiro_ust_dev.py
"""

import sys
import os

# Add src to path for importing hiro_ust package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Now import and run the GUI
from hiro_ust.ui import main

if __name__ == "__main__":
    main()


