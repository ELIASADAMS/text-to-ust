"""Procedural melody generation with deterministic randomness and motif memory."""

import random
from collections import defaultdict
from typing import Sequence

import numpy as np

from ..constants import VOWEL_CHARS, CONSONANT_CHARS
from .intone_utils import get_intone_settings
from .scales import SCALES


class NoteMarkov:
    """Small order-N pitch transition model."""

    def __init__(self, order: int = 1, rng: np.random.Generator | None = None):
        self.order = max(1, int(order))
        self.transitions = {}
        self.rng = rng or np.random.default_rng()

    def train(self, notes: Sequence[int], stresses: Sequence[int]) -> None:
        if len(notes) != len(stresses) or len(notes) <= self.order:
            return
        counts = defaultdict(lambda: np.zeros(12, dtype=float))
        for i in range(len(notes) - self.order):
            state = tuple(int(n) % 12 for n in notes[i:i + self.order])
            stress = int(stresses[i + self.order])
            counts[(state, stress)][int(notes[i + self.order]) % 12] += 1
        self.transitions = dict(counts)

    def next_note(self, state: Sequence[int], stress: int, scale: Sequence[int]) -> int:
        scale = list(scale)
        key = (tuple(int(n) % 12 for n in state[-self.order:]), int(stress))
        if key not in self.transitions:
            return int(self.rng.choice(scale))
        probs = self.transitions[key].copy()
        allowed = np.isin(np.arange(12), scale)
        probs[~allowed] *= 0.1
        if probs.sum() <= 0:
            return int(self.rng.choice(scale))
        probs /= probs.sum()
        return int(self.rng.choice(12, p=probs))


class MotifMemory:
    """Stores interval motifs so they can be repeated at different pitches."""

    def __init__(self, motif_length: int = 4, max_motifs: int = 5, rng: random.Random | None = None):
        self.motif_length = max(2, int(motif_length))
        self.max_motifs = max(1, int(max_motifs))
        self.stored_motifs: list[list[int]] = []
        self.rng = rng or random.Random()

    def add_motif(self, notes: Sequence[int]) -> None:
        if len(notes) < self.motif_length:
            return
        notes = list(notes[-self.motif_length:])
        intervals = [notes[i + 1] - notes[i] for i in range(len(notes) - 1)]
        if intervals and intervals not in self.stored_motifs:
            self.stored_motifs.append(intervals)
            self.stored_motifs = self.stored_motifs[-self.max_motifs:]

    def get_motif_note(self, current_note: int, scale: Sequence[int], use_motif_prob: float = 0.4) -> int:
        if not self.stored_motifs or self.rng.random() >= use_motif_prob:
            return int(self.rng.choice(list(scale)))
        motif = self.rng.choice(self.stored_motifs)
        interval = motif[0]
        target = int(current_note) + interval
        return int(min(scale, key=lambda x: abs(x - target)))

    def debug_motifs(self) -> str:
        if not self.stored_motifs:
            return "No motifs stored"
        return " | ".join(f"[{','.join(map(str, m))}]" for m in self.stored_motifs)


