from hiro_ust.config import GeneratorConfig
from hiro_ust.converter.phonemizer import Phonemizer
from hiro_ust.generator import USTWriter
from hiro_ust.melody.intone_utils import get_intone_settings
from hiro_ust.melody.melody_logic import MelodyBrain


def test_generator_config_aliases():
    config = GeneratorConfig(intone_level="Tight (1)")
    assert config.intone == "Tight (1)"
    assert config.effective_root_key == 60


def test_phonemizer_preserves_phrase_punctuation():
    phonemes = Phonemizer().text_to_phonemes("こんにちは。")
    assert phonemes[-1] == "。"


def test_ust_writer_preserves_fractional_pitch_intent():
    writer = USTWriter("test", 120)
    writer.add_note(240, "a", 60.5, 0, 0, 80, "0,10,35,0,100,100,0")
    text = writer.finalize()
    assert "NoteNum=60" in text
    assert "PBY=25" in text


def test_melody_seed_is_reproducible():
    kwargs = dict(root_midi=60, scale_name="Major Pentatonic", phoneme="a")
    a = MelodyBrain(seed=42).get_smart_note(**kwargs)
    b = MelodyBrain(seed=42).get_smart_note(**kwargs)
    assert a == b


def test_intone_presets_have_materially_different_motion_limits():
    tight = get_intone_settings("Tight (1)")
    wide = get_intone_settings("Wide (3)")
    wild = get_intone_settings("Wild (5)")
    assert tight["leap"] < wide["leap"] < wild["leap"]
    assert tight["temperature"] < wide["temperature"] < wild["temperature"]


def test_voice_registers_are_distinct():
    lyrics = ["a", "e", "i", "o", "u"]

    def generate(root):
        brain = MelodyBrain(seed=123)
        return [
            brain.get_smart_note(
                root,
                "Major Pentatonic",
                phoneme,
                "Medium (2)",
                pitch_range=70,
            )
            for phoneme in lyrics
        ]

    alto = generate(60)
    baritone = generate(52)
    assert alto != baritone
    assert min(alto) > min(baritone)


def test_tight_intone_prevents_large_successive_leaps():
    brain = MelodyBrain(seed=999)
    notes = [
        brain.get_smart_note(
            60,
            "Major Pentatonic",
            phoneme,
            "Tight (1)",
            pitch_range=70,
        )
        for phoneme in "aeiouaeiou"
    ]
    relative = [round(note - 60) for note in notes]
    assert all(abs(b - a) <= 2 for a, b in zip(relative, relative[1:]))
