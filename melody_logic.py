# melody_logic.py
import random

import numpy as np

from constants import VOWEL_CHARS, CONSONANT_CHARS
from intone_utils import get_intone_settings
from scales import SCALES


class NoteMarkov:
    def __init__(self, order=1):
        self.order = order
        self.transitions = {}

    def train(self, notes, stresses):
        for i in range(len(notes) - self.order):
            state = tuple(notes[i : i + self.order])
            stress = stresses[i + self.order]
            next_note = notes[i + self.order]
            key = (state, stress)
            if key not in self.transitions:
                self.transitions[key] = np.zeros(12)
            self.transitions[key][next_note] += 1
        self._normalize()

    def _normalize(self):
        for key in self.transitions:
            total = self.transitions[key].sum()
            if total > 0:
                self.transitions[key] /= total

    def next_note(self, state, stress, scale):
        key = (tuple(state[-self.order :]), stress)
        if key in self.transitions:
            probs = self.transitions[key].copy()
            # Bias to scale
            probs[~np.isin(np.arange(12), scale)] *= 0.1
            probs /= probs.sum()
            return np.random.choice(12, p=probs)
        return random.choice(scale)


class MotifMemory:
    def __init__(self, motif_length=4):
        self.motif_length = motif_length
        self.stored_motifs = []
        self.max_motifs = 5

    def add_motif(self, notes):
        if len(notes) >= self.motif_length:
            motif = notes[-self.motif_length :]
            if motif not in self.stored_motifs:
                self.stored_motifs.append(motif)
                # Keep only top 5
                if len(self.stored_motifs) > self.max_motifs:
                    self.stored_motifs.pop(0)

    def get_motif_note(self, current_note, scale, use_motif_prob=0.4):
        if (
            self.stored_motifs
            and random.random() < use_motif_prob
            and len(self.stored_motifs[-1]) > 1
        ):

            # REUSE MOTIF
            motif = self.stored_motifs[-1]
            next_in_motif = motif[1:]

            if random.random() < 0.5:
                varied_note = next_in_motif[0] + random.choice([-1, 0, 1])
                target_note = min(max(0, varied_note), 11)
            else:
                target_note = next_in_motif[0]

            # Snap to scale
            closest_scale = min(scale, key=lambda x: abs(x - target_note))
            return closest_scale

        # No motif
        melodic_notes = [0, 2, 4, 5, 7, 9]
        return random.choice(melodic_notes)

    def debug_motifs(self):
        """Stored motifs for preview"""
        if not self.stored_motifs:
            return "No motifs stored"
        return " | ".join([f"[{','.join(map(str, m))}]" for m in self.stored_motifs])


