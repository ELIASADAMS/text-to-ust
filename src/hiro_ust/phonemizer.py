# Bridge module to expose Phonemizer at package top-level
from hiro_ust.converter.phonemizer import Phonemizer, ROMAJI_MAP

__all__ = ["Phonemizer", "ROMAJI_MAP"]

# ROMAJI_MAP should be provided by converter.phonemizer; set to None if missing
try:
    ROMAJI_MAP  # noqa: F401
except Exception:
    ROMAJI_MAP = None
