"""
Hiro UST Generator - Intelligent UST file generator for Japanese singing synthesis.

This package provides tools for converting Japanese lyrics to UST/USTX files
used in UTAU and OpenUtau for voice synthesis.

## Quick Start

### Programmatic Use (API)
```python
from .core import HiroUSTProcessor, GeneratorConfig

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
from .core import GeneratorConfig
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


# Lazy imports to avoid circular dependencies
def __getattr__(name: str):
    """Lazy import attributes to avoid circular imports."""
    imports_map = {
        "HiroUSTProcessor": ("core", "HiroUSTProcessor"),
        "GeneratorConfig": ("core", "GeneratorConfig"),
        "get_logger": ("logger", "get_logger"),
        "logger": ("logger", "logger"),
        "HiroUSTGenerator": ("converter", "HiroUSTGenerator"),
        "Phonemizer": ("converter", "Phonemizer"),
        "USTWriter": ("generator", "USTWriter"),
        "MelodyBrain": ("melody", "MelodyBrain"),
        "SCALES": ("melody", "SCALES"),
        "KEY_ROOTS": ("voice", "KEY_ROOTS"),
        "ENVELOPE_PRESETS": ("voice", "ENVELOPE_PRESETS"),
        "USTGeneratorApp": ("ui", "USTGeneratorApp"),
        "run_gui": ("ui", "main"),
    }

    if name in imports_map:
        module_name, attr_name = imports_map[name]
        module = __import__(f"hiro_ust.{module_name}", fromlist=[attr_name])
        attr = getattr(module, attr_name)
        globals()[name] = attr
        return attr

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "__version__",
    "HiroUSTProcessor",
    "GeneratorConfig",
    "get_logger",
    "logger",
    "HiroUSTGenerator",
    "Phonemizer",
    "USTWriter",
    "MelodyBrain",
    "SCALES",
    "KEY_ROOTS",
    "ENVELOPE_PRESETS",
    "USTGeneratorApp",
    "run_gui",
]