class MelodyBrain:
    _intone_cache = {}

    def __init__(self, seed=None):
        self.seed = seed or 1234
        random.seed(self.seed)
        self.last_note = 0
        self.phrases = []
        self.phrase_len = 0
        self.recent_notes = []
        self.motif_memory = MotifMemory(motif_length=4)
        self.VOWEL_CHARS = VOWEL_CHARS
        self.CONSONANT_CHARS = CONSONANT_CHARS
        self.word_morae = []
        self.word_pos = 0
        self.pitch_drop_pos = 0
        self.is_high_pitch = False
        self.prev_high_pitch = False
        self.markov = NoteMarkov(order=1)

    def train_markov(self, phonemes, notes=None):
        if notes is None:
            notes = self.recent_notes[-20:]
        stresses = [1 if p in self.VOWEL_CHARS else 0 for p in phonemes[-20:]]
        if len(notes) > 2:
            self.markov.train(notes, stresses)

    def set_accent_pattern(self, pattern, word_length):
        self.word_morae = list(range(word_length))
        self.word_pos = 0
        if pattern == "Heiban":
            self.pitch_drop_pos = 999
            self.is_high_pitch = True
        elif pattern == "Atamadaka":
            self.pitch_drop_pos = 1
            self.is_high_pitch = True
        elif pattern == "Nakadaka":
            self.pitch_drop_pos = max(2, word_length // 2)
            self.is_high_pitch = True
        elif pattern == "Odaka":
            self.pitch_drop_pos = 999
            self.is_high_pitch = False

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
        self.phrase_len += 1
        settings = get_intone_settings(intone_level)
        is_vowel = phoneme in "あいうえお"
        is_stretch = phoneme == "+"
        phrase_pos = (self.phrase_len - 1) / max(12, settings["phrase"])
        contour_curve = contour_bias / 100.0
        contour_target = (
            phrase_pos + contour_curve * phrase_pos * (1 - phrase_pos)
        ) * pitch_range

        stress = 1 if is_vowel else 0
        self.train_markov([phoneme], [self.last_note])

        if intone_level not in self._intone_cache:
            self._intone_cache[intone_level] = get_intone_settings(intone_level)
        settings = self._intone_cache[intone_level]

        if self.phrase_len > settings["phrase"] or phoneme in "。！？":
            self.phrases.append(self.last_note)
            self.last_note = min(max(0, int(contour_target * 0.8)), 11)
            target_note = self.last_note
            self.phrase_len = 1
        else:
            state = [self.last_note]
            markov_note = self.markov.next_note(state, stress, scale)

            if use_motifs:
                motif_note = self.motif_memory.get_motif_note(self.last_note, scale)
                target_note = (
                    markov_note * 0.5 + motif_note * 0.3 + contour_target * 0.2
                )
            else:
                if is_vowel:
                    high_notes = scale[-3:]
                    target_note = (
                        markov_note * 0.6
                        + random.choice([4, 7] + high_notes) * 0.3
                        + contour_target * 0.1
                    )
                elif is_stretch:
                    target_note = markov_note * 0.8 + self.last_note * 0.2
                else:
                    cons_notes = [0, 2, 4, 7]
                    if settings["leap"] > 2:
                        cons_notes.extend([9, 11])
                    target_note = (
                        markov_note * 0.7
                        + random.choice(cons_notes) * 0.2
                        + contour_target * 0.1
                    )

            if chord_mode:
                beat_pos = (self.phrase_len - 1) % 8
                chord_root = {0: 0, 3: 5, 5: 7}.get(beat_pos // 3 % 3, 0)
                chord_tones = [(chord_root + i) % 12 for i in [0, 4, 7]]
                chord_tones = [n for n in chord_tones if n in scale]
                if chord_tones:
                    target_note = min(chord_tones, key=lambda x: abs(x - target_note))

        # ACCENT BLEND
        if accent != "None":
            accent_factor = 1.5
            if self.is_high_pitch:
                accent_note = target_note + accent_factor
            else:
                accent_note = target_note - accent_factor
            target_note = target_note * 0.7 + accent_note * 0.3

        self.word_pos += 1
        if self.word_pos >= self.pitch_drop_pos:
            self.is_high_pitch = False
        if phoneme in "。！？。," or self.word_pos >= len(self.word_morae):
            self.word_pos = 0
            self.is_high_pitch = False

        self.recent_notes.append(self.last_note)
        if len(self.recent_notes) > 8:
            self.recent_notes.pop(0)
            self.motif_memory.add_motif(self.recent_notes)

        max_leap = settings["leap"]
        motion = max(-max_leap, min(max_leap, target_note - self.last_note))
        new_note = self.last_note + motion
        closest_scale_note = min(scale, key=lambda x: abs(x - new_note))
        self.last_note = closest_scale_note

        if quarter_tone and random.random() < 0.3 and is_vowel:
            self.last_note += random.choice([0, 0.5, -0.5])
        if flat_mode:
            self.last_note = 5
        self.prev_high_pitch = self.is_high_pitch
        return root_midi + self.last_note

    def get_intensity(self, note_height, phrase_progress):
        base = 80 + int(abs(note_height - 5) * 8)
        if phrase_progress > 0.8:
            base += 15
        return max(50, min(120, base))
