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
        "FileDialog": ("ui", "FileDialog"),
        "SaveDialog": ("ui", "SaveDialog"),
        "DialogMessages": ("ui", "DialogMessages"),
        "LabeledEntry": ("ui", "LabeledEntry"),
        "LabeledSpinbox": ("ui", "LabeledSpinbox"),
        "LabeledCombobox": ("ui", "LabeledCombobox"),
        "LabeledScale": ("ui", "LabeledScale"),
        "CheckbuttonGroup": ("ui", "CheckbuttonGroup"),
        "ParameterPanel": ("ui", "ParameterPanel"),
        "ProgressBar": ("ui", "ProgressBar"),
        "PresetManager": ("ui", "PresetManager"),
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
    # Core API
    "HiroUSTProcessor",
    "GeneratorConfig",
    # Logging
    "get_logger",
    "logger",
    # Converter
    "HiroUSTGenerator",
    "Phonemizer",
    # Generator
    "USTWriter",
    "NoteGenerator",
    "PitchBendCalculator",
    "EnvelopeCalculator",
    # Melody
    "MelodyBrain",
    "SCALES",
    # Voice & Phonetics
    "KEY_ROOTS",
    "ENVELOPE_PRESETS",
    "MoraAnalyzer",
    "AccentAnalyzer",
    "VowelHarmony",
    "PhoneticNormalizer",
    # UI Components
    "FileDialog",
    "SaveDialog",
    "DialogMessages",
    "LabeledEntry",
    "LabeledSpinbox",
    "LabeledCombobox",
    "LabeledScale",
    "CheckbuttonGroup",
    "ParameterPanel",
    "ProgressBar",
    "PresetManager",
    "USTGeneratorApp",
    "run_gui",
]
