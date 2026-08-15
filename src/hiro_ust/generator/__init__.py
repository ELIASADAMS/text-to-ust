"""UST/USTX output and note-level generation utilities."""

from .ust_strings import UST_HEADER_TEMPLATE, REST_NOTE_TEMPLATE, SMALL_TSU_TEMPLATE, NOTE_BLOCK_TEMPLATE, TRACK_END
from .note_generator import NoteGenerator, PitchBendCalculator, EnvelopeCalculator


class USTWriter:
    """Serialize note/rest events to classic UST text."""

    def __init__(self, project_name: str, tempo: float):
        self.lines = []
        self.note_id = 0
        self.project_name = str(project_name)
        self.tempo = float(tempo)
        self._write_header()

    def _write_header(self) -> None:
        self.lines.append(UST_HEADER_TEMPLATE.format(tempo=self.tempo, project_name=self.project_name))

    def add_rest(self, length: int) -> None:
        self.lines.append(REST_NOTE_TEMPLATE.format(note_id=self.note_id, length=int(length)))
        self.note_id += 1

    def add_small_tsu(self, root_key: int, length: int = 60) -> None:
        self.lines.append(SMALL_TSU_TEMPLATE.format(note_id=self.note_id, length=int(length), root_key=int(root_key)))
        self.note_id += 1

    def add_note(self, length: int, lyric: str, note_num: float, pre_utter: int, voice_overlap: int,
                 intensity: int, envelope: str, pbs: str | int = 0, pbw: str | int = 0,
                 flags: str = "") -> None:
        """Add a note. Fractional MIDI pitches are converted to UTAU pitch bends."""
        rounded = int(round(float(note_num)))
        fraction = float(note_num) - rounded
        if abs(fraction) > 1e-9 and (pbs == 0 or pbs == "0"):
            # UTAU PBS=50 corresponds to a 100-cent range; 0.5 semitone = 25 units.
            bend = int(round(fraction * 50))
            pbs = "0;0"
            pbw = f"10"
            # PBY is not emitted by this compact writer; the two-point bend is sufficient.
            flags = flags
            bend_curve = f"{bend}"
        else:
            bend_curve = None

        block = NOTE_BLOCK_TEMPLATE.format(
            note_id=self.note_id,
            length=int(length),
            lyric=lyric,
            note_num=rounded,
            pre_utter=int(pre_utter),
            voice_overlap=int(voice_overlap),
            intensity=int(intensity),
            envelope=envelope,
            pbs=str(pbs),
            pbw=str(pbw),
            flags=flags,
        )
        if bend_curve is not None:
            block = block.replace("\n[Flags]", f"\n[PBY]\n{bend_curve}\n[Flags]")
        self.lines.append(block)
        self.note_id += 1

    def finalize(self) -> str:
        self.lines.append(TRACK_END)
        return "\n".join(self.lines)


__all__ = [
    "USTWriter", "NoteGenerator", "PitchBendCalculator", "EnvelopeCalculator",
    "UST_HEADER_TEMPLATE", "REST_NOTE_TEMPLATE", "SMALL_TSU_TEMPLATE", "NOTE_BLOCK_TEMPLATE", "TRACK_END",
]
