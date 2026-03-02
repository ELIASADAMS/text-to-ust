"""
Note-level generation logic for UST/USTX files.

This module handles individual note creation, including:
- Note length calculation with variation
- Note pitch selection with intelligence
- Accent pattern application
- Envelope and pitch bend generation

Separates note-level concerns from high-level text processing.
"""

import random
from typing import List, Tuple, Optional

from ..config import HiroConfig
from ..constants import VOWEL_CHARS, CONSONANT_CHARS
from ..melody.scales import SCALES
from ..melody.intone_utils import get_intone_settings


class NoteGenerator:
    """Generator for individual note parameters.

    Handles note length calculation, pitch selection, and effect parameters
    without dependencies on UI or file writing.

    Example:
        >>> gen = NoteGenerator(base_length=240, length_var=0.3)
        >>> length = gen.get_note_length("a", length_factor=1.0)
        >>> pitch = gen.get_random_pitch(root_key=60, scale_name="Major Pentatonic")
    """

    def __init__(self, base_length: int = 240, length_var: float = 0.3):
        """Initialize note generator.

        Args:
            base_length: Base note length in ticks (480 = quarter note)
            length_var: Length variation factor (0.0-1.0)
        """
        self.base_length = base_length
        self.length_var = length_var
        self.vowel_chars = VOWEL_CHARS
        self.consonant_chars = CONSONANT_CHARS

    def get_note_length(
        self,
        phoneme: str,
        length_factor: float = 1.0,
        melody_brain: Optional[object] = None,
    ) -> int:
        """Calculate note length with variation based on phoneme type.

        Vowels get longer durations, consonants shorter.
        Length is clamped to HiroConfig min/max bounds.

        Args:
            phoneme: Romaji phoneme string (e.g., 'a', 'ka', '+')
            length_factor: Multiplier for length (for stretching)
            melody_brain: Optional MelodyBrain for context

        Returns:
            Note length in ticks, bounded by HiroConfig limits
        """
        # Continuation notes get fixed short length
        if phoneme == "+":
            factor = 0.6
            length = int(self.base_length * factor * length_factor)
            return max(HiroConfig.MIN_NOTE_LEN, min(HiroConfig.MAX_NOTE_LEN, length))

        # Get vowel/consonant chars from melody_brain if available
        vowel_chars = (
            getattr(melody_brain, "VOWEL_CHARS", VOWEL_CHARS)
            if melody_brain
            else VOWEL_CHARS
        )
        consonant_chars = (
            getattr(melody_brain, "CONSONANT_CHARS", CONSONANT_CHARS)
            if melody_brain
            else CONSONANT_CHARS
        )

        phoneme_char = phoneme[0] if len(phoneme) > 0 else "a"

        # Apply different length factors based on phoneme type
        if phoneme_char in vowel_chars:
            factor = 1.0 + random.uniform(-self.length_var, self.length_var * 0.3)
        elif phoneme_char in consonant_chars:
            factor = 0.5 + random.uniform(0, self.length_var * 1.5)
        else:
            factor = 0.7 + random.uniform(-self.length_var * 0.2, self.length_var * 0.2)

        length = int(self.base_length * factor * length_factor)
        return max(HiroConfig.MIN_NOTE_LEN, min(HiroConfig.MAX_NOTE_LEN, length))

    def get_random_pitch(
        self,
        root_key: int,
        scale_name: str,
        intone_level: str = "Medium (2)",
        flat_mode: bool = False,
        quartertone_mode: bool = False,
        use_motifs: bool = True,
        chord_mode: bool = False,
    ) -> float:
        """Generate random pitch within scale constraints.

        Applies motif memory, chords, and microtones based on settings.

        Args:
            root_key: MIDI note number for root
            scale_name: Name of scale (e.g., "Major Pentatonic")
            intone_level: Intonation setting ("Tight", "Medium", "Wide", "Wild")
            flat_mode: If True, return flat/monotone pitch
            quartertone_mode: If True, allow microtones
            use_motifs: If True, use pitch motif memory
            chord_mode: If True, generate chord-based pitches

        Returns:
            MIDI note number (may be float for microtones)
        """
        scale = SCALES.get(scale_name, SCALES["Major"])

        # Flat mode returns root + fifth (safe, neutral)
        if flat_mode:
            return root_key + 5

        # Start with random scale degree
        base_semitone = random.choice(scale)

        # Apply motif memory
        if use_motifs:
            if not hasattr(self, "_recent_notes"):
                self._recent_notes = []
            recent = self._recent_notes
            if len(recent) >= 2:
                # Continue motif from previous notes
                motif_continue = recent[-1]
                base_semitone = min(
                    scale, key=lambda x: abs(x - (motif_continue % 12))
                )
            self._recent_notes.append(base_semitone)
            # Keep only last 4 notes for motif tracking
            if len(self._recent_notes) > 4:
                self._recent_notes = self._recent_notes[-4:]

        # Apply chord constraints
        settings = get_intone_settings(intone_level)
        if chord_mode:
            # Generate I-IV-V chord
            chord_root = {0: 0, 1: 3, 2: 5}.get(random.randint(0, 2), 0)
            chord = [
                n
                for n in [(chord_root + i) % 12 for i in [0, 4, 7]]
                if n in scale
            ]
            base_semitone = random.choice(chord or scale)

        # Apply leap limits from intonation settings
        if settings["leap"] < 3:
            base_semitone = min(base_semitone, settings["leap"] * 2)

        # Apply microtones
        if quartertone_mode and random.random() < 0.5:
            base_semitone += random.choice([0, 0.5, -0.5])

        return root_key + base_semitone

    def create_stretch_notes(
        self,
        phoneme: str,
        stretch_prob: float = 0.25,
        max_stretch: int = 3,
        melody_brain: Optional[object] = None,
    ) -> List[Tuple[str, float]]:
        """Create stretched note variations for a phoneme.

        Handles vowel doubling, note extension with continuation notes (+).

        Args:
            phoneme: Hiragana phoneme string
            stretch_prob: Probability of stretching (0.0-1.0)
            max_stretch: Maximum continuation notes to add
            melody_brain: Optional MelodyBrain for vowel definitions

        Returns:
            List of (phoneme, length_factor) tuples for stretching

        Example:
            >>> gen.create_stretch_notes("あ", 0.5)
            [("あ", 1.2), ("+", 0.6), ("+", 0.6)]
        """
        vowel_chars = (
            getattr(melody_brain, "VOWEL_CHARS", VOWEL_CHARS)
            if melody_brain
            else VOWEL_CHARS
        )

        # Double vowels (長音) get extended
        if (
            len(phoneme) >= 2
            and phoneme[0] == phoneme[1]
            and phoneme[0] in vowel_chars
        ):
            return [(phoneme[0], 1.8)]

        # Single vowels may be stretched with continuation notes
        if (
            len(phoneme) == 1
            and phoneme in vowel_chars
            and random.random() < (stretch_prob + 0.5)
        ):
            stretches = random.randint(1, max_stretch)
            return [(phoneme, 1.2)] + [("+", 0.6)] * stretches

        # No stretching
        return [(phoneme, 1.0)]


