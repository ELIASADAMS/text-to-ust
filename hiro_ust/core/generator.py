# src/hiro_ust/core/generator.py
"""Core UST generation logic - no GUI dependencies"""
try:
    from hiro_ust.ustx_writer import USTXWriter

    USTX_AVAILABLE = True
except ImportError:
    USTX_AVAILABLE = False

# IMPORT MODULES
from hiro_ust.constants import VOWEL_CHARS, CONSONANT_CHARS
from hiro_ust.data.hiragana_map import HIRAGANA_MAP
from hiro_ust.data.mora_trie_data import MORA_DATA
from hiro_ust.data.scales import SCALES
from hiro_ust.ust_strings import (
    UST_HEADER_TEMPLATE,
    REST_NOTE_TEMPLATE,
    SMALL_TSU_TEMPLATE,
    NOTE_BLOCK_TEMPLATE,
    TRACK_END,
)
from hiro_ust.utils.config import HiroConfig
from hiro_ust.utils.intone_utils import get_intone_settings
from hiro_ust.utils.kana_to_hiragana import convert_lyrics

from hiro_ust.utils.phonemizer import Phonemizer
from hiro_ust.constants import VOWEL_CHARS, CONSONANT_CHARS
from hiro_ust.ust_strings import UST_HEADER_TEMPLATE, REST_NOTE_TEMPLATE
from hiro_ust.utils.intone_utils import get_intone_settings

import random


# === CUT THESE CLASSES/FUNCTIONS FROM hiro_ust_dev.py ===
class USTWriter:
    def __init__(self, project_name, tempo):
        self.lines = []
        self.note_id = 0
        self.project_name = str(project_name)
        self.tempo = tempo
        self._write_header()

    def _write_header(self):
        self.lines.append(
            UST_HEADER_TEMPLATE.format(tempo=self.tempo, project_name=self.project_name)
        )

    def add_rest(self, length):
        self.lines.append(
            REST_NOTE_TEMPLATE.format(note_id=self.note_id, length=length)
        )
        self.note_id += 1

    def add_small_tsu(self, root_key, length=60):
        self.lines.append(
            SMALL_TSU_TEMPLATE.format(
                note_id=self.note_id, length=length, root_key=int(root_key)
            )
        )
        self.note_id += 1

    def add_note(
        self,
        length,
        lyric,
        note_num,
        pre_utter,
        voice_overlap,
        intensity,
        envelope,
        pbs=0,
        pbw=0,
        flags="",
    ):
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

    def finalize(self):
        self.lines.append(TRACK_END)
        return "\n".join(self.lines)


class HiroUSTGenerator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.hiragana_map = HIRAGANA_MAP
            cls._instance._build_mora_trie()
        return cls._instance

    def _build_mora_trie(self):
        self.mora_trie = {}
        for mora, phones in MORA_DATA.items():
            node = self.mora_trie
            for char in mora:
                if char not in node:
                    node[char] = {"end": False, "phones": None}
                node = node[char]
            node["end"] = True
            node["phones"] = phones

    def romaji_to_hiragana(self, phoneme):
        if phoneme.startswith("kk") or phoneme.startswith("gg"):
            return self.hiragana_map.get(phoneme, phoneme)
        if phoneme in ["ji", "zu"]:
            return self.hiragana_map.get(f"ji_s", phoneme)
        if phoneme == "ji_t":
            return self.hiragana_map.get("ji_t", phoneme)
        return self.hiragana_map.get(phoneme, phoneme)

    def hiragana_to_romaji(self, text):
        phonemes = []
        i = 0
        text = text.strip()

        text = convert_lyrics(text)

        while i < len(text):
            node = self.mora_trie
            start = i
            best_match = None
            best_end = i

            while i < len(text) and text[i] in node:
                node = node[text[i]]
                i += 1

                if "end" in node and node["end"]:
                    best_match = node
                    best_end = i

            if best_match and best_match["end"]:
                phonemes.extend(best_match["phones"])
                i = best_end
            else:
                char = text[start]
                if char == "っ":  # Sokuon
                    phonemes.append("っ")
                    i = start + 1
                else:
                    i = start + 1

        return phonemes


