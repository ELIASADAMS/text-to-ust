"""
Voice and prosody module.

Manages voice-specific settings, presets, and phonetic parameters.

Components:
  - Key roots: Voice key mappings
  - Presets: Voice and parameter presets
  - Phonetic utilities: Voice-specific phonetic processing
"""

from .key_roots import KEY_ROOTS
from .presets import (
    build_preset_from_app,
    apply_preset_to_app,
    save_preset_to_file,
    load_preset_from_file,
)
from .phonetic_utils import (
    MoraAnalyzer,
    AccentAnalyzer,
    VowelHarmony,
    PhoneticNormalizer,
)
from ..melody.envelopes import ENVELOPE_PRESETS
from ..logger import get_logger

logger = get_logger(__name__)


def get_envelope_presets():
    """Get all available envelope presets.

    Returns:
        dict: Envelope presets mapped by name
    """
    return ENVELOPE_PRESETS


def get_voice_roots():
    """Get all available voice root keys.

    Returns:
        dict: Voice names mapped to MIDI note numbers
    """
    return KEY_ROOTS


__all__ = [
    "KEY_ROOTS",
    "ENVELOPE_PRESETS",
    "MoraAnalyzer",
    "AccentAnalyzer",
    "VowelHarmony",
    "PhoneticNormalizer",
    "build_preset_from_app",
    "apply_preset_to_app",
    "save_preset_to_file",
    "load_preset_from_file",
    "get_envelope_presets",
    "get_voice_roots",
]
