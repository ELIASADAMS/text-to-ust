"""Public package API for Hiro UST."""

__version__ = "0.3.0"
__author__ = "Ilya Minin (Eli)"


def __getattr__(name: str):
    """Lazy-load public objects to keep package imports lightweight."""
    imports_map = {
        "HiroUSTProcessor": ("core", "HiroUSTProcessor"),
        "GeneratorConfig": ("config", "GeneratorConfig"),
        "HiroConfig": ("config", "HiroConfig"),
        "get_logger": ("logger", "get_logger"),
        "logger": ("logger", "logger"),
        "HiroUSTGenerator": ("converter", "HiroUSTGenerator"),
        "Phonemizer": ("converter", "Phonemizer"),
        "USTWriter": ("generator", "USTWriter"),
        "NoteGenerator": ("generator", "NoteGenerator"),
        "PitchBendCalculator": ("generator", "PitchBendCalculator"),
        "EnvelopeCalculator": ("generator", "EnvelopeCalculator"),
        "MelodyBrain": ("melody", "MelodyBrain"),
        "SCALES": ("melody", "SCALES"),
        "KEY_ROOTS": ("voice", "KEY_ROOTS"),
        "ENVELOPE_PRESETS": ("voice", "ENVELOPE_PRESETS"),
        "MoraAnalyzer": ("voice", "MoraAnalyzer"),
        "AccentAnalyzer": ("voice", "AccentAnalyzer"),
        "VowelHarmony": ("voice", "VowelHarmony"),
        "PhoneticNormalizer": ("voice", "PhoneticNormalizer"),
        "USTGeneratorApp": ("cli", "USTGeneratorApp"),
        "run_gui": ("cli", "main"),
    }
    if name not in imports_map:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = imports_map[name]
    module = __import__(f"hiro_ust.{module_name}", fromlist=[attr_name])
    attr = getattr(module, attr_name)
    globals()[name] = attr
    return attr


__all__ = [
    "__version__",
    "__author__",
    "HiroUSTProcessor",
    "GeneratorConfig",
    "HiroConfig",
    "get_logger",
    "logger",
    "HiroUSTGenerator",
    "Phonemizer",
    "USTWriter",
    "NoteGenerator",
    "PitchBendCalculator",
    "EnvelopeCalculator",
    "MelodyBrain",
    "SCALES",
    "KEY_ROOTS",
    "ENVELOPE_PRESETS",
    "MoraAnalyzer",
    "AccentAnalyzer",
    "VowelHarmony",
    "PhoneticNormalizer",
    "USTGeneratorApp",
    "run_gui",
]
