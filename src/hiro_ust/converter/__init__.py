"""
Text and phoneme conversion module.

Provides conversion between different text formats (hiragana, katakana, romaji)
and phoneme representations.

Components:
  - HiroUSTGenerator: Hiragana↔romaji conversion using mora trie
  - Phonemizer: Multi-mode phoneme conversion
  - Mora trie data and mappings
"""

from .mora_trie import build_mora_trie, MORA_DATA
from hiro_ust.hiragana_map import HIRAGANA_MAP
from hiro_ust.kana_to_hiragana import convert_lyrics
from hiro_ust.phonemizer import Phonemizer
from hiro_ust.logger import get_logger

logger = get_logger(__name__)


class HiroUSTGenerator:
    """Singleton generator for hiragana/katakana to romaji conversion.

    Builds a mora-based trie from MORA_DATA for efficient conversion of
    Japanese text to romaji phonemes. Caches hiragana mappings.

    Attributes:
        hiragana_map (dict): Mapping from romaji to hiragana characters
        mora_trie (dict): Trie structure for mora-based text matching
    """
    _instance = None

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.hiragana_map = HIRAGANA_MAP
            cls._instance.mora_trie = build_mora_trie()
        return cls._instance

    def romaji_to_hiragana(self, phoneme: str) -> str:
        """Convert romaji phoneme to hiragana character.

        Args:
            phoneme: Romaji string (e.g., 'ka', 'ji_s', 'ji_t')

        Returns:
            Hiragana character or original phoneme if not found
        """
        if phoneme.startswith("kk") or phoneme.startswith("gg"):
            return self.hiragana_map.get(phoneme, phoneme)
        if phoneme in ["ji", "zu"]:
            return self.hiragana_map.get("ji_s", phoneme)
        if phoneme == "ji_t":
            return self.hiragana_map.get("ji_t", phoneme)
        return self.hiragana_map.get(phoneme, phoneme)

    def hiragana_to_romaji(self, text: str) -> list:
        """Convert hiragana/katakana text to list of romaji phonemes.

        Uses trie-based matching for efficient mora parsing.
        Handles small tsu (っ) for gemination.

        Args:
            text: Hiragana or katakana text string

        Returns:
            List of romaji phoneme strings
        """
        phonemes = []
        i = 0
        text = text.strip()
        text = convert_lyrics(text)

        while i < len(text):
            node = self.mora_trie
            start = i
            best_match = None
            best_end = i

            while i < len(text) and text[i] in node:
                node = node[text[i]]
                i += 1

                if "end" in node and node["end"]:
                    best_match = node
                    best_end = i

            if best_match and best_match["end"]:
                phonemes.extend(best_match["phones"])
                i = best_end
            else:
                char = text[start]
                if char == "っ":  # Sokuon (small tsu = gemination)
                    phonemes.append("っ")
                    i = start + 1
                else:
                    i = start + 1

        return phonemes


__all__ = [
    "HiroUSTGenerator",
    "Phonemizer",
    "MORA_DATA",
]