def parse_song_structure(
    text, line_pause=960, section_pause=1920, on_warning=None, phonemizer=None
):
    parts = {"Main": []}
    current_part = "Main"
    all_elements = []

    if not text or not text.strip():
        return parts, all_elements

    lines = text.strip().split("\n")

    for line_num, raw_line in enumerate(lines, 1):
        line = raw_line.strip()

        if line.startswith("[") and line.endswith("]") and len(line) > 2:
            section_name = line[1:-1].strip()
            if section_name:
                if all_elements:
                    all_elements.append(f"PAUSE_SECTION:{section_pause}")
                current_part = section_name
                parts[current_part] = []
            else:
                msg = f"⚠️ Empty section '[]' on line {line_num} - using 'Main'"
                if on_warning:
                    on_warning(msg)
            continue

        elif line:
            try:
                # SPLIT LINE INTO WORDS
                words = line.split()

                for word_idx, word in enumerate(words):
                    if phonemizer:
                        phonemes = phonemizer.text_to_phonemes(word)
                    else:
                        generator = HiroUSTGenerator()
                        phonemes = generator.hiragana_to_romaji(word)

                    if phonemes:
                        parts[current_part].append(word)
                        all_elements.extend(phonemes)
                        if word_idx < len(words) - 1:
                            all_elements.append(f"PAUSE_WORD:120")

                all_elements.append(f"PAUSE_LINE:{line_pause}")

            except Exception as e:
                msg = f"⚠️ Parse error line {line_num}: '{line}' → {e}"
                if on_warning:
                    on_warning(msg)
            continue

    if all_elements and all_elements[-1].startswith("PAUSE_LINE"):
        all_elements.pop()

    if not all_elements:
        all_elements = [f"PAUSE_LINE:{HiroConfig.PAUSE_LINE_UNIT * 2}"]

    return parts, all_elements


