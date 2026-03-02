"""
Phonetic utility functions for Japanese text processing.

Provides helpers for:
- Mora classification (consonant vs vowel)
- Phonetic feature extraction
- Text normalization
- Kana type detection

Used by melody generation, accent patterns, and text processing.
"""

from typing import List

from ..constants import VOWEL_CHARS, CONSONANT_CHARS


class MoraAnalyzer:
    """Analyzer for Japanese mora (syllable) properties.

    A mora is the fundamental unit of Japanese phonetic structure.
    Examples: か (ka), きゃ (kya), ん (n)
    """

    # Common vowel prolongation markers
    PROLONGATION_MARKERS = {"ー", "あ", "い", "う", "え", "お"}

    @staticmethod
    def get_vowel(mora: str) -> str:
        """Extract vowel from mora.

        Args:
            mora: Japanese mora string (e.g., "きゃ" → "a")

        Returns:
            Vowel character or empty string if not found
        """
        mora = mora.strip()
        if not mora:
            return ""

        # Single vowel
        if mora in VOWEL_CHARS:
            return mora

        # Multi-character mora: find first vowel
        for char in mora:
            if char in VOWEL_CHARS:
                return char

        return ""

    @staticmethod
    def get_consonant(mora: str) -> str:
        """Extract consonant from mora.

        Args:
            mora: Japanese mora string (e.g., "きゃ" → "kya")

        Returns:
            Consonant part or empty string if vowel-only
        """
        mora = mora.strip()
        if not mora:
            return ""

        # Pure vowel
        if mora in VOWEL_CHARS:
            return ""

        # Multi-character: consonant before vowel
        consonant = ""
        for char in mora:
            if char not in VOWEL_CHARS:
                consonant += char
            else:
                break

        return consonant

    @staticmethod
    def is_voiced(mora: str) -> bool:
        """Check if mora starts with voiced consonant.

        Voiced consonants: が行, ぎ行, ぐ行, げ行, ご行, etc.
        (ga, gi, gu, ge, go, da, di, du, de, do, ba, bi, bu, be, bo, etc.)

        Args:
            mora: Japanese mora

        Returns:
            True if mora has voiced consonant
        """
        first_char = mora[0] if mora else ""
        voiced_chars = set("がぎぐげござじずぜぞだぢづでどばびぶべぼ")
        return first_char in voiced_chars

    @staticmethod
    def is_geminate(mora: str) -> bool:
        """Check if mora is a geminate (small tsu, っ).

        Geminates double the following consonant.

        Args:
            mora: Japanese mora

        Returns:
            True if mora is っ
        """
        return mora == "っ"

    @staticmethod
    def is_nasal(mora: str) -> bool:
        """Check if mora is nasal (ん or ん-like).

        Args:
            mora: Japanese mora

        Returns:
            True if mora is ん or m-series
        """
        return mora in ("ん", "m", "ん゛")

    @staticmethod
    def is_long_vowel(mora: str) -> bool:
        """Check if mora is a long vowel.

        Long vowels in Japanese:
        - Doubled vowels: ああ, いい, etc.
        - Prolongation mark: ー
        - あ row with え, い row with い, etc.

        Args:
            mora: Japanese mora

        Returns:
            True if mora is extended vowel
        """
        if len(mora) < 2:
            return False

        # Check for doubled vowels
        if mora[0] == mora[1] and mora[0] in VOWEL_CHARS:
            return True

        # Check for prolongation patterns
        vowel_pairs = {
            "あい": True,  # おかあ → "a" + "i"
            "いい": True,
            "ああ": True,
            "ええ": True,
            "おう": True,
            "おお": True,
        }
        return mora in vowel_pairs or "ー" in mora

    @staticmethod
    def classify_mora_type(mora: str) -> str:
        """Classify mora into phonetic type.

        Args:
            mora: Japanese mora

        Returns:
            One of: "vowel", "consonant", "nasal", "geminate", "prolongation"
        """
        if MoraAnalyzer.is_geminate(mora):
            return "geminate"
        if MoraAnalyzer.is_nasal(mora):
            return "nasal"
        if mora in VOWEL_CHARS:
            return "vowel"
        if MoraAnalyzer.is_long_vowel(mora):
            return "prolongation"
        if mora[0] in CONSONANT_CHARS if mora else False:
            return "consonant"
        return "unknown"


