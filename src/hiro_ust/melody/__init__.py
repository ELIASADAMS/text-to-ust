"""
Melody generation and musical logic module.

Provides intelligent melody generation with support for:
- Multiple musical scales
- Voice leading and motion control
- Motif memory and repetition
- Chord progressions
- Accent patterns (Japanese pitch accent)
- Intonation levels

Components:
  - MelodyBrain: Main melody generation engine
  - Scales: Musical scale definitions
  - Intone settings: Intonation parameters
  - Envelopes: Pitch envelope presets
"""

from .melody_logic import MelodyBrain
from .scales import SCALES
from .intone_utils import get_intone_settings
from .envelopes import ENVELOPE_PRESETS
from ..logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "MelodyBrain",
    "SCALES",
    "get_intone_settings",
    "ENVELOPE_PRESETS",
]

