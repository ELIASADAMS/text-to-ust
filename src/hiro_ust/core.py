"""
Core API for Hiro UST Generator.

Provides high-level interface for programmatic use without GUI.
This module serves as the main entry point for library users.

Example:
    >>> from hiro_ust.core import HiroUSTProcessor
    >>> processor = HiroUSTProcessor(config)
    >>> ust_content = processor.process_lyrics("きゃっきゃ")
    >>> with open("output.ust", "w", encoding="utf-8-sig") as f:
    ...     f.write(ust_content)
"""

from dataclasses import dataclass
from typing import Optional

try:
    from hiro_ust.logger import get_logger
except ImportError:
    # Fallback if logger not available
    import logging

    get_logger = lambda name: logging.getLogger(f"hiro_ust.{name}")

logger = get_logger(__name__)


@dataclass
class GeneratorConfig:
    """Configuration for UST generation.

    Attributes:
        tempo: BPM (60-240)
        base_length: Base note length in ticks
        root_key: MIDI note for voice root
        scale: Musical scale name
        intone_level: Intonation level
        length_var: Length variation factor
        stretch_prob: Probability of note stretching
        pre_utterance: Pre-utterance time in ms
        voice_overlap: Voice overlap time in ms
        intensity_base: Base intensity (50-120)
        envelope: Envelope preset name
        flat_mode: Monotone mode
        quartertone_mode: Enable microtones
        lyrical_mode: Use intelligent melody
        use_motifs: Use motif memory
        seed: Random seed for reproducibility
    """

    tempo: float = 120.0
    base_length: int = 240
    root_key: int = 60
    scale: str = "Major Pentatonic"
    intone_level: str = "Medium (2)"
    length_var: float = 0.3
    stretch_prob: float = 0.25
    pre_utterance: int = 25
    voice_overlap: int = 10
    intensity_base: int = 80
    envelope: str = "Pop"
    flat_mode: bool = False
    quartertone_mode: bool = False
    lyrical_mode: bool = True
    use_motifs: bool = True
    seed: int = 1234


