"""
Launcher script for Hiro UST Generator GUI.
"""

import sys
import os
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
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
