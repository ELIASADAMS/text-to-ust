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
from hiro_ust.logger import get_logger

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
        logger.info(f"HiroUSTProcessor initialized with config: {config}")

        # Import here to avoid circular imports
        from hiro_ust.converter import HiroUSTGenerator, Phonemizer
        from hiro_ust.melody import MelodyBrain

        self.generator = HiroUSTGenerator()
        self.phonemizer = Phonemizer()
        self.melody_brain = MelodyBrain(seed=config.seed)

    def process_lyrics(
        self,
        lyrics: str,
        project_name: str = "Hiro_Main",
        output_format: str = "ust"
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

            # TODO: Implement full processing pipeline
            # 1. Parse lyrics structure
            # 2. Generate phonemes
            # 3. Generate melody
            # 4. Generate UST/USTX

            logger.info("Lyrics processing complete")
            return ""  # TODO: Return actual content

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

