# Phonemizer at package top-level
from hiro_ust.converter.phonemizer import Phonemizer, ROMAJI_MAP

__all__ = ["Phonemizer", "ROMAJI_MAP"]


try:
    ROMAJI_MAP
except Exception:
    ROMAJI_MAP = None
