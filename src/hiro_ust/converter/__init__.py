"""
Text and phoneme conversion module.

"""

from .mora_trie import build_mora_trie, MORA_DATA

try:
    from hiro_ust.hiragana_map import HIRAGANA_MAP
    from hiro_ust.kana_to_hiragana import convert_lyrics
    from hiro_ust.phonemizer import Phonemizer
except ImportError as e:
    # Fallback
    HIRAGANA_MAP = {}
    convert_lyrics = lambda x: x
    Phonemizer = None

from hiro_ust.logger import get_logger

logger = get_logger(__name__)


class HiroUSTGenerator:

    _instance = None

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Import here to avoid circular imports
            from hiro_ust.hiragana_map import HIRAGANA_MAP as hmap

            cls._instance.hiragana_map = hmap
            cls._instance.mora_trie = build_mora_trie()
            logger.debug("HiroUSTGenerator singleton created")
        return cls._instance

    def romaji_to_hiragana(self, phoneme: str) -> str:
        """
        Convert romaji phoneme to hiragana character.

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
        """
        Convert hiragana/katakana text to list of romaji phonemes.

        Args:
            text: Hiragana or katakana text string

        Returns:
            List of romaji phoneme strings
        """
        from hiro_ust.kana_to_hiragana import convert_lyrics as convert

        phonemes = []
        i = 0
        text = text.strip()
        text = convert(text)

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
