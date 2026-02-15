"""Package shim to let static tools and scripts import `hiro_ust.<module>` while
actual implementation lives under `src/hiro_ust/`.
"""
import os

_this_dir = os.path.dirname(__file__)
_src_path = os.path.abspath(os.path.join(_this_dir, '..', 'src', 'hiro_ust'))
if os.path.isdir(_src_path) and _src_path not in __path__:
    __path__.insert(0, _src_path)

# Optionally expose a simple API marker
__all__ = []

