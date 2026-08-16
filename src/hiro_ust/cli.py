"""Canonical GUI entry point for Hiro UST."""

from __future__ import annotations

import sys
import tkinter as tk

from .hiro_ust_dev import USTGeneratorApp


def main(argv=None, debug: bool = False):
    """Start the Hiro GUI.

    The ``hiro_ust_dev`` module currently contains the working legacy GUI
    implementation. This module is the stable public launcher so callers do
    not need to know that internal filename.
    """
    _ = argv if argv is not None else sys.argv[1:]
    root = tk.Tk()
    app = USTGeneratorApp(root)
    if debug:
        print("[hiro_ust] GUI initialized (debug mode)")
        return app
    root.mainloop()
    return None


__all__ = ["main", "USTGeneratorApp"]


if __name__ == "__main__":
    main()
