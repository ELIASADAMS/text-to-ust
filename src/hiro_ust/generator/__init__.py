"""
UST and USTX file generation module.

Handles conversion of note sequences to UST (Uta Synthesizer Tool)
and USTX (OpenUtau) file formats.

Components:
  - USTWriter: Generates UST format output
  - USTXWriter: Generates USTX format output
  - NoteGenerator: Note-level generation logic
  - PitchBendCalculator: Pitch bend parameter calculation
  - EnvelopeCalculator: Envelope and intensity calculation
"""

from .ust_strings import (
    UST_HEADER_TEMPLATE,
    REST_NOTE_TEMPLATE,
    SMALL_TSU_TEMPLATE,
    NOTE_BLOCK_TEMPLATE,
    TRACK_END,
)
from .note_generator import (
    NoteGenerator,
    PitchBendCalculator,
    EnvelopeCalculator,
)
from hiro_ust.logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "USTWriter",
    "NoteGenerator",
    "PitchBendCalculator",
    "EnvelopeCalculator",
    "UST_HEADER_TEMPLATE",
    "REST_NOTE_TEMPLATE",
    "SMALL_TSU_TEMPLATE",
    "NOTE_BLOCK_TEMPLATE",
    "TRACK_END",
]


class USTWriter:
    """Generates UST (Uta Synthesizer Tool) format files.

    UST format is a plain-text music notation format commonly used with
    UTAU (Utau Synthesizer) for voice synthesis.

    Attributes:
        lines (list): Accumulated UST format lines
        note_id (int): Sequential ID counter for notes
        project_name (str): Name of the project
        tempo (float): Tempo in BPM
    """

    def __init__(self, project_name: str, tempo: float):
        self.lines = []
        self.note_id = 0
        self.project_name = str(project_name)
        self.tempo = tempo
        self._write_header()

    def _write_header(self) -> None:
        """Write UST header section with project metadata."""
        self.lines.append(
            UST_HEADER_TEMPLATE.format(tempo=self.tempo, project_name=self.project_name)
        )

    def add_rest(self, length: int) -> None:
        """Add a rest (silence) note of specified length."""
        self.lines.append(
            REST_NOTE_TEMPLATE.format(note_id=self.note_id, length=length)
        )
        self.note_id += 1

    def add_small_tsu(self, root_key: int, length: int = 60) -> None:
        """Add a small tsu (っ) gemination note."""
        self.lines.append(
            SMALL_TSU_TEMPLATE.format(
                note_id=self.note_id, length=length, root_key=int(root_key)
            )
        )
        self.note_id += 1

    def add_note(
        self,
        length: int,
        lyric: str,
        note_num: float,
        pre_utter: int,
        voice_overlap: int,
        intensity: int,
        envelope: str,
        pbs: int = 0,
        pbw: int = 0,
        flags: str = "",
    ) -> None:
        """Add a music note with phonetic and timing information.

        Args:
            length: Duration in ticks
            lyric: Hiragana/romaji lyric text
            note_num: MIDI note number
            pre_utter: Pre-utterance (lead-in) time in ms
            voice_overlap: Voice overlap time in ms
            intensity: Volume intensity (0-200)
            envelope: Pitch envelope curve (ATK,DEC,SUSTend,REL format)
            pbs: Pitch bend start (cents)
            pbw: Pitch bend width
            flags: Processing flags (e.g., 'g0B0H0P86')
        """
        self.lines.append(
            NOTE_BLOCK_TEMPLATE.format(
                note_id=self.note_id,
                length=length,
                lyric=lyric,
                note_num=int(round(note_num)),
                pre_utter=pre_utter,
                voice_overlap=voice_overlap,
                intensity=intensity,
                envelope=envelope,
                pbs=str(pbs),
                pbw=str(pbw),
                flags=flags,
            )
        )
        self.note_id += 1

    def finalize(self) -> str:
        """Finalize and return complete UST file content as string."""
        self.lines.append(TRACK_END)
        return "\n".join(self.lines)


__all__ = [
    "USTWriter",
]
