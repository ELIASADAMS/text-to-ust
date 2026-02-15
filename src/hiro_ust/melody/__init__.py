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

from hiro_ust.melody_logic import MelodyBrain
from hiro_ust.scales import SCALES
from hiro_ust.intone_utils import get_intone_settings
from hiro_ust.envelopes import ENVELOPE_PRESETS
from hiro_ust.logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "MelodyBrain",
    "SCALES",
    "get_intone_settings",
    "ENVELOPE_PRESETS",
]

