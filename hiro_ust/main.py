# hiro_ust/main.py
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import tkinter as tk
from gui.app import USTGeneratorApp

if __name__ == "__main__":
    root = tk.Tk()
    app = USTGeneratorApp(root)
    root.mainloop()