def text_to_ustx(
    text_elements,
    project_name,
    tempo,
    base_length,
    root_key,
    scale,
    intone_level,
    length_var,
    stretch_prob,
    melody_brain,
    pre_utterance=25,
    voice_overlap=10,
    intensity_base=80,
    envelope="0,10,35,0,100,100,0",
    flat_mode=False,
    quartertone_mode=False,
    lyrical_mode=True,
    use_motifs=True,
    chord_mode=False,
    contour_bias=0,
    pitch_range=70,
    accent="None",
):
    generator = HiroUSTGenerator()
    writer = USTXWriter(project_name=project_name, tempo=tempo)

    word_phonemes = []
    word_start = True

    for element in text_elements:
        if element.startswith("PAUSE_WORD:"):
            pause_length = int(element.split(":")[1])
            writer.add_rest(pause_length)
            continue
        if accent != "None":
            word_phonemes = []
            word_start = True
        if element.startswith("PAUSE_LINE:"):
            melody_brain.phrase_len = 0
            melody_brain.recent_notes.clear()
            pause_length = int(element.split(":")[1])
            num_rests = pause_length // HiroConfig.PAUSE_LINE_UNIT
            for _ in range(num_rests):
                writer.add_rest(HiroConfig.PAUSE_LINE_UNIT)
            continue

        if element.startswith("PAUSE_SECTION:"):
            melody_brain.phrase_len = 0
            melody_brain.recent_notes.clear()
            pause_length = int(element.split(":")[1])
            num_rests = pause_length // HiroConfig.PAUSE_SECTION_UNIT
            for _ in range(num_rests):
                writer.add_rest(HiroConfig.PAUSE_SECTION_UNIT)
            continue

        romaji_phoneme = element

        # small tsu
        if romaji_phoneme == "っ":
            writer.add_small_tsu(root_key, length=60)
            continue

        hiragana_phoneme = generator.romaji_to_hiragana(romaji_phoneme)
        # WORD BOUNDARY DETECTION + ACCENT
        if accent != "None" and romaji_phoneme not in ["っ", "+"]:
            if word_start or romaji_phoneme in [" ", "　", "、", "，"]:
                if word_phonemes:
                    word_length = len(word_phonemes)
                    melody_brain.set_accent_pattern(accent, max(2, word_length))
                word_phonemes = []
                word_start = False
            word_phonemes.append(romaji_phoneme)
        else:
            word_start = True
        stretch_notes = create_stretch_notes(
            hiragana_phoneme, stretch_prob, 3, melody_brain
        )

        if accent != "None" and len(word_phonemes) == 1:
            estimated_word_length = min(
                6, max(2, len([p for p in text_elements if p == romaji_phoneme]))
            )
            melody_brain.set_accent_pattern(accent, estimated_word_length)

        for stretch_phoneme, length_factor in stretch_notes:
            note_length = get_note_length(
                stretch_phoneme, base_length, length_var, length_factor, melody_brain
            )

            if lyrical_mode:
                note_num = melody_brain.get_smart_note(
                    root_key,
                    scale,
                    stretch_phoneme,
                    intone_level,
                    flat_mode,
                    quartertone_mode,
                    use_motifs,
                    chord_mode,
                    contour_bias,
                    pitch_range,
                    accent=accent,
                )
            else:
                note_num = get_random_note(
                    root_key, scale, flat_mode=flat_mode, quarter_tone=quartertone_mode
                )

            # QUARTERTONE + ACCENT PBS
            pbs = "0;0"
            pbw = "0"
            pby = "0"
            pbm = ","

            if quartertone_mode and note_num != int(note_num):
                fraction = note_num - int(note_num)
                bend_amount = int(fraction * 50)
                pbs = f"0;{bend_amount}"
                pbw = "10"
            elif accent != "None" and hasattr(melody_brain, "is_high_pitch"):

                if not melody_brain.is_high_pitch and melody_brain.prev_high_pitch:
                    drop_strength = random.choice([-50, -40, -35, -30, -25])
                    pbs = f"0;{drop_strength}"
                    pbw = "0"

                    if note_length > 200:
                        pbw = f"25,50,{int(note_length * 0.15)}"
                        pby = f"-15,-15,0"

                elif accent == "Odaka" and melody_brain.word_pos == 2:
                    pbs = f"0;{random.choice([25, 35, 45])}"
                    pbw = "20"

                elif melody_brain.word_pos == 1 and melody_brain.is_high_pitch:
                    pbs = f"0;{random.choice([15, 20])}"
                    pbw = "0"

            phrase_progress = getattr(melody_brain, "phrase_len", 0) / 12.0
            last_note_safe = getattr(melody_brain, "last_note", 0)
            base_intensity = intensity_base
            melody_offset = melody_brain.get_intensity(last_note_safe, phrase_progress)
            intensity = max(50, min(120, base_intensity + (melody_offset - 80)))

            flags = "g0B0H0P86"

            writer.add_note(
                length=note_length,
                lyric=stretch_phoneme,
                note_num=note_num,
                pre_utter=pre_utterance,
                voice_overlap=voice_overlap,
                intensity=intensity,
                envelope=envelope,
                pbs=pbs,
                pbw=pbw,
                flags=flags,
                bpm=tempo,
            )

    return writer.finalize()


def create_stretch_notes(phoneme, stretch_prob=0.25, max_stretch=3, brain=None):
    vowel_chars = brain.VOWEL_CHARS if brain else VOWEL_CHARS

    # DOUBLE VOWELS
    if len(phoneme) >= 2 and phoneme[0] == phoneme[1] and phoneme[0] in vowel_chars:
        return [(phoneme[0], 1.8)]  # Long vowel

    # SINGLE VOWEL STRETCH
    if (
        len(phoneme) == 1
        and phoneme in vowel_chars
        and random.random() < (stretch_prob + 0.5)
    ):
        stretches = random.randint(1, max_stretch)
        return [(phoneme, 1.2)] + [("+", 0.6)] * stretches

    return [(phoneme, 1.0)]


