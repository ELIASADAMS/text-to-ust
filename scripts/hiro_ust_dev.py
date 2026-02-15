"""Launcher for the GUI during development.
Adds src/ to sys.path and calls hiro_ust.hiro_ust_dev.main().
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from importlib import import_module

mod = import_module('hiro_ust.hiro_ust_dev')
if hasattr(mod, 'main'):
    mod.main()
else:
    print('Module has no main() — run as package (python -m hiro_ust.hiro_ust_dev)')

