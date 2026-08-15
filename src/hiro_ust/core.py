"""Public core API for the Hiro UST generator."""

from .config import GeneratorConfig, HiroConfig
from .constants import VOWEL_CHARS, CONSONANT_CHARS
from .converter import HiroUSTGenerator, Phonemizer
from .generator import USTWriter
from .melody import MelodyBrain, SCALES
from .voice.key_roots import KEY_ROOTS


class HiroUSTProcessor:
    """High-level facade for converting lyrics into UST/USTX output."""

    def __init__(self, config: GeneratorConfig | None = None):
        self.config = config or GeneratorConfig()
        self._generator = HiroUSTGenerator()
        self._phonemizer = Phonemizer()
        self._melody_brain = None

    @property
    def generator(self):
        return self._generator

    @property
    def phonemizer(self):
        return self._phonemizer

    @property
    def melody_brain(self):
        if self._melody_brain is None:
            self._melody_brain = MelodyBrain(seed=self.config.seed)
        return self._melody_brain

    def process_lyrics(
        self,
        lyrics: str,
        project_name: str = "Hiro_Main",
        output_format: str = "ust",
    ) -> str:
        """Convert lyrics to UST or USTX using the configured engine."""
        if output_format not in {"ust", "ustx"}:
            raise ValueError(f"Invalid output format: {output_format}")
        if not isinstance(lyrics, str) or not lyrics.strip():
            raise ValueError("lyrics must be a non-empty string")

        try:
            from .hiro_ust_dev import parse_song_structure, text_to_ustx

            _, elements = parse_song_structure(
                lyrics,
                HiroConfig.PAUSE_LINE_UNIT * 2,
                HiroConfig.PAUSE_SECTION_UNIT * 2,
                on_warning=lambda msg: __import__("logging").getLogger(__name__).warning(msg),
                phonemizer=self.phonemizer,
            )

            if output_format == "ustx":
                return text_to_ustx(
                    elements,
                    project_name,
                    self.config.tempo,
                    self.config.base_length,
                    self.config.effective_root_key,
                    self.config.scale,
                    self.config.intone_level,
                    self.config.length_var,
                    self.config.stretch_prob,
                    self.melody_brain,
                )

            writer = USTWriter(project_name=project_name, tempo=self.config.tempo)
            root_key = self.config.effective_root_key
            for element in elements:
                if element.startswith("PAUSE_WORD:"):
                    writer.add_rest(int(element.split(":", 1)[1]))
                elif element.startswith("PAUSE_LINE:"):
                    writer.add_rest(HiroConfig.PAUSE_LINE_UNIT)
                elif element == "っ":
                    writer.add_small_tsu(root_key)
                else:
                    writer.add_note(
                        length=HiroConfig.MIN_NOTE_LEN,
                        lyric=self.generator.romaji_to_hiragana(element),
                        note_num=root_key,
                        pre_utter=self.config.pre_utterance,
                        voice_overlap=self.config.voice_overlap,
                        intensity=self.config.intensity_base,
                        envelope=HiroConfig.DEFAULT_ENVELOPE,
                    )
            return writer.finalize()
        except Exception as exc:
            raise RuntimeError(f"Lyrics processing failed: {exc}") from exc

    def get_supported_scales(self) -> list[str]:
        return list(SCALES.keys())

    def get_supported_envelopes(self) -> list[str]:
        try:
            from .voice.presets import ENVELOPE_PRESETS
            return list(ENVELOPE_PRESETS.keys())
        except ImportError:
            return []


__all__ = ["HiroUSTProcessor", "GeneratorConfig"]
