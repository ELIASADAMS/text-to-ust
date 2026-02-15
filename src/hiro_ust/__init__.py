"""
Hiro UST Generator - Intelligent UST file generator for Japanese singing synthesis.

This package provides tools for converting Japanese lyrics to UST/USTX files
used in UTAU and OpenUtau for voice synthesis.

## Quick Start

### Programmatic Use (API)
```python
from hiro_ust.core import HiroUSTProcessor, GeneratorConfig

config = GeneratorConfig(tempo=120, scale="Major Pentatonic")
processor = HiroUSTProcessor(config)
ust_content = processor.process_lyrics("きゃっきゃ", project_name="MyProject")

with open("output.ust", "w", encoding="utf-8-sig") as f:
    f.write(ust_content)
```

### GUI Application
```bash
python scripts/hiro_ust_dev.py
```

## Modules

- **core**: Main API (HiroUSTProcessor)
- **converter**: Text/phoneme conversion
- **generator**: UST/USTX file generation
- **melody**: Melody generation engine
- **voice**: Voice and preset management
- **data**: Data tables and configurations
- **ui**: Tkinter GUI application
- **logger**: Unified logging

## Configuration

Configure via `src/hiro_ust/config.py` or programmatically:

```python
from hiro_ust.core import GeneratorConfig
config = GeneratorConfig(
    tempo=120,
    scale="Major Pentatonic",
    intone_level="Medium (2)",
    use_motifs=True
)
```
"""

__version__ = "0.2.0"
__author__ = "Hiro UST Project"

# Core API
from .core import HiroUSTProcessor, GeneratorConfig
from .logger import get_logger, logger

# Converter module
from .converter import HiroUSTGenerator, Phonemizer

# Generator module
from .generator import USTWriter

# Melody module
from .melody import MelodyBrain, SCALES

# Voice module
from .voice import KEY_ROOTS, ENVELOPE_PRESETS

# UI
from .ui import USTGeneratorApp, main as run_gui

__all__ = [
    # Version
    "__version__",

    # Core API
    "HiroUSTProcessor",
    "GeneratorConfig",

    # Logging
    "get_logger",
    "logger",

    # Converters
    "HiroUSTGenerator",
    "Phonemizer",

    # Generators
    "USTWriter",

    # Melody
    "MelodyBrain",
    "SCALES",

    # Voice
    "KEY_ROOTS",
    "ENVELOPE_PRESETS",

    # GUI
    "USTGeneratorApp",
    "run_gui",
]

