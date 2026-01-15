"""
Main kanji conversion engine with automatic Kanken level merging.
"""

from typing import Dict, List
from .kanken_level_10 import KANKEN_10_READINGS
from .kanken_level_9 import KANKEN_9_READINGS

# Auto-merge all Kanken levels
KANJI_READINGS: Dict[str, str] = {}
KANKEN_LEVELS = {}


def _merge_kanken_levels():
    """Merge all Kanken levels into master dictionary."""
    global KANJI_READINGS, KANKEN_LEVELS

    # Level 10
    KANJI_READINGS.update(KANKEN_10_READINGS)
    KANKEN_LEVELS.update({k: "10" for k in KANKEN_10_READINGS})

    # Level 9
    KANJI_READINGS.update(KANKEN_9_READINGS)
    KANKEN_LEVELS.update({k: "9" for k in KANKEN_9_READINGS})

    # Level 8
    KANJI_READINGS.update(KANKEN_8_READINGS)
    KANKEN_LEVELS.update({k: "8" for k in KANKEN_8_READINGS})


_merge_kanken_levels()  # Run once at import


def kanji_to_hiragana(text: str) -> str:
    """Convert kanji compounds and mixed text to hiragana readings."""
    if not text:
        return text

    result = text
    # Longest-first matching
    for kanji, reading in sorted(KANJI_READINGS.items(), key=lambda x: len(x[0]), reverse=True):
        result = result.replace(kanji, reading)

    return result


def add_custom_reading(kanji: str, reading: str, level: str = "custom") -> None:
    """Add new kanji reading"""
    KANJI_READINGS[kanji] = reading
    KANKEN_LEVELS[kanji] = level


def get_missing_kanji(text: str) -> List[str]:
    """Find unconverted kanji characters"""
    result = kanji_to_hiragana(text)
    missing = []
    hiragana_range = set("ぁ-ん")

    for char in result:
        if char not in hiragana_range and not char.isascii():
            missing.append(char)

    return list(set(missing))


def get_stats() -> Dict:
    """Get conversion statistics"""
    return {
        "total_kanji": len(KANJI_READINGS),
        "level_10": len([k for k, v in KANKEN_LEVELS.items() if v == "10"]),
        "level_9": len([k for k, v in KANKEN_LEVELS.items() if v == "9"]),
        "level_8": len([k for k, v in KANKEN_LEVELS.items() if v == "8"]),
        "custom": len([k for k, v in KANKEN_LEVELS.items() if v == "custom"]),
    }


def batch_convert_lyrics(lyrics_lines: List[str]) -> List[str]:
    """Process multiple lines."""
    return [kanji_to_hiragana(line) for line in lyrics_lines]


if __name__ == "__main__":
    print("=== Kanji Converter Stats ===")
    print(get_stats())
    print("\n=== Test Conversions ===")
    test_cases = ["痛み嬉しい", "夜の影鬼", "美しい夢"]
    for test in test_cases:
        print(f"{test} → {kanji_to_hiragana(test)}")
