"""
Mora-based trie structure for efficient Japanese text processing.

This module provides the core trie-building and mora data structures
used for converting hiragana to romaji phonemes.
"""

from ..data.mora_trie_data import MORA_DATA
from hiro_ust.logger import get_logger

logger = get_logger(__name__)


def build_mora_trie() -> dict:
    """Build trie structure from MORA_DATA for efficient text matching.

    The trie enables fast matching of mora sequences in Japanese text.
    Each node has:
        - child nodes for each character
        - 'end': True if node marks end of mora
        - 'phones': list of romaji phonemes for this mora

    Returns:
        dict: Trie structure

    Example:
        >>> trie = build_mora_trie()
        >>> # 'きゃ' -> ['kya']
        >>> trie['き']['ゃ']['end'] == True
    """
    mora_trie = {}

    for mora, phones in MORA_DATA.items():
        node = mora_trie
        for char in mora:
            if char not in node:
                node[char] = {"end": False, "phones": None}
            node = node[char]
        node["end"] = True
        node["phones"] = phones

    logger.debug(f"Built mora trie with {len(MORA_DATA)} entries")
    return mora_trie


__all__ = [
    "build_mora_trie",
    "MORA_DATA",
]
