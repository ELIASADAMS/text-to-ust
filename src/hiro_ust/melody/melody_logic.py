"""Phrase-aware procedural melody generation.

The engine uses deterministic randomness, phrase contours, melodic candidate
scoring, interval motifs, register targets, cadence handling, and optional
harmonic constraints. It is intentionally procedural so the same seed can
reproduce a melody while different seeds produce genuinely different shapes.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Sequence

import numpy as np

from ..constants import VOWEL_CHARS, CONSONANT_CHARS
from .intone_utils import get_intone_settings
from .scales import SCALES


class NoteMarkov:
    """Small pitch-class transition model kept as a secondary musical cue."""

    def __init__(self, order: int = 1, rng: np.random.Generator | None = None):
        self.order = max(1, int(order))
        self.transitions: dict[tuple[tuple[int, ...], int], np.ndarray] = {}
        self.rng = rng or np.random.default_rng()

    def train(self, notes: Sequence[int], stresses: Sequence[int]) -> None:
        if len(notes) != len(stresses) or len(notes) <= self.order:
            return
        counts = defaultdict(lambda: np.zeros(12, dtype=float))
        for i in range(len(notes) - self.order):
            state = tuple(int(n) % 12 for n in notes[i : i + self.order])
            stress = int(stresses[i + self.order])
            counts[(state, stress)][int(notes[i + self.order]) % 12] += 1
        self.transitions = dict(counts)

    def next_note(self, state: Sequence[int], stress: int, scale: Sequence[int]) -> int | None:
        if not self.transitions:
            return None
        scale = list(scale)
        key = (tuple(int(n) % 12 for n in state[-self.order:]), int(stress))
        probs = self.transitions.get(key)
        if probs is None:
            return None
        probs = probs.copy()
        allowed = np.zeros(12, dtype=bool)
        for pitch_class in scale:
            allowed[int(pitch_class) % 12] = True
        probs[~allowed] *= 0.15
        total = probs.sum()
        if total <= 0:
            return None
        probs /= total
        return int(self.rng.choice(12, p=probs))


class MotifMemory:
    """Stores interval motifs and can continue them in a transposed register."""

    def __init__(
        self,
        motif_length: int = 4,
        max_motifs: int = 8,
        rng: random.Random | None = None,
    ):
        self.motif_length = max(2, int(motif_length))
        self.max_motifs = max(1, int(max_motifs))
        self.stored_motifs: list[list[int]] = []
        self.rng = rng or random.Random()

    def add_motif(self, notes: Sequence[int]) -> None:
        if len(notes) < self.motif_length:
            return
        notes = [int(n) for n in notes[-self.motif_length :]]
        intervals = [notes[i + 1] - notes[i] for i in range(len(notes) - 1)]
        # Reject a totally static motif unless it is the only available idea.
        if not any(intervals) and self.stored_motifs:
            return
        if intervals not in self.stored_motifs:
            self.stored_motifs.append(intervals)
            self.stored_motifs = self.stored_motifs[-self.max_motifs :]

    def choose(self) -> list[int] | None:
        if not self.stored_motifs:
            return None
        return list(self.rng.choice(self.stored_motifs))

    def debug_motifs(self) -> str:
        if not self.stored_motifs:
            return "No motifs stored"
        return " | ".join(f"[{','.join(map(str, m))}]" for m in self.stored_motifs)


class MelodyBrain:
    """Generate melody using phrase-level planning and candidate scoring."""

    _intone_cache = {}

    CONTOURS = (
        "arch",
        "rise",
        "fall",
        "late_peak",
        "wave",
        "pendulum",
        "answer",
    )

    def __init__(self, seed: int | None = None):
        self.seed = 1234 if seed is None else int(seed)
        self.rng = random.Random(self.seed)
        self.np_rng = np.random.default_rng(self.seed + 101)

        self.last_note = 5  # relative semitone from root
        self.phrase_len = 0
        self.phrases: list[int] = []
        self.note_history: list[int] = []
        self.recent_notes: list[int] = []
        self.motif_memory = MotifMemory(motif_length=4, rng=self.rng)

        self.VOWEL_CHARS = VOWEL_CHARS
        self.CONSONANT_CHARS = CONSONANT_CHARS

        self.word_morae: list[int] = []
        self.word_pos = 0
        self.pitch_drop_pos = 0
        self.is_high_pitch = False
        self.prev_high_pitch = False

        self.markov = NoteMarkov(order=1, rng=self.np_rng)

        self._phrase_length = 12
        self._phrase_style = "arch"
        self._phrase_start = True
        self._phrase_register = 5.0
        self._phrase_range = 16.0
        self._previous_direction = 0
        self._active_motif: list[int] | None = None
        self._motif_index = 0
        self._phrase_index = 0

    def _is_vowel(self, phoneme: str) -> bool:
        if not phoneme:
            return False
        if phoneme in VOWEL_CHARS:
            return True
        return phoneme[-1].lower() in "aeiou"

    def train_markov(self, phonemes: Sequence[str], notes: Sequence[int] | None = None) -> None:
        if notes is None:
            notes = self.note_history[-32:]
        if len(notes) < 3:
            return
        phonemes = list(phonemes)[-len(notes) :]
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

    def _start_phrase(self, settings: dict, contour_bias: float, pitch_range: float) -> None:
        self._phrase_length = max(4, int(settings["phrase"]))
        self._phrase_index = len(self.phrases)
        self._phrase_start = False
        self._motif_index = 0
        self._active_motif = None

        style_roll = self.rng.random()
        # contour_bias shifts probability toward rise/fall without removing variety.
        bias = max(-1.0, min(1.0, contour_bias / 50.0))
        weights = {
            "arch": 1.5,
            "rise": 1.0 + max(0.0, bias),
            "fall": 1.0 + max(0.0, -bias),
            "late_peak": 1.0,
            "wave": 1.1,
            "pendulum": 0.8,
            "answer": 0.9,
        }
        total = sum(weights.values())
        marker = style_roll * total
        acc = 0.0
        for style, weight in weights.items():
            acc += weight
            if marker <= acc:
                self._phrase_style = style
                break

        # Register changes slowly between phrases, with intentional contrast.
        center = max(2.0, min(float(pitch_range) - 2.0, float(pitch_range) * 0.48))
        register_jump = self.rng.choice([-1, 0, 0, 1]) * self.rng.uniform(2.0, 5.0)
        if self.phrase_history_nonempty():
            register_jump += self.rng.uniform(-2.5, 2.5)
        self._phrase_register = max(1.0, min(float(pitch_range) - 1.0, center + register_jump))
        self._phrase_range = max(8.0, min(float(pitch_range) * 0.42, 22.0))

    def phrase_history_nonempty(self) -> bool:
        return bool(self.phrases)

    def _contour_target(self, position: float, pitch_range: float) -> float:
        # Position and target are both relative semitone offsets from root.
        x = max(0.0, min(1.0, position))
        center = self._phrase_register
        span = self._phrase_range
        style = self._phrase_style

        if style == "rise":
            shape = x
        elif style == "fall":
            shape = 1.0 - x
        elif style == "late_peak":
            shape = math.sin(math.pi * (x * 0.75))
        elif style == "wave":
            shape = 0.5 + 0.5 * math.sin(2 * math.pi * x - math.pi / 2)
        elif style == "pendulum":
            shape = 0.5 + 0.5 * math.sin(3 * math.pi * x)
        elif style == "answer":
            shape = 0.38 + 0.28 * math.sin(math.pi * x)
        else:  # arch
            shape = math.sin(math.pi * x)

        # Convert 0..1 shape to an offset around the phrase register.
        return max(0.0, min(pitch_range, center + (shape - 0.5) * span))

    @staticmethod
    def _scale_candidates(scale: Sequence[int], pitch_range: float) -> list[int]:
        scale = [int(x) % 12 for x in scale]
        max_offset = max(2, int(round(pitch_range)))
        candidates = []
        for offset in range(max_offset + 1):
            if offset % 12 in scale:
                candidates.append(offset)
        return candidates

    def _score_candidate(
        self,
        candidate: int,
        target: float,
        settings: dict,
        phrase_pos: float,
        is_vowel: bool,
        is_stretch: bool,
        chord_mode: bool,
        scale: Sequence[int],
        contour_bias: float,
        cadence: bool,
        markov_note: int | None,
    ) -> float:
        distance = abs(candidate - target)
        score = -1.25 * distance

        motion = candidate - self.last_note
        abs_motion = abs(motion)

        # Stepwise movement is preferred, but not mandatory.
        if abs_motion <= 2:
            score += 3.3
        elif abs_motion <= 4:
            score += 1.8
        elif abs_motion <= 7:
            score += 0.2
        else:
            score -= 2.8

        # Avoid repeating a note too often; repetition is allowed as a phrase device.
        if candidate == self.last_note:
            score += 0.9 if cadence or is_stretch else -0.8
        if len(self.note_history) >= 2 and candidate == self.note_history[-1] == self.note_history[-2]:
            score -= 2.5

        # Counterweight: after a larger leap, prefer a step in the opposite direction.
        if self._previous_direction and abs(self.note_history[-1] - self.note_history[-2]) >= 4 if len(self.note_history) >= 2 else False:
            if motion * self._previous_direction < 0:
                score += 2.0
            else:
                score -= 1.0

        # Vowels are strong melodic anchors; consonants are more likely passing movement.
        if is_vowel:
            if abs_motion >= 2:
                score += 0.6
        else:
            if abs_motion > 4:
                score -= 1.2

        # Cadences strongly prefer tonic-ish or fifth-ish scale degrees.
        if cadence:
            relative_pc = candidate % 12
            scale_list = [int(x) % 12 for x in scale]
            if relative_pc == scale_list[0]:
                score += 4.5
            elif relative_pc in scale_list[: min(3, len(scale_list))]:
                score += 1.5
            score -= abs_motion * 0.35

        # Phrase target remains the main structural force.
        score += -0.75 * abs(candidate - target)

        # Contour bias controls tendency, not destination.
        if contour_bias:
            wanted = 1 if contour_bias > 0 else -1
            if motion * wanted > 0:
                score += min(abs(contour_bias) / 12.0, 2.0)

        # Harmonic support: chord tones are preferred, especially on phrase accents.
        if chord_mode:
            chord_root = 0
            beat_pos = self.phrase_len % 8
            if beat_pos in {3, 5}:
                chord_root = 5 if beat_pos == 3 else 7
            chord_tones = {(chord_root + i) % 12 for i in (0, 4, 7)}
            if candidate % 12 in chord_tones:
                score += 2.8 if cadence or phrase_pos > 0.75 else 1.2
            else:
                score -= 0.3

        # Optional learned hint. It is deliberately small, never dominant.
        if markov_note is not None:
            score -= 0.18 * abs((candidate % 12) - markov_note)

        return score

    def _choose_motif_note(self, scale: Sequence[int], pitch_range: float) -> int | None:
        if not self._active_motif:
            return None
        if self._motif_index >= len(self._active_motif):
            return None
        target = self.last_note + self._active_motif[self._motif_index]
        self._motif_index += 1
        candidates = self._scale_candidates(scale, pitch_range)
        if not candidates:
            return None
        return min(candidates, key=lambda n: abs(n - target))

    def get_smart_note(
        self,
        root_midi,
        scale_name,
        phoneme,
        intone_level="Tight (1)",
        flat_mode=False,
        quarter_tone=False,
        use_motifs=True,
        chord_mode=False,
        contour_bias=0,
        pitch_range=70,
        accent="None",
    ):
        scale = SCALES[scale_name]
        settings = self._intone_cache.setdefault(intone_level, get_intone_settings(intone_level))
        pitch_range = max(12.0, min(float(pitch_range), 72.0))
        is_vowel = self._is_vowel(phoneme)
        is_stretch = phoneme == "+"
        cadence = self.phrase_len >= max(1, int(settings["phrase"]) - 2)

        if self._phrase_start or self.phrase_len == 0:
            self._start_phrase(settings, contour_bias, pitch_range)

        self.phrase_len += 1
        phrase_pos = (self.phrase_len - 1) / max(1, self._phrase_length - 1)
        phrase_pos = min(1.0, phrase_pos)
        target = self._contour_target(phrase_pos, pitch_range)

        # Activate motifs occasionally, but don't let them dominate every phrase.
        if use_motifs and self._active_motif is None and self.rng.random() < (0.28 if self._phrase_index else 0.15):
            motif = self.motif_memory.choose()
            if motif:
                self._active_motif = motif
                self._motif_index = 0

        motif_candidate = self._choose_motif_note(scale, pitch_range) if use_motifs else None

        candidates = self._scale_candidates(scale, pitch_range)
        if not candidates:
            candidates = list(range(int(pitch_range) + 1))

        # Keep candidate pool musically close, but allow a few large-leap choices.
        max_leap = max(2, int(settings["leap"]))
        local_candidates = [n for n in candidates if abs(n - self.last_note) <= max(7, max_leap + 5)]
        if not local_candidates:
            local_candidates = candidates

        # Add register-near candidates and phrase anchors even when outside local pool.
        anchor_candidates = sorted(candidates, key=lambda n: abs(n - target))[:5]
        pool = sorted(set(local_candidates + anchor_candidates))

        # Learned hint from previous real notes only.
        markov_note = self.markov.next_note(self.note_history[-1:], int(is_vowel), scale)

        scored: list[tuple[float, int]] = []
        for candidate in pool:
            score = self._score_candidate(
                candidate=candidate,
                target=target,
                settings=settings,
                phrase_pos=phrase_pos,
                is_vowel=is_vowel,
                is_stretch=is_stretch,
                chord_mode=chord_mode,
                scale=scale,
                contour_bias=contour_bias,
                cadence=cadence,
                markov_note=markov_note,
            )
            if motif_candidate is not None:
                score += 2.8 - 0.55 * abs(candidate - motif_candidate)
            if accent != "None" and self.is_high_pitch:
                score += 0.45 if candidate >= target else -0.15
            elif accent != "None" and not self.is_high_pitch:
                score += 0.3 if candidate <= target else -0.1
            scored.append((score, candidate))

        scored.sort(reverse=True)
        # Soft choice among the best candidates: noticeably different melodies
        # without sacrificing the musical ranking.
        top = scored[: min(5, len(scored))]
        temperature = 0.55 + self.rng.random() * 0.45
        weights = [math.exp((score - top[0][0]) / temperature) for score, _ in top]
        chosen = self.rng.choices([n for _, n in top], weights=weights, k=1)[0]

        if quarter_tone and is_vowel and self.rng.random() < 0.25:
            chosen += self.rng.choice([0.5, -0.5])

        if flat_mode:
            chosen = min(candidates, key=lambda n: abs(n - min(5, pitch_range)))

        # Keep the generated note inside the intended relative register.
        chosen = max(0.0, min(pitch_range, chosen))

        self.prev_high_pitch = self.is_high_pitch
        self.word_pos += 1
        if self.word_pos >= self.pitch_drop_pos:
            self.is_high_pitch = False
        if phoneme in "。！？,，、" or (self.word_morae and self.word_pos >= len(self.word_morae)):
            self.word_pos = 0
            self.is_high_pitch = False

        self._previous_direction = 0 if chosen == self.last_note else (1 if chosen > self.last_note else -1)
        self.last_note = chosen
        self.note_history.append(chosen)
        self.recent_notes.append(chosen)
        if len(self.recent_notes) > 8:
            self.recent_notes.pop(0)
        if len(self.note_history) >= 4 and len(self.note_history) % 2 == 0:
            self.motif_memory.add_motif(self.note_history)
            self.train_markov([phoneme] * min(32, len(self.note_history)), self.note_history[-32:])

        # End-of-phrase: preserve an idea for the next phrase and create a clean reset.
        if cadence or phoneme in "。！？":
            self.phrases.append(int(round(self.last_note)))
            self._phrase_start = True
            self._active_motif = None
            self._motif_index = 0
            self.phrase_len = 0

        absolute_note = float(root_midi) + float(self.last_note)
        return max(0.0, min(127.0, absolute_note))

    def get_intensity(self, note_height, phrase_progress):
        height = float(note_height)
        base = 78 + int(min(18, abs(height - self._phrase_register) * 0.6))
        if phrase_progress > 0.82:
            base += 8
        if phrase_progress < 0.12:
            base -= 3
        return max(50, min(120, base))


__all__ = ["MelodyBrain", "NoteMarkov", "MotifMemory"]
