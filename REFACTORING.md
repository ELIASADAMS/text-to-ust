# Hiro UST Generator - Refactored Structure Guide

## Overview

Hiro UST Generator is a Python application for creating UST (Uta Synthesizer Tool) and USTX (OpenUtau) files from Japanese lyrics using intelligent melody generation.

## Project Structure (refactor/restructure-src branch)

```
text-to-ust/
├── src/
│   └── hiro_ust/              # Main package
│       ├── __init__.py
│       ├── config.py          # Configuration constants
│       ├── constants.py       # Global constants
│       ├── hiro_ust_dev.py    # Core module with GUI (1200+ lines)
│       ├── hiro_ust_dev.py    # Main implementation
│       ├── melody_logic.py    # Melody generation engine
│       ├── phonemizer.py      # Text-to-phoneme conversion
│       ├── hiragana_map.py    # Romaji to hiragana mappings
│       ├── kana_to_hiragana.py # Katakana conversion utilities
│       ├── mora_trie_data.py  # Mora database
│       ├── ust_strings.py     # UST format templates
│       ├── ustx_writer.py     # USTX format writer
│       ├── presets.py         # Preset management
│       ├── scales.py          # Musical scales
│       ├── key_roots.py       # Voice key mappings
│       ├── envelopes.py       # Envelope presets
│       ├── intone_utils.py    # Intonation settings
│       ├── kana_to_hiragana.py # Katakana->Hiragana
│       └── data/
│           └── parts_presets.json
├── scripts/
│   └── hiro_ust_dev.py        # Launcher script for GUI
├── hiro_ust/                  # Package shim for IDE compatibility
│   └── __init__.py
├── test_imports.py            # Basic import test
├── test_core.py               # Comprehensive functionality tests
├── pyproject.toml             # Python project metadata (src layout)
├── requirements.txt
└── run.ps1                     # PowerShell launcher script

```

## Key Improvements (Refactoring)

### 1. **Module Organization**
   - Moved all source code to `src/hiro_ust/` (src-layout PEP 517 compatible)
   - Separated entry point scripts to `scripts/`
   - Added `hiro_ust/__init__.py` shim for IDE compatibility

### 2. **Import System**
   - Updated all imports to use relative imports within package (e.g., `from .config import HiroConfig`)
   - Scripts add `src` to `sys.path` for runtime compatibility
   - Module can run directly or as package: `python src/hiro_ust/hiro_ust_dev.py` or `python -m hiro_ust.hiro_ust_dev`

### 3. **ROMAJI Map Standardization**
   - Fixed duplicate keys in ROMAJI_MAP
   - Standardized ji/zu mappings:
     - `ji_s` → じ (sibilant, modern standard)
     - `ji_t` → ぢ (affricate, rare/traditional)
     - `zu` → ず (standard)
     - `zu_t` → づ (rare/traditional)

### 4. **Code Documentation**
   - Added comprehensive docstrings to core classes:
     - `HiroUSTGenerator`: Hiragana↔romaji conversion
     - `USTWriter`: UST format generation
     - Helper functions: `create_stretch_notes`, `parse_song_structure`, etc.
   - Type hints for better IDE support

### 5. **Removed Duplication**
   - Deleted `scripts/hiro_ust_v4.2.py` (was backup of dev version)
   - Consolidated functionality into single main module

## How to Run

### Option 1: Launcher Script (Recommended)
```powershell
python .\scripts\hiro_ust_dev.py
```

### Option 2: Direct Module Execution
```powershell
python src\hiro_ust\hiro_ust_dev.py
```

### Option 3: Package Module (requires PYTHONPATH or pip install)
```powershell
$env:PYTHONPATH = "src"
python -m hiro_ust.hiro_ust_dev
```

## Testing

### Quick Import Test
```powershell
python test_imports.py
```

### Comprehensive Functionality Test
```powershell
python test_core.py
```

This verifies:
- Core module imports (HiroUSTGenerator, Phonemizer, MelodyBrain)
- Basic functionality (hiragana→romaji conversion)
- ROMAJI_MAP consistency (no duplicate keys)
- ji/zu mappings are correct

## Core Classes

### HiroUSTGenerator
Singleton for efficient hiragana/katakana to romaji conversion using mora-based trie matching.

```python
gen = HiroUSTGenerator()
phonemes = gen.hiragana_to_romaji("きゃっきゃ")  # → ['kya', 'っ', 'ki']
hiragana = gen.romaji_to_hiragana("kya")         # → 'きゃ'
```

### Phonemizer
Multi-mode phoneme conversion (Japanese, Hepburn, Wapuro, English).

```python
phonemizer = Phonemizer()
phonemizer.set_mode("japanese")
phonemes = phonemizer.text_to_phonemes("きゃっきゃ")
```

### MelodyBrain
Intelligent melody generation with motif memory, voice leading, and chord progressions.

### USTWriter
Generates UST format files with notes, rests, and timing information.

```python
writer = USTWriter("MyProject", tempo=120)
writer.add_note(length=240, lyric="あ", note_num=60, ...)
ust_content = writer.finalize()
```

## Git History

The refactoring is tracked in branch `refactor/restructure-src`:
```
7ebc88d - refactor: improve ROMAJI_MAP, add comprehensive docstrings
90fecd3 - chore: add pyproject.toml, launcher script
2c9beb6 - refactor: move modules into src/hiro_ust, add scripts launcher
```

## Dependencies

See `requirements.txt` for Python dependencies. Core packages:
- tkinter (GUI)
- pyyaml (USTX format)

## Notes for Future Development

1. **GUI Refactoring**: Consider extracting `USTGeneratorApp` to separate module (`gui.py`)
2. **API Layer**: Expose core functionality via clean API for CLI/web use
3. **Type Hints**: Gradually add type hints for better IDE support
4. **Testing**: Expand test coverage with pytest
5. **Documentation**: Generate API docs from docstrings

## Troubleshooting

### ImportError: attempted relative import with no known parent package
- Use launcher script: `python .\scripts\hiro_ust_dev.py`
- Or set PYTHONPATH: `$env:PYTHONPATH = "src"`

### Missing modules
- Ensure `src/` directory exists and contains `hiro_ust/` package
- Run `python test_imports.py` to verify setup

### IDE warnings about duplicate keys
- ROMAJI_MAP is now fixed; cache may need refresh
- Rebuild IDE indexes if needed

---

**Branch**: `refactor/restructure-src`  
**Last Updated**: 2025-02-15  
**Status**: ✓ Refactoring complete, all tests passing

