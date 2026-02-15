# phonemizer.py
import re

# Hepburn/Wapuro → Hiragana conversion table
ROMAJI_MAP = {
    # Vowels
    "a": "あ",
    "i": "い",
    "u": "う",
    "e": "え",
    "o": "お",
    "ā": "あー",
    "ī": "いー",
    "ū": "うー",
    "ē": "えー",
    "ō": "おー",
    # K + Vowels
    "ka": "か",
    "ki": "き",
    "ku": "く",
    "ke": "け",
    "ko": "こ",
    "ga": "が",
    "gi": "ぎ",
    "gu": "ぐ",
    "ge": "げ",
    "go": "ご",
    "kya": "きゃ",
    "kyu": "きゅ",
    "kyo": "きょ",
    "gya": "ぎゃ",
    "gyu": "ぎゅ",
    "gyo": "ぎょ",
    # S + Vowels
    "sa": "さ",
    "shi": "し",
    "su": "す",
    "se": "せ",
    "so": "そ",
    "za": "ざ",
    "ji": "じ",
    "zu": "ず",
    "ze": "ぜ",
    "zo": "ぞ",
    "sha": "しゃ",
    "shu": "しゅ",
    "sho": "しょ",
    "ja": "じゃ",
    "ju": "じゅ",
    "jo": "じょ",
    # T + Vowels
    "ta": "た",
    "chi": "ち",
    "tsu": "つ",
    "te": "て",
    "to": "と",
    "da": "だ",
    "ji": "ぢ",
    "zu": "づ",
    "de": "で",
    "do": "ど",
    "cha": "ちゃ",
    "chu": "ちゅ",
    "cho": "ちょ",
    # N + Vowels
    "na": "な",
    "ni": "に",
    "nu": "ぬ",
    "ne": "ね",
    "no": "の",
    "nya": "にゃ",
    "nyu": "にゅ",
    "nyo": "にょ",
    # H + Vowels
    "ha": "は",
    "hi": "ひ",
    "fu": "ふ",
    "he": "へ",
    "ho": "ほ",
    "ba": "ば",
    "bi": "び",
    "bu": "ぶ",
    "be": "べ",
    "bo": "ぼ",
    "pa": "ぱ",
    "pi": "ぴ",
    "pu": "ぷ",
    "pe": "ぺ",
    "po": "ぽ",
    "hya": "ひゃ",
    "hyu": "ひゅ",
    "hyo": "ひょ",
    # M + Vowels
    "ma": "ま",
    "mi": "み",
    "mu": "む",
    "me": "め",
    "mo": "も",
    "mya": "みゃ",
    "myu": "みゅ",
    "myo": "みょ",
    # Y + Vowels
    "ya": "や",
    "yu": "ゆ",
    "yo": "よ",
    # R + Vowels
    "ra": "ら",
    "ri": "り",
    "ru": "る",
    "re": "れ",
    "ro": "ろ",
    "rya": "りゃ",
    "ryu": "りゅ",
    "ryo": "りょ",
    # W + Vowels
    "wa": "わ",
    "wo": "を",
    "n": "ん",
    # Small tsu / gemination
    "っ": "っ",
    "xtsu": "っ",
    "-": "ー",
}

# Simple English → Hiragana
ENGLISH_VOWEL_MAP = {"a": "あ", "e": "え", "i": "い", "o": "お", "u": "う"}
ENGLISH_CONSONANT_MAP = {
    "b": "b",
    "k": "k",
    "g": "g",
    "d": "d",
    "t": "t",
    "p": "p",
    "m": "m",
    "n": "ん",
    "r": "r",
    "s": "s",
    "h": "h",
    "f": "f",
    "v": "v",
    "ch": "ち",
    "sh": "し",
    "j": "じ",
}


class Phonemizer:
    def __init__(self):
        self.mode = "japanese"

    def set_mode(self, mode):
        valid_modes = ["japanese", "hepburn", "wapuro", "english"]
        if mode in valid_modes:
            self.mode = mode

    def text_to_phonemes(self, text):
        text = re.sub(r"[^\w\s]", "", text.lower()).strip()
        if not text:
            return []

        # if input is already Japanese characters
        first_char = text[0] if text else ""
        is_japanese_chars = any(
            "\u3040" <= c <= "\u309f" or "\u30a0" <= c <= "\u30ff" for c in text
        )

        if self.mode == "english":
            return self._english_to_phonemes(text)
        elif self.mode == "japanese" and is_japanese_chars:
            # DIRECT HIRAGANA/KATAKANA → phonemes
            from hiro_ust_dev import HiroUSTGenerator

            generator = HiroUSTGenerator()
            return generator.hiragana_to_romaji(text)
        else:
            # Romaji modes (hepburn, wapuro, or japanese+romaji)
            return self._romaji_to_phonemes(text)

    def _romaji_to_phonemes(self, text):
        # Split by spaces OR process word-by-word
        words = text.split()
        hiragana_mora = []

        for word in words:
            i = 0
            while i < len(word):
                matched = False
                for length in [4, 3, 2, 1]:
                    if i + length <= len(word):
                        candidate = word[i : i + length]
                        if candidate in ROMAJI_MAP:
                            hiragana_mora.append(ROMAJI_MAP[candidate])
                            i += length
                            matched = True
                            break

                if not matched:
                    i += 1

        # Convert to phonemes
        from hiro_ust_dev import HiroUSTGenerator

        generator = HiroUSTGenerator()
        phonemes = []
        for mora in hiragana_mora:
            phonemes.extend(generator.hiragana_to_romaji(mora))
        return phonemes

    def _english_to_phonemes(self, text):
        """English → simple phonemes"""
        phonemes = []
        words = re.findall(r"\b\w+\b", text)
        for word in words:
            for char in word:
                if char in ENGLISH_VOWEL_MAP:
                    phonemes.append(ENGLISH_VOWEL_MAP[char])
                elif char in ENGLISH_CONSONANT_MAP:
                    phonemes.append(ENGLISH_CONSONANT_MAP[char])
                else:
                    phonemes.append(char)
        return phonemes
