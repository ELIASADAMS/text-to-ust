from hiro_ust.converter import HiroUSTGenerator, Phonemizer


def test_japanese_phonemizer_after_package_cleanup():
    phonemizer = Phonemizer()
    phonemes = phonemizer.text_to_phonemes("これわけいこくです")
    assert phonemes
    assert "ko" in phonemes
    assert "re" in phonemes
    assert "ke" in phonemes
    assert "ko" in phonemes


def test_romaji_to_hiragana_preview_mapping():
    generator = HiroUSTGenerator()
    assert generator.romaji_to_hiragana("kore") == "kore"
    assert generator.romaji_to_hiragana("ko") == "こ"