class MelodyBrain:
    _intone_cache = {}

    def __init__(self, seed: int | None = None):
        self.seed = 1234 if seed is None else int(seed)
        self.rng = random.Random(self.seed)
        self.np_rng = np.random.default_rng(self.seed)
        self.last_note = 0
        self.phrases = []
        self.phrase_len = 0
        self.recent_notes = []
        self.note_history = []
        self.motif_memory = MotifMemory(motif_length=4, rng=self.rng)
        self.VOWEL_CHARS = VOWEL_CHARS
        self.CONSONANT_CHARS = CONSONANT_CHARS
        self.word_morae = []
        self.word_pos = 0
        self.pitch_drop_pos = 0
        self.is_high_pitch = False
        self.prev_high_pitch = False
        self.markov = NoteMarkov(order=1, rng=self.np_rng)

    def _is_vowel(self, phoneme: str) -> bool:
        if not phoneme:
            return False
        if phoneme in VOWEL_CHARS:
            return True
        # Hiro phonemes are normally romaji (ka, shi, kyo, ...).
        return phoneme[-1].lower() in "aeiou"

    def train_markov(self, phonemes: Sequence[str], notes: Sequence[int] | None = None) -> None:
        if notes is None:
            notes = self.note_history[-32:]
        if len(notes) < 2:
            return
        phonemes = list(phonemes)[-len(notes):]
        stresses = [1 if self._is_vowel(p) else 0 for p in phonemes]
        if len(stresses) == len(notes):
            self.markov.train(notes, stresses)

    def set_accent_pattern(self, pattern: str, word_length: int) -> None:
        self.word_morae = list(range(max(0, word_length)))
        self.word_pos = 0
        if pattern == "Heiban":
            self.pitch_drop_pos, self.is_high_pitch = 999, True
        elif pattern == "Atamadaka":
            self.pitch_drop_pos, self.is_high_pitch = 1, True
        elif pattern == "Nakadaka":
            self.pitch_drop_pos, self.is_high_pitch = max(2, word_length // 2), True
        elif pattern == "Odaka":
            self.pitch_drop_pos, self.is_high_pitch = 999, False
        else:
            self.pitch_drop_pos, self.is_high_pitch = 0, False

    def get_smart_note(self, root_midi, scale_name, phoneme, intone_level="Tight (1)", flat_mode=False,
                       quarter_tone=False, use_motifs=True, chord_mode=False, contour_bias=0,
                       pitch_range=70, accent="None"):
        scale = SCALES[scale_name]
        self.phrase_len += 1
        settings = self._intone_cache.setdefault(intone_level, get_intone_settings(intone_level))
        is_vowel = self._is_vowel(phoneme)
        is_stretch = phoneme == "+"
        phrase_pos = (self.phrase_len - 1) / max(12, settings["phrase"])
        contour_curve = contour_bias / 100.0
        contour_target = (phrase_pos + contour_curve * phrase_pos * (1 - phrase_pos)) * pitch_range
        stress = int(is_vowel)

        if self.phrase_len > settings["phrase"] or phoneme in "。！？":
            self.phrases.append(self.last_note)
            self.last_note = min(max(0, int(contour_target * 0.8)), 11)
            target_note = self.last_note
            self.phrase_len = 1
        else:
            markov_note = self.markov.next_note([self.last_note], stress, scale)
            motif_note = self.motif_memory.get_motif_note(self.last_note, scale) if use_motifs else markov_note
            if is_vowel:
                local = self.rng.choice([4, 7] + list(scale[-3:]))
                target_note = markov_note * 0.45 + motif_note * 0.30 + local * 0.15 + contour_target * 0.10
            elif is_stretch:
                target_note = markov_note * 0.75 + self.last_note * 0.25
            else:
                target_note = markov_note * 0.60 + motif_note * 0.25 + contour_target * 0.15

            if chord_mode:
                beat_pos = (self.phrase_len - 1) % 8
                chord_root = {0: 0, 3: 5, 5: 7}.get(beat_pos, 0)
                chord_tones = [n for n in ((chord_root + i) % 12 for i in (0, 4, 7)) if n in scale]
                if chord_tones:
                    target_note = min(chord_tones, key=lambda x: abs(x - target_note))

        if accent != "None":
            accent_shift = 1.5 if self.is_high_pitch else -1.5
            target_note = target_note * 0.7 + (target_note + accent_shift) * 0.3

        self.prev_high_pitch = self.is_high_pitch
        self.word_pos += 1
        if self.word_pos >= self.pitch_drop_pos:
            self.is_high_pitch = False
        if phoneme in "。！？。," or (self.word_morae and self.word_pos >= len(self.word_morae)):
            self.word_pos = 0
            self.is_high_pitch = False

        max_leap = settings["leap"]
        motion = max(-max_leap, min(max_leap, target_note - self.last_note))
        new_note = self.last_note + motion
        self.last_note = min(scale, key=lambda x: abs(x - new_note))

        if quarter_tone and self.rng.random() < 0.3 and is_vowel:
            self.last_note += self.rng.choice([0, 0.5, -0.5])
        if flat_mode:
            self.last_note = 5

        self.note_history.append(self.last_note)
        self.recent_notes.append(self.last_note)
        if len(self.recent_notes) > 8:
            self.recent_notes.pop(0)
            self.motif_memory.add_motif(self.recent_notes)
        if len(self.note_history) >= 4:
            self.train_markov([phoneme] * min(32, len(self.note_history)), self.note_history[-32:])
        return root_midi + self.last_note

    def get_intensity(self, note_height, phrase_progress):
        base = 80 + int(abs(note_height - 5) * 8)
        if phrase_progress > 0.8:
            base += 15
        return max(50, min(120, base))


__all__ = ["MelodyBrain", "NoteMarkov", "MotifMemory"]