def get_note_length(
    phoneme, base_length=480, length_var=0.3, length_factor=1.0, brain=None
):
    if phoneme == "+":
        factor = 0.6
        length = int(base_length * factor * length_factor)
        return max(HiroConfig.MIN_NOTE_LEN, min(HiroConfig.MAX_NOTE_LEN, length))

    phoneme_char = phoneme[0] if len(phoneme) > 0 else "a"
    if brain:
        vowel_chars = getattr(brain, "VOWEL_CHARS", VOWEL_CHARS)
        consonant_chars = getattr(brain, "CONSONANT_CHARS", CONSONANT_CHARS)
    else:
        vowel_chars = VOWEL_CHARS
        consonant_chars = CONSONANT_CHARS

    if phoneme_char in vowel_chars:
        factor = 1.0 + random.uniform(-length_var, length_var * 0.3)
    elif phoneme_char in consonant_chars:
        factor = 0.5 + random.uniform(0, length_var * 1.5)
    else:
        factor = 0.7 + random.uniform(-length_var * 0.2, length_var * 0.2)

    length = int(base_length * factor * length_factor)
    return max(HiroConfig.MIN_NOTE_LEN, min(HiroConfig.MAX_NOTE_LEN, length))


def get_random_note(root_midi, scale_name, flat_mode=False, quarter_tone=False):
    scale = SCALES[scale_name]
    if flat_mode:
        return root_midi + 5
    note = random.choice(scale)
    if quarter_tone and random.random() < 0.3:
        note += random.choice([0, 0.5, -0.5])
    return root_midi + note


def get_random_note(
    root_midi,
    scale_name,
    intone_level="Tight (1)",
    flat_mode=False,
    quarter_tone=False,
    use_motifs=True,
    chord_mode=False,
):
    scale = SCALES[scale_name]
    if flat_mode:
        return root_midi + 5

    # 1. START with random/default
    base_semitone = random.choice(scale)

    # Motifs
    if use_motifs:
        if not hasattr(get_random_note, "_recent_notes"):
            get_random_note._recent_notes = []
        recent = get_random_note._recent_notes
        if len(recent) >= 2:
            motif_continue = recent[-1]
            base_semitone = min(scale, key=lambda x: abs(x - (motif_continue % 12)))
        get_random_note._recent_notes.append(base_semitone)
        if len(get_random_note._recent_notes) > 4:
            get_random_note._recent_notes = get_random_note._recent_notes[-4:]

    # Chords
    settings = get_intone_settings(intone_level)
    if chord_mode:
        chord_root = {0: 0, 3: 5, 5: 7}.get(random.randint(0, 2), 0)
        chord = [n for n in [(chord_root + i) % 12 for i in [0, 4, 7]] if n in scale]
        base_semitone = random.choice(chord or scale)

    # Leap limits
    if settings["leap"] < 3:
        base_semitone = min(base_semitone, settings["leap"] * 2)

    # Microtones
    if quarter_tone and random.random() < 0.5:
        base_semitone += random.choice([0, 0.5, -0.5])

    return root_midi + base_semitone


# MISSING FUNCTIONS - ADD TO END OF generator.py
import random


def create_stretch_notes(phoneme, stretch_prob=0.25, max_stretch=3, brain=None):
    vowel_chars = brain.VOWEL_CHARS if brain else VOWEL_CHARS
    if len(phoneme) >= 2 and phoneme[0] == phoneme[1] and phoneme[0] in vowel_chars:
        return [(phoneme[0], 1.8)]
    if (
        len(phoneme) == 1
        and phoneme in vowel_chars
        and random.random() < (stretch_prob + 0.5)
    ):
        return [(phoneme, 1.2), ("+", 0.6)]
    return [(phoneme, 1.0)]


def get_note_length(
    phoneme, base_length=480, length_var=0.3, length_factor=1.0, brain=None
):
    if phoneme == "+":
        return max(120, min(480, int(base_length * 0.6 * length_factor)))
    phoneme_char = phoneme[0] if len(phoneme) > 0 else "a"
    vowel_chars = getattr(brain, "VOWEL_CHARS", VOWEL_CHARS) if brain else VOWEL_CHARS
    if phoneme_char in vowel_chars:
        factor = 1.0 + random.uniform(-length_var, length_var * 0.3)
    else:
        factor = 0.7 + random.uniform(-length_var * 0.2, length_var * 0.2)
    length = int(base_length * factor * length_factor)
    return max(120, min(1920, length))


def get_random_note(root_midi, scale_name, flat_mode=False, quarter_tone=False):
    scale = SCALES[scale_name]
    if flat_mode:
        return root_midi + 5
    note = random.choice(scale)
    if quarter_tone and random.random() < 0.3:
        note += random.choice([0, 0.5, -0.5])
    return root_midi + note