class HiroUSTProcessor:
    """Main processor for generating UST files from lyrics.

    This class provides the primary API for programmatic UST generation.
    It coordinates between phonemization, melody generation, and UST writing.

    Usage:
        config = GeneratorConfig(tempo=120, scale="Major Pentatonic")
        processor = HiroUSTProcessor(config)
        ust_content = processor.process_lyrics(
            "きゃっきゃ",
            project_name="MyProject"
        )
    """

    def __init__(self, config: GeneratorConfig):
        """Initialize processor with configuration.

        Args:
            config: GeneratorConfig instance with all settings
        """
        self.config = config
        logger.info(
            f"HiroUSTProcessor initialized with tempo={config.tempo}, scale={config.scale}"
        )

        # Lazy imports to avoid circular dependencies
        self._generator = None
        self._phonemizer = None
        self._melody_brain = None

    @property
    def generator(self):
        """Lazy-load HiroUSTGenerator."""
        if self._generator is None:
            from hiro_ust.converter import HiroUSTGenerator

            self._generator = HiroUSTGenerator()
        return self._generator

    @property
    def phonemizer(self):
        """Lazy-load Phonemizer."""
        if self._phonemizer is None:
            from hiro_ust.converter import Phonemizer

            self._phonemizer = Phonemizer()
        return self._phonemizer

    @property
    def melody_brain(self):
        """Lazy-load MelodyBrain."""
        if self._melody_brain is None:
            from hiro_ust.melody import MelodyBrain

            self._melody_brain = MelodyBrain(seed=self.config.seed)
        return self._melody_brain

    def process_lyrics(
        self, lyrics: str, project_name: str = "Hiro_Main", output_format: str = "ust"
    ) -> str:
        """Process lyrics and generate UST/USTX content.

        Args:
            lyrics: Input lyrics (hiragana, katakana, or romaji)
            project_name: Project name for UST metadata
            output_format: "ust" or "ustx"

        Returns:
            Complete UST/USTX file content as string

        Raises:
            ValueError: If output_format is invalid
            RuntimeError: If processing fails
        """
        if output_format not in ("ust", "ustx"):
            raise ValueError(f"Invalid output format: {output_format}")

        try:
            logger.info(f"Processing lyrics: {lyrics[:50]}...")

            # Lazy imports to avoid circular imports
            from hiro_ust.hiro_ust_dev import (
                parse_song_structure,
                text_to_ustx,
                HiroUSTGenerator,
            )
            from hiro_ust.melody.melody_logic import MelodyBrain

            # Use existing phonemizer if available (lazy property) else create one
            phonemizer = None
            try:
                phonemizer = self.phonemizer
            except Exception:
                phonemizer = None

            # Build melody brain
            melody_brain = self.melody_brain

            # Parse lyrics into elements (phonemes + pauses)
            parts, elements = parse_song_structure(
                lyrics,
                (
                    HiroConfig.PAUSE_LINE_UNIT * 2
                    if hasattr(HiroConfig, "PAUSE_LINE_UNIT")
                    else 960
                ),
                (
                    HiroConfig.PAUSE_SECTION_UNIT * 2
                    if hasattr(HiroConfig, "PAUSE_SECTION_UNIT")
                    else 1920
                ),
                on_warning=lambda msg: logger.warning(msg),
                phonemizer=phonemizer,
            )

            logger.debug(f"Parsed elements: {len(elements)} items")

            if output_format == "ustx":
                # Use existing high-level text_to_ustx function
                ustx = text_to_ustx(
                    elements,
                    project_name,
                    float(self.config.tempo),
                    (
                        int(self.config.base_length)
                        if hasattr(self.config, "base_length")
                        else 240
                    ),
                    (
                        KEY_ROOTS.get(self.config.voice, 60)
                        if hasattr(self.config, "voice")
                        else 60
                    ),
                    (
                        self.config.scale
                        if hasattr(self.config, "scale")
                        else next(iter(SCALES))
                    ),
                    (
                        self.config.intone
                        if hasattr(self.config, "intone")
                        else "Medium (2)"
                    ),
                    (
                        float(self.config.length_var)
                        if hasattr(self.config, "length_var")
                        else 0.3
                    ),
                    (
                        float(self.config.stretch_prob)
                        if hasattr(self.config, "stretch_prob")
                        else 0.25
                    ),
                    melody_brain,
                )
                logger.info("Lyrics processing complete (ustx)")
                return ustx

            # Fallback: generate simple UST using USTWriter from hiro_ust.hiro_ust_dev
            from hiro_ust.hiro_ust_dev import HiroUSTGenerator, USTWriter

            generator = HiroUSTGenerator()
            writer = USTWriter(
                project_name=project_name, tempo=float(self.config.tempo)
            )

            root_key = (
                KEY_ROOTS.get(self.config.voice, 60)
                if hasattr(self.config, "voice")
                else 60
            )

            for element in elements:
                if element.startswith("PAUSE_WORD:"):
                    writer.add_rest(int(element.split(":")[1]))
                    continue
                if element.startswith("PAUSE_LINE:"):
                    writer.add_rest(
                        HiroConfig.PAUSE_LINE_UNIT
                        if hasattr(HiroConfig, "PAUSE_LINE_UNIT")
                        else 480
                    )
                    continue
                if element == "っ":
                    writer.add_small_tsu(root_key)
                    continue
                hir = generator.romaji_to_hiragana(element)
                # simple mapping: vowel -> one note
                writer.add_note(
                    length=(
                        HiroConfig.MIN_NOTE_LEN
                        if hasattr(HiroConfig, "MIN_NOTE_LEN")
                        else 120
                    ),
                    lyric=hir,
                    note_num=root_key,
                    pre_utter=25,
                    voice_overlap=10,
                    intensity=80,
                    envelope=(
                        HiroConfig.DEFAULT_ENVELOPE
                        if hasattr(HiroConfig, "DEFAULT_ENVELOPE")
                        else "0,10,35,0,100,100,0"
                    ),
                )

            ust = writer.finalize()
            logger.info("Lyrics processing complete (ust)")
            return ust

        except Exception as e:
            logger.error(f"Failed to process lyrics: {e}")
            raise RuntimeError(f"Lyrics processing failed: {e}") from e

    def get_supported_scales(self) -> list:
        """Get list of supported musical scales.

        Returns:
            List of scale names
        """
        from hiro_ust.melody import SCALES

        return list(SCALES.keys())

    def get_supported_envelopes(self) -> list:
        """Get list of supported envelope presets.

        Returns:
            List of envelope preset names
        """
        from hiro_ust.voice import get_envelope_presets

        return list(get_envelope_presets().keys())


__all__ = [
    "HiroUSTProcessor",
    "GeneratorConfig",
]
