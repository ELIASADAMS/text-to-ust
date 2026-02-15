# Hiro UST Generator - Architecture & Module Structure

## Version 0.2.0 - Refactored Modular Architecture

### Overview

The refactored version introduces a clean, modular architecture separating concerns:
- **Business Logic** → Reusable API (core.py)
- **Text Processing** → Dedicated converter package
- **Melody Generation** → Isolated melody package  
- **File Generation** → Dedicated generator package
- **Voice Management** → Dedicated voice package
- **User Interface** → Separated UI package

### Directory Structure

```
src/hiro_ust/
├── __init__.py                    # Package exports and documentation
├── core.py                        # ⭐ Main API (HiroUSTProcessor)
├── logger.py                      # 📝 Unified logging
├── config.py                      # ⚙️ Configuration constants
├── constants.py                   # 🔢 Global constants
│
├── converter/                     # 🔄 Text → Phoneme Conversion
│   ├── __init__.py               # HiroUSTGenerator, Phonemizer
│   └── mora_trie.py              # Mora trie building
│
├── generator/                     # 📝 Phoneme → UST/USTX
│   ├── __init__.py               # USTWriter (UST generation)
│   ├── note_generator.py         # Note-level logic (TODO)
│   └── ust_strings.py            # Format templates
│
├── melody/                        # 🎵 Melody Generation
│   ├── __init__.py               # MelodyBrain, SCALES
│   ├── melody_logic.py           # Melody engine
│   ├── scales.py                 # Scale definitions
│   ├── intone_utils.py           # Intonation settings
│   └── envelopes.py              # Pitch envelopes
│
├── voice/                         # 🎤 Voice & Presets
│   ├── __init__.py               # Voice management API
│   ├── key_roots.py              # Voice key mappings
│   ├── presets.py                # Voice presets
│   └── phonetic_utils.py         # Phonetic helpers (TODO)
│
├── data/                          # 📊 Data Tables
│   ├── __init__.py
│   ├── mora_trie_data.py         # Mora database (1000+ entries)
│   └── parts_presets.json        # Part templates
│
├── ui/                            # 🖥️ User Interface
│   ├── __init__.py               # Main app + GUI launcher
│   ├── app.py                    # USTGeneratorApp (TODO: extract)
│   ├── dialogs.py                # File dialogs (TODO)
│   └── widgets.py                # Reusable widgets (TODO)
│
└── compat modules (for now):      # Will be deprecated/moved
    ├── hiragana_map.py
    ├── kana_to_hiragana.py
    ├── ustx_writer.py
    └── others...
```

## Module Responsibilities

### 📌 core.py
**Purpose**: Public API for programmatic use

```python
class HiroUSTProcessor:
    def process_lyrics(lyrics, project_name, format) -> str
    def get_supported_scales() -> list
    def get_supported_envelopes() -> list

@dataclass
class GeneratorConfig:
    tempo, base_length, root_key, scale, intone_level, ...
```

**Use Case**: Library users, CLI tools, external integrations

### 🔄 converter/
**Purpose**: Text/phoneme conversion

```python
class HiroUSTGenerator:
    def hiragana_to_romaji(text) -> List[str]
    def romaji_to_hiragana(phoneme) -> str

class Phonemizer:
    def text_to_phonemes(text) -> List[str]
    def set_mode(mode)  # japanese, hepburn, wapuro, english
```

**Use Case**: Lyric processing, phoneme extraction

### 📝 generator/
**Purpose**: UST/USTX file generation

```python
class USTWriter:
    def add_note(length, lyric, note_num, ...)
    def add_rest(length)
    def finalize() -> str
```

**Use Case**: Converting note sequences to file format

### 🎵 melody/
**Purpose**: Intelligent melody generation

```python
class MelodyBrain:
    def get_smart_note(root_key, scale, phoneme, ...) -> float
    def set_accent_pattern(pattern, word_length)
    def get_intensity(note, progress) -> int

SCALES = {"Major Pentatonic": [...], "Minor": [...], ...}
```

**Use Case**: Melody generation with voice leading, accents

### 🎤 voice/
**Purpose**: Voice-specific settings and presets

```python
KEY_ROOTS = {"Soprano": 84, "Alto": 72, "Tenor": 60, ...}
ENVELOPE_PRESETS = {"Pop": "...", "Opera": "...", ...}

def get_voice_roots() -> dict
def get_envelope_presets() -> dict
```

**Use Case**: Voice management, envelope selection

