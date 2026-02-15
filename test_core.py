#!/usr/bin/env python
"""
Quick test to verify core module imports and basic functionality.
Run this to ensure the refactored package structure is working.
"""

import sys
import os

# Test 1: Import core classes
print("=" * 50)
print("TEST 1: Core Module Imports")
print("=" * 50)

sys.path.insert(0, os.path.abspath("src"))

try:
    from hiro_ust.hiro_ust_dev import HiroUSTGenerator

    print("✓ HiroUSTGenerator imported successfully")
except ImportError as e:
    print(f"✗ Failed to import HiroUSTGenerator: {e}")
    sys.exit(1)

try:
    from hiro_ust.phonemizer import Phonemizer

    print("✓ Phonemizer imported successfully")
except ImportError as e:
    print(f"✗ Failed to import Phonemizer: {e}")
    sys.exit(1)

try:
    from hiro_ust.melody_logic import MelodyBrain

    print("✓ MelodyBrain imported successfully")
except ImportError as e:
    print(f"✗ Failed to import MelodyBrain: {e}")
    sys.exit(1)

# Test 2: Basic functionality
print("\n" + "=" * 50)
print("TEST 2: Basic Functionality")
print("=" * 50)

try:
    gen = HiroUSTGenerator()
    result = gen.hiragana_to_romaji("きゃっきゃ")
    print(f"✓ HiroUSTGenerator.hiragana_to_romaji() works")
    print(f"  'きゃっきゃ' -> {result}")
except Exception as e:
    print(f"✗ HiroUSTGenerator test failed: {e}")
    sys.exit(1)

try:
    phonemizer = Phonemizer()
    phonemizer.set_mode("japanese")
    print("✓ Phonemizer initialized successfully")
except Exception as e:
    print(f"✗ Phonemizer test failed: {e}")
    sys.exit(1)

# Test 3: ROMAJI_MAP consistency
print("\n" + "=" * 50)
print("TEST 3: ROMAJI_MAP Consistency Check")
print("=" * 50)

from hiro_ust.phonemizer import ROMAJI_MAP

keys = list(ROMAJI_MAP.keys())
unique_keys = set(keys)

if len(keys) == len(unique_keys):
    print(f"✓ No duplicate keys in ROMAJI_MAP ({len(keys)} unique keys)")
else:
    duplicates = [k for k in unique_keys if keys.count(k) > 1]
    print(f"✗ Found duplicate keys: {duplicates}")
    sys.exit(1)

# Verify key mappings
expected_ji = {
    "ji_s": "じ",  # sibilant (modern standard)
    "ji_t": "ぢ",  # affricate (rare, traditional)
}

expected_zu = {
    "zu": "ず",  # sibilant (modern standard)
    "zu_t": "づ",  # affricate (rare, traditional)
}

for key, hiragana in expected_ji.items():
    if ROMAJI_MAP.get(key) == hiragana:
        print(f"✓ {key} -> {hiragana}")
    else:
        print(
            f"✗ {key} mapping incorrect: expected {hiragana}, got {ROMAJI_MAP.get(key)}"
        )
        sys.exit(1)

for key, hiragana in expected_zu.items():
    if ROMAJI_MAP.get(key) == hiragana:
        print(f"✓ {key} -> {hiragana}")
    else:
        print(
            f"✗ {key} mapping incorrect: expected {hiragana}, got {ROMAJI_MAP.get(key)}"
        )
        sys.exit(1)

print("\n" + "=" * 50)
print("ALL TESTS PASSED ✓")
print("=" * 50)