class PitchBendCalculator:
    """Calculator for pitch bend (PBS/PBW) parameters.

    Generates pitch bend curves for accents, microtones, and special effects.
    """

    @staticmethod
    def calculate_quartertone_bend(
        note_num: float,
    ) -> Tuple[str, str]:
        """Calculate bend for quartertone pitch.

        Args:
            note_num: MIDI note with fractional part (e.g., 60.5)

        Returns:
            Tuple of (pbs, pbw) strings
        """
        fraction = note_num - int(note_num)
        if fraction == 0:
            return "0;0", "0"

        bend_amount = int(fraction * 50)  # Convert to cents
        return f"0;{bend_amount}", "10"

    @staticmethod
    def calculate_accent_bend(
        melody_brain: object,
        note_length: int,
        accent: str,
    ) -> Tuple[str, str, str, str]:
        """Calculate bend for accent pattern.

        Applies pitch drops and rises based on accent type and word position.

        Args:
            melody_brain: MelodyBrain instance with accent state
            note_length: Note length in ticks
            accent: Accent type (e.g., "Odaka", "Atamadaka")

        Returns:
            Tuple of (pbs, pbw, pby, pbm) strings
        """
        pbs = "0;0"
        pbw = "0"
        pby = "0"
        pbm = ","

        # Handle pitch drops
        if (
            hasattr(melody_brain, "is_high_pitch")
            and not melody_brain.is_high_pitch
            and hasattr(melody_brain, "prev_high_pitch")
            and melody_brain.prev_high_pitch
        ):
            drop_strength = random.choice([-50, -40, -35, -30, -25])
            pbs = f"0;{drop_strength}"
            pbw = "0"

            # Add recovery curve for long notes
            if note_length > 200:
                pbw = f"25,50,{int(note_length * 0.15)}"
                pby = f"-15,-15,0"

        # Odaka (high pitch on second mora)
        elif accent == "Odaka" and hasattr(melody_brain, "word_pos"):
            if melody_brain.word_pos == 2:
                pbs = f"0;{random.choice([25, 35, 45])}"
                pbw = "20"

        # First mora high pitch
        elif hasattr(melody_brain, "word_pos") and hasattr(
            melody_brain, "is_high_pitch"
        ):
            if melody_brain.word_pos == 1 and melody_brain.is_high_pitch:
                pbs = f"0;{random.choice([15, 20])}"
                pbw = "0"

        return pbs, pbw, pby, pbm


class EnvelopeCalculator:
    """Calculator for note envelope parameters.

    Intensity modulation based on melody progression and note position.
    """

    @staticmethod
    def calculate_intensity(
        melody_brain: object,
        intensity_base: int,
        note_position: int = 0,
        phrase_length: int = 12,
    ) -> int:
        """Calculate intensity (volume) for a note.

        Applies dynamic changes based on phrase position and melody contour.

        Args:
            melody_brain: MelodyBrain with current note
            intensity_base: Base intensity (50-120)
            note_position: Position in phrase (0-phrase_length)
            phrase_length: Total phrase length

        Returns:
            Intensity value (0-200)
        """
        phrase_progress = note_position / max(1, phrase_length)
        last_note_safe = getattr(melody_brain, "last_note", 0)

        melody_offset = melody_brain.get_intensity(last_note_safe, phrase_progress)
        intensity = max(50, min(120, intensity_base + (melody_offset - 80)))

        return int(intensity)


__all__ = [
    "NoteGenerator",
    "PitchBendCalculator",
    "EnvelopeCalculator",
]