### 📝 logger.py
**Purpose**: Unified logging

```python
logger = get_logger(__name__)
logger.info/debug/warning/error(...)
```

**Use Case**: Debugging, error reporting

### 🖥️ ui/
**Purpose**: Tkinter GUI application

```python
class USTGeneratorApp:
    def __init__(root)
    def generate_ust()
    def save_ust()
    def preview_phonemes()

def main():
    # Launch GUI
```

**Use Case**: Interactive use, real-time preview

## Data Flow

```
User Input (Lyrics)
        ↓
[converter] Phonemization
        ↓
[melody] Melody Generation
        ↓
[generator] UST Generation
        ↓
Output (UST/USTX File)
```

## API Usage Examples

### Example 1: Programmatic Generation
```python
from hiro_ust.core import HiroUSTProcessor, GeneratorConfig

config = GeneratorConfig(
    tempo=120,
    scale="Major Pentatonic",
    use_motifs=True
)
processor = HiroUSTProcessor(config)
ust = processor.process_lyrics("きゃっきゃ", "MyProject")
```

### Example 2: Using Converter
```python
from hiro_ust.converter import HiroUSTGenerator, Phonemizer

gen = HiroUSTGenerator()
phonemes = gen.hiragana_to_romaji("きゃっきゃ")  # ['kya', 'っ', 'ki']

phonemizer = Phonemizer()
phonemizer.set_mode("japanese")
```

### Example 3: Melody Generation
```python
from hiro_ust.melody import MelodyBrain, SCALES

brain = MelodyBrain(seed=42)
note = brain.get_smart_note(
    root_key=72,
    scale="Major Pentatonic",
    phoneme="a"
)
```

### Example 4: UST Generation
```python
from hiro_ust.generator import USTWriter

writer = USTWriter("MyProject", tempo=120)
writer.add_note(length=240, lyric="あ", note_num=72, ...)
writer.add_rest(240)
ust_content = writer.finalize()
```

### Example 5: GUI Usage
```python
from hiro_ust.ui import main

main()  # Launches Tkinter GUI
```

## Testing Strategy

Each module can be tested independently:

```python
# Test converter
from hiro_ust.converter import HiroUSTGenerator
gen = HiroUSTGenerator()
assert gen.hiragana_to_romaji("あ") == ["a"]

# Test melody
from hiro_ust.melody import SCALES
assert "Major Pentatonic" in SCALES

# Test generator
from hiro_ust.generator import USTWriter
writer = USTWriter("Test", 120)
writer.add_note(240, "a", 60, ...)
output = writer.finalize()
assert "[#0000]" in output  # UST format check
```

## Migration Path

### Phase 1: ✅ Complete
- Modular structure created
- core.py API defined
- logger.py unified logging
- Subpackages created

### Phase 2: In Progress
- Extract GUI from hiro_ust_dev.py → ui/app.py
- Create note_generator.py
- Create dialogs.py, widgets.py

### Phase 3: TODO
- Full hiro_ust_dev.py → ui/app.py migration
- Remove legacy code
- Add 100+ unit tests
- Performance optimization

### Phase 4: TODO
- Create CLI interface
- Add USTX support enhancement
- Documentation generation

## Compatibility Notes

### Backward Compatibility
- Old `hiro_ust_dev.py` still available (deprecated)
- All old imports still work via re-export
- No breaking changes in v0.2.0

### Forward Compatibility
- New code should import from subpackages:
  ```python
  # ✅ New way (recommended)
  from hiro_ust.core import HiroUSTProcessor
  from hiro_ust.converter import HiroUSTGenerator
  from hiro_ust.melody import MelodyBrain
  
  # ✅ Still works (backward compat)
  from hiro_ust import HiroUSTProcessor
  ```

## Performance Considerations

- **Singleton Pattern**: HiroUSTGenerator uses singleton for efficiency
- **Trie Structure**: Mora trie pre-built at import time
- **Lazy Imports**: UI imports deferred until needed
- **Logging Overhead**: Minimal (only in dev/debug mode)

## Dependencies

- **tkinter**: GUI (stdlib)
- **pyyaml**: USTX format (optional)
- **Standard library**: No external required for core API

## Future Enhancements

1. **Async Processing**: Non-blocking melody generation
2. **Plugin System**: Custom melody engines, scales
3. **Web API**: FastAPI/Flask wrapper for core.py
4. **CLI Tool**: Command-line interface
5. **Cython Optimization**: Performance-critical paths

