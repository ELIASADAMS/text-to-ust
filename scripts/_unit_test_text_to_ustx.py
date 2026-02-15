import sys

sys.path.insert(0, "src")
from hiro_ust.hiro_ust_dev import text_to_ustx
from hiro_ust.melody.melody_logic import MelodyBrain

melody = MelodyBrain(seed=42)
elements = ["ka", "PAUSE_LINE:480", "a"]
ustx = text_to_ustx(
    elements,
    project_name="UnitTest",
    tempo=120,
    base_length=240,
    root_key=60,
    scale="Major Pentatonic",
    intone_level="Medium (2)",
    length_var=0.3,
    stretch_prob=0.2,
    melody_brain=melody,
    pre_utterance=25,
    voice_overlap=10,
    intensity_base=80,
    envelope="0,10,35,0,100,100,0",
    flat_mode=False,
    quartertone_mode=False,
    lyrical_mode=True,
    use_motifs=True,
    chord_mode=False,
    contour_bias=0,
    pitch_range=70,
    accent="None",
)
print("USTX length:", len(ustx) if ustx else 0)
print(ustx[:800])
