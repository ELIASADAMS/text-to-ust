#!/usr/bin/env python
"""Quick test of refactored module structure."""

import sys
import os

sys.path.insert(0, os.path.abspath("src"))

print("=" * 60)
print("REFACTORED MODULE STRUCTURE TEST")
print("=" * 60)

# Test 1: Logger
try:
    from hiro_ust.logger import get_logger

    logger = get_logger("test")
    print("✓ Logger imported successfully")
except Exception as e:
    print(f"✗ Logger import failed: {e}")
    sys.exit(1)

# Test 2: Converter
try:
    from hiro_ust.converter import HiroUSTGenerator

    gen = HiroUSTGenerator()
    result = gen.hiragana_to_romaji("あ")
    print(f"✓ HiroUSTGenerator works: あ -> {result}")
except Exception as e:
    print(f"✗ Converter failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 3: Core API
try:
    from hiro_ust.core import HiroUSTProcessor, GeneratorConfig

    config = GeneratorConfig(tempo=120)
    processor = HiroUSTProcessor(config)
    print(f"✓ HiroUSTProcessor created with tempo={processor.config.tempo}")
except Exception as e:
    print(f"✗ Core API failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 4: Melody
try:
    from hiro_ust.melody import SCALES

    scales_list = list(SCALES.keys())[:3]
    print(f"✓ Melody module loaded: {scales_list}")
except Exception as e:
    print(f"✗ Melody failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 5: Voice
try:
    from hiro_ust.voice import KEY_ROOTS

    voices = list(KEY_ROOTS.keys())[:3]
    print(f"✓ Voice module loaded: {voices}")
except Exception as e:
    print(f"✗ Voice failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 6: Generator
try:
    from hiro_ust.generator import USTWriter

    writer = USTWriter("Test", 120)
    print(f"✓ USTWriter initialized")
except Exception as e:
    print(f"✗ Generator failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
print("\nRefactored modular structure is working correctly!")
print("New packages:")
print("  - converter/   : Text/phoneme conversion")
print("  - generator/   : UST file generation")
print("  - melody/      : Melody generation")
print("  - voice/       : Voice management")
print("  - ui/          : GUI components")
print("  - core.py      : Public API")
print("  - logger.py    : Logging system")
