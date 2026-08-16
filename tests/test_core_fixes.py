from hiro_ust.config import GeneratorConfig
from hiro_ust.converter.phonemizer import Phonemizer
from hiro_ust.generator import USTWriter
from hiro_ust.generator.ustx_writer import USTXWriter
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


def test_ustx_writer_restores_tuning_expression():
    writer = USTXWriter("test", 120)
    writer.add_note(
        length=720,
        lyric="a",
        note_num=60,
        pre_utter=25,
        voice_overlap=10,
        intensity=90,
        envelope="Pop",
        pbs="0;-35",
    )
    assert len(writer.notes) == 1
    note = writer.notes[0]
    assert note["pitch"]["data"]
    assert note["pitch"]["data"][-1]["y"] == 0
    assert "vibrato" in note
    assert note["vibrato"]["length"] >= 0


def test_melody_seed_is_reproducible():
    kwargs = dict(root_midi=60, scale_name="Major Pentatonic", phoneme="a")
    a = MelodyBrain(seed=42).get_smart_note(**kwargs)
    b = MelodyBrain(seed=42).get_smart_note(**kwargs)
    assert a == b