class AccentAnalyzer:
    """Analyzer for Japanese accent patterns (pitch accent).

    Japanese has pitch accent patterns that vary by dialect and word.
    Common patterns: heiban (flat), atamadaka (head high), nakadaka (middle high), odaka (tail high).
    """

    # Accent pattern definitions
    ACCENT_PATTERNS = {
        "Heiban": {"description": "平板", "high_moras": []},  # All flat
        "Atamadaka": {"description": "頭高", "high_moras": [0]},  # First high
        "Nakadaka": {
            "description": "中高",
            "high_moras": [1],
        },  # Second+ high
        "Odaka": {"description": "尾高", "high_moras": [-1]},  # Last high
    }

    @staticmethod
    def get_accent_moras(
        accent_type: str, word_length: int
    ) -> List[int]:
        """Get high-pitch mora positions for accent type.

        Args:
            accent_type: One of "Heiban", "Atamadaka", "Nakadaka", "Odaka"
            word_length: Number of moras in word

        Returns:
            List of mora indices (0-based) that should be high pitch
        """
        if accent_type not in AccentAnalyzer.ACCENT_PATTERNS:
            return []

        pattern = AccentAnalyzer.ACCENT_PATTERNS[accent_type]
        moras = pattern["high_moras"]

        # Handle negative indices (from end)
        result = []
        for m in moras:
            if m < 0:
                result.append(word_length + m)
            else:
                result.append(m)

        return [m for m in result if 0 <= m < word_length]

    @staticmethod
    def should_be_high(mora_position: int, accent_type: str, word_length: int) -> bool:
        """Check if mora should be high pitch.

        Args:
            mora_position: Position in word (0-based)
            accent_type: Accent type
            word_length: Total moras in word

        Returns:
            True if mora should be high pitch
        """
        high_moras = AccentAnalyzer.get_accent_moras(accent_type, word_length)
        return mora_position in high_moras


class VowelHarmony:
    """Analyzer for Japanese vowel harmony patterns.

    Helps with phoneme-level melody decisions based on vowel characteristics.
    """

    # Vowel properties
    VOWEL_PROPERTIES = {
        "あ": {"height": "low", "backness": "back", "rounding": "unrounded"},
        "い": {"height": "high", "backness": "front", "rounding": "unrounded"},
        "う": {"height": "high", "backness": "back", "rounding": "rounded"},
        "え": {"height": "mid", "backness": "front", "rounding": "unrounded"},
        "お": {"height": "mid", "backness": "back", "rounding": "rounded"},
    }

    @staticmethod
    def get_vowel_openness(mora: str) -> int:
        """Get vowel openness (0=closed, 4=open).

        Open vowels (a, o) typically get longer durations.

        Args:
            mora: Mora containing vowel

        Returns:
            Openness value (0-4)
        """
        vowel = MoraAnalyzer.get_vowel(mora)

        openness_map = {
            "あ": 4,  # Most open
            "お": 3,
            "え": 2,
            "い": 1,
            "う": 0,  # Most closed
        }

        return openness_map.get(vowel, 2)

    @staticmethod
    def is_back_vowel(mora: str) -> bool:
        """Check if mora contains back vowel (a, o, u).

        Back vowels have different resonance characteristics.

        Args:
            mora: Mora containing vowel

        Returns:
            True if back vowel
        """
        vowel = MoraAnalyzer.get_vowel(mora)
        return vowel in ("あ", "お", "う")

    @staticmethod
    def is_high_vowel(mora: str) -> bool:
        """Check if mora contains high vowel (i, u).

        Args:
            mora: Mora containing vowel

        Returns:
            True if high vowel
        """
        vowel = MoraAnalyzer.get_vowel(mora)
        return vowel in ("い", "う")


class PhoneticNormalizer:
    """Normalizer for phonetic text variants.

    Handles different input formats and normalizes them.
    """

    @staticmethod
    def normalize_small_tsu_spacing(text: str) -> str:
        """Normalize small tsu (っ) spacing.

        Ensures っ is properly separated and recognized.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Remove extra spaces around っ
        import re

        text = re.sub(r"\s*っ\s*", "っ", text)
        return text

    @staticmethod
    def normalize_choonpu(text: str) -> str:
        """Normalize prolongation marks (ー choonpu).

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Ensure ー is recognized
        text = text.replace("−", "ー")  # Unicode minus sign
        text = text.replace("─", "ー")  # Horizontal bar
        text = text.replace("-", "ー")  # Hyphen (context-dependent)
        return text

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace variants.

        Args:
            text: Input text

        Returns:
            Text with normalized spaces
        """
        # Normalize full-width spaces to regular spaces
        text = text.replace("　", " ")
        # Remove multiple spaces
        import re

        text = re.sub(r"\s+", " ", text)
        return text


__all__ = [
    "MoraAnalyzer",
    "AccentAnalyzer",
    "VowelHarmony",
    "PhoneticNormalizer",
]


