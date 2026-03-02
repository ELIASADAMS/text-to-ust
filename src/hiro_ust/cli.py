"""CLI entrypoint for Hiro UST.
"""

import sys
from pathlib import Path
import tkinter as tk

root = Path(__file__).resolve().parents[1]  # src/hiro_ust/.. -> src
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from hiro_ust.hiro_ust_dev import USTGeneratorApp, HiroConfig  # type: ignore


def main(argv=None, debug=False):
    argv = argv or sys.argv[1:]
    root_tk = tk.Tk()
    app = USTGeneratorApp(root_tk)
    if debug:
        print("[hiro_ust.cli] GUI initialized (debug mode)")
        return app
    # Normal run: start event loop
    root_tk.mainloop()


if __name__ == "__main__":
    main()
