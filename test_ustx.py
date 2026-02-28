#!/usr/bin/env python
"""Quick test script for USTX generation"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hiro_ust.hiro_ust_dev import (
    text_to_ustx,
    parse_song_structure,
    HiroUSTGenerator,
)
from hiro_ust.melody.melody_logic import MelodyBrain
from hiro_ust.phonemizer import Phonemizer
from hiro_ust.voice.key_roots import KEY_ROOTS

# Test lyrics
lyrics = """[Verse]
きゃっきゃ うれし いたい

[Chorus]
いたみ いたみ きもちいい
"""

print("=== Testing USTX Generation ===")
print(f"Lyrics:\n{lyrics}\n")

# Create phonemizer
phonemizer = Phonemizer()
phonemizer.set_mode("japanese")

# Parse song structure
parts, elements = parse_song_structure(lyrics, phonemizer=phonemizer)
print(f"Parsed elements ({len(elements)} total):")
for i, elem in enumerate(elements[:20]):
    print(f"  {i}: {elem}")
print("  ...")

# Create melody brain
melodybrain = MelodyBrain(seed=1234)

# Generate USTX
ust_content = text_to_ustx(
    text_elements=elements,
    project_name="Test_USTX",
    tempo=120,
    base_length=480,
    root_key=KEY_ROOTS["Alto"],
    scale="Minor",
    intone_level="Tight (1)",
    length_var=0.3,
    stretch_prob=0.25,
    melody_brain=melodybrain,
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

print(f"\n=== Generated USTX ({len(ust_content)} chars) ===")
# Show first 500 chars
print(ust_content[:500])
print("\n... [content truncated] ...")

# Save to file
output_path = os.path.join(os.path.dirname(__file__), "test_output.ustx")
with open(output_path, "w", encoding="utf-8-sig") as f:
    f.write(ust_content)
print(f"\nSaved to: {output_path}")


