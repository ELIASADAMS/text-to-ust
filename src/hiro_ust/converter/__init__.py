"""Text and phoneme conversion utilities."""

from __future__ import annotations

from .hiragana_map import HIRAGANA_MAP
from .kana_to_hiragana import convert_lyrics
from .mora_trie import MORA_DATA, build_mora_trie
from .phonemizer import Phonemizer
from ..logger import get_logger

logger = get_logger(__name__)


class HiroUSTGenerator:
    """Mora-aware Japanese text converter used by the Hiro pipeline."""

    _instance: "HiroUSTGenerator | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.hiragana_map = HIRAGANA_MAP
            cls._instance.mora_trie = build_mora_trie()
            logger.debug("HiroUSTGenerator singleton created")
        return cls._instance

    def romaji_to_hiragana(self, phoneme: str) -> str:
        """Convert a supported romaji phoneme to kana."""
        if phoneme.startswith(("kk", "gg")):
            return self.hiragana_map.get(phoneme, phoneme)
        if phoneme in {"ji", "zu"}:
            return self.hiragana_map.get("ji_s", phoneme)
        if phoneme == "ji_t":
            return self.hiragana_map.get("ji_t", phoneme)
        return self.hiragana_map.get(phoneme, phoneme)

    def hiragana_to_romaji(self, text: str) -> list[str]:
        """Convert Japanese kana into mora/phoneme tokens using longest match."""
        text = convert_lyrics(text.strip())
        phonemes: list[str] = []
        i = 0

        while i < len(text):
            node = self.mora_trie
            start = i
            best_match = None
            best_end = i

            while i < len(text) and text[i] in node:
                node = node[text[i]]
                i += 1
                if node.get("end"):
                    best_match = node
                    best_end = i

            if best_match is not None:
                phonemes.extend(best_match["phones"])
                i = best_end
                continue

            char = text[start]
            if char == "っ":
                phonemes.append("っ")
            elif char in "。、「」『』！？,，、…" or char.isspace():
                phonemes.append(char)
            else:
                logger.warning("Unrecognized kana character: %r", char)
            i = start + 1

        return phonemes


__all__ = ["HiroUSTGenerator", "Phonemizer", "MORA_DATA"]
