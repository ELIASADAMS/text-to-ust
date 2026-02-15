import sys, os

sys.path.insert(0, os.path.abspath("src"))
import importlib

try:
    mod = importlib.import_module("hiro_ust.hiro_ust_dev")
    p = importlib.import_module("hiro_ust.phonemizer")
    print("HiroUSTGenerator present:", hasattr(mod, "HiroUSTGenerator"))
    print("Phonemizer present:", hasattr(p, "Phonemizer"))
except Exception as e:
    print("Import failed:", repr(e))
    raise
