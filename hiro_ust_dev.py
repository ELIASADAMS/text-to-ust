import logging
import os
import random
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog

# IMPORT DATA MODULES
from constants import VOWEL_CHARS, CONSONANT_CHARS
from hiragana_map import HIRAGANA_MAP
from kana_to_hiragana import convert_lyrics
from key_roots import KEY_ROOTS
from mora_trie_data import MORA_DATA
from scales import SCALES

logger = logging.getLogger(__name__)


#   FIRST CLASS
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
                    node[char] = {'end': False, 'phones': None}
                node = node[char]
            node['end'] = True
            node['phones'] = phones

    def romaji_to_hiragana(self, phoneme):
        if phoneme.startswith('kk') or phoneme.startswith('gg'):
            return self.hiragana_map.get(phoneme, phoneme)
        if phoneme in ['ji', 'zu']:
            return self.hiragana_map.get(f'ji_s', phoneme)
        if phoneme == 'ji_t':
            return self.hiragana_map.get('ji_t', phoneme)
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

                if 'end' in node and node['end']:
                    best_match = node
                    best_end = i

            if best_match and best_match['end']:
                phonemes.extend(best_match['phones'])
                i = best_end
            else:
                char = text[start]
                if char == 'っ':  # Sokuon - gemination
                    phonemes.append('っ')
                    i = start + 1
                else:
                    i = start + 1

        return phonemes


def create_stretch_notes(phoneme, stretch_prob=0.25, max_stretch=3, brain=None):
    vowel_chars = brain.VOWEL_CHARS if brain else VOWEL_CHARS

    # DOUBLE VOWELS ("aa", "ii")
    if len(phoneme) >= 2 and phoneme[0] == phoneme[1] and phoneme[0] in vowel_chars:
        return [(phoneme[0], 1.8)]  # Long vowel

    # SINGLE VOWEL STRETCH
    if (len(phoneme) == 1 and phoneme in vowel_chars and
            random.random() < (stretch_prob + 0.5)):
        stretches = random.randint(1, max_stretch)
        return [(phoneme, 1.2)] + [('+', 0.6)] * stretches

    return [(phoneme, 1.0)]


def parse_song_structure(
        text,
        line_pause=960,
        section_pause=1920,
        on_warning=None
):
    parts = {"Main": []}
    current_part = "Main"
    all_elements = []

    if not text or not text.strip():
        return parts, all_elements

    lines = text.strip().split('\n')

    for line_num, raw_line in enumerate(lines, 1):
        line = raw_line.strip()

        if line.startswith('[') and line.endswith(']') and len(line) > 2:
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

        elif line:
            try:
                generator = HiroUSTGenerator()
                clean_line = line.replace(' ', '')
                phonemes = generator.hiragana_to_romaji(line)
                if phonemes:
                    parts[current_part].append(line)
                    all_elements.extend(phonemes)
                    all_elements.append(f"PAUSE_LINE:{line_pause}")
                else:
                    msg = f"⚠️ Skipped invalid line {line_num}: '{line[:20]}...'"
                    if on_warning:
                        on_warning(msg)
            except Exception as e:
                msg = f"⚠️ Parse error line {line_num}: '{line}' → {e}"
                if on_warning:
                    on_warning(msg)
                continue

    if all_elements and all_elements[-1].startswith("PAUSE_LINE"):
        all_elements.pop()

    if not all_elements:
        all_elements = ["PAUSE_LINE:480"]

    return parts, all_elements


class MotifMemory:
    def __init__(self, motif_length=4):
        self.motif_length = motif_length
        self.stored_motifs = []
        self.max_motifs = 5

    def add_motif(self, notes):
        if len(notes) >= self.motif_length:
            motif = notes[-self.motif_length:]
            # Avoid duplicate
            if motif not in self.stored_motifs:
                self.stored_motifs.append(motif)
                # Keep only top 5
                if len(self.stored_motifs) > self.max_motifs:
                    self.stored_motifs.pop(0)

    def get_motif_note(self, current_note, scale, use_motif_prob=0.4):
        if (self.stored_motifs and
                random.random() < use_motif_prob and
                len(self.stored_motifs[-1]) > 1):

            # REUSE MOTIF WITH VARIATION
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

        # No motif: regular
        melodic_notes = [0, 2, 4, 5, 7, 9]
        return random.choice(melodic_notes)

    def debug_motifs(self):
        """Stored motifs for preview"""
        if not self.stored_motifs:
            return "No motifs stored"
        return " | ".join([f"[{','.join(map(str, m))}]" for m in self.stored_motifs])


class MelodyBrain:
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

    def get_smart_note(self, root_midi, scale_name, phoneme, intone_level="Tight (1)",
                       flat_mode=False, quarter_tone=False, use_motifs=True, chord_mode=False,
                       contour_bias=0, pitch_range=70):
        scale = SCALES[scale_name]
        self.phrase_len += 1
        settings = self._get_intone_settings(intone_level)

        is_vowel = phoneme in 'あいうえお'
        is_stretch = phoneme == '+'

        # CONTOUR CONTROL (NEW!)
        phrase_pos = (self.phrase_len - 1) / max(12, settings["phrase"])
        contour_curve = contour_bias / 100.0  # -0.5 to +0.5
        contour_target = (phrase_pos + contour_curve * phrase_pos * (1 - phrase_pos)) * pitch_range

        # Store recent notes for motif detection
        self.recent_notes.append(self.last_note)
        if len(self.recent_notes) > 8:
            self.recent_notes.pop(0)
            self.motif_memory.add_motif(self.recent_notes)

        # PHRASE ENDINGS + CONTOUR
        if self.phrase_len > settings["phrase"] or phoneme in '。！？':
            self.phrases.append(self.last_note)
            self.last_note = min(max(0, int(contour_target * 0.8)), 11)
            self.phrase_len = 1
            target_note = self.last_note
        else:
            if use_motifs:
                motif_note = self.motif_memory.get_motif_note(self.last_note, scale)
                target_note = motif_note * 0.6 + contour_target * 0.4
            else:
                if is_vowel:
                    high_notes = scale[-3:]
                    target_note = random.choice([4, 7] + high_notes) + contour_target * 0.1
                elif is_stretch:
                    target_note = self.last_note
                else:
                    cons_notes = [0, 2, 4, 7]
                    if settings["leap"] > 2: cons_notes.extend([9, 11])
                    target_note = random.choice(cons_notes) + contour_target * 0.1

            # CHORD PROGRESSION
            if chord_mode:
                beat_pos = (self.phrase_len - 1) % 8
                chord_root = {0: 0, 3: 5, 5: 7}.get(beat_pos // 3 % 3, 0)  # I-IV-V cycle
                chord_tones = [(chord_root + i) % 12 for i in [0, 4, 7]]
                chord_tones = [n for n in chord_tones if n in scale]
                if chord_tones:
                    target_note = min(chord_tones, key=lambda x: abs(x - target_note))

        # Voice leading + snap to scale
        max_leap = settings["leap"]
        motion = max(-max_leap, min(max_leap, target_note - self.last_note))
        new_note = self.last_note + motion
        closest_scale_note = min(scale, key=lambda x: abs(x - new_note))
        self.last_note = closest_scale_note

        if quarter_tone and random.random() < 0.3 and is_vowel:
            self.last_note += random.choice([0, 0.5, -0.5])
        if flat_mode:
            self.last_note = 5

        return root_midi + self.last_note

    def _get_intone_settings(self, intone_level):
        return {
            "Tight (1)": {"leap": 1, "phrase": 6},
            "Medium (2)": {"leap": 2, "phrase": 8},
            "Wide (3)": {"leap": 3, "phrase": 10},
            "Wild (5)": {"leap": 5, "phrase": 12}
        }.get(intone_level, {"leap": 1, "phrase": 6})

    def get_intensity(self, note_height, phrase_progress):
        base = 80 + int(abs(note_height - 5) * 8)
        if phrase_progress > 0.8:
            base += 15
        return max(50, min(120, base))


def get_note_length(phoneme, base_length=480, length_var=0.3, length_factor=1.0, brain=None):
    if phoneme == '+':
        return int(base_length * 0.6 * length_factor)

    phoneme_char = phoneme[0] if len(phoneme) > 0 else 'a'
    if brain:
        vowel_chars = getattr(brain, 'VOWEL_CHARS', VOWEL_CHARS)
        consonant_chars = getattr(brain, 'CONSONANT_CHARS', CONSONANT_CHARS)
    else:
        vowel_chars = VOWEL_CHARS
        consonant_chars = CONSONANT_CHARS

    if phoneme_char in vowel_chars:
        factor = 1.0 + random.uniform(-length_var, length_var * 0.3)
    elif phoneme_char in consonant_chars:
        factor = 0.5 + random.uniform(0, length_var * 1.5)
    else:
        factor = 0.7 + random.uniform(-length_var * 0.2, length_var * 0.2)
    return max(120, int(base_length * factor * length_factor))


def text_to_ust(text_elements, project_name, tempo, base_length, root_key, scale,
                intone_level, length_var, stretch_prob, melody_brain,
                pre_utterance=25, voice_overlap=10, intensity_base=80, envelope="0,10,35,0,100,100,0",
                flat_mode=False, quartertone_mode=False, lyrical_mode=True, use_motifs=True, chord_mode=False,
                contour_bias=0, pitch_range=70):
    generator = HiroUSTGenerator()
    project_name = str(project_name)

    ust = f'''[#VERSION]
UST Version1.2
[#SETTING]
Tempo={tempo}
Tracks=1
ProjectName={project_name}
VoiceDir=%VOICE%
OutFile=
CacheDir=.cache
Tool1=wavtool.exe
Tool2=resampler.exe
Mode2=True
'''

    note_id = 0
    for element in text_elements:
        if element.startswith("PAUSE_LINE:"):
            melody_brain.phrase_len = 0
            melody_brain.recent_notes.clear()
            pause_length = int(element.split(":")[1])
            num_rests = pause_length // 240
            for _ in range(num_rests):
                ust += f'\n[#{note_id:04d}]\nLength=240\nLyric=R\nNoteNum=60\n'
                ust += 'PreUtterance=0\nVoiceOverlap=0\nIntensity=0\nModulation=0\nPBS=0\n'
                ust += 'PBW=0\nStartPoint=0\nEnvelope=0,0,0,0,0,0,0\n'
                note_id += 1
            continue

        if element.startswith("PAUSE_SECTION:"):
            melody_brain.phrase_len = 0
            melody_brain.recent_notes.clear()
            pause_length = int(element.split(":")[1])
            num_rests = pause_length // 480
            for _ in range(num_rests):
                ust += f'\n[#{note_id:04d}]\nLength=480\nLyric=R\nNoteNum=60\n'
                ust += 'PreUtterance=0\nVoiceOverlap=0\nIntensity=0\nModulation=0\nPBS=0\n'
                ust += 'PBW=0\nStartPoint=0\nEnvelope=0,0,0,0,0,0,0\n'
                note_id += 1
            continue

        else:
            romaji_phoneme = element
            if romaji_phoneme == 'っ':
                note_length = 60
                ust += f'\n[#{note_id:04d}]\nLength={note_length}\nLyric=っ\nNoteNum={int(root_key)}\n'
                ust += f'PreUtterance=0\nVoiceOverlap=0\nIntensity=30\n'
                ust += f'Modulation=0\nPBS=0\nPBW=0\nStartPoint=0\nEnvelope=0,0,0,0,0,0,0\n'
                note_id += 1
                continue

            hiragana_phoneme = generator.romaji_to_hiragana(romaji_phoneme)
            stretch_notes = create_stretch_notes(hiragana_phoneme, stretch_prob, 3, melody_brain)

            for stretch_phoneme, length_factor in stretch_notes:
                note_length = get_note_length(stretch_phoneme, base_length, length_var, length_factor, melody_brain)

                if lyrical_mode:
                    note_num = melody_brain.get_smart_note(
                        root_key, scale, stretch_phoneme, intone_level,
                        flat_mode, quartertone_mode, use_motifs, chord_mode,
                        contour_bias, pitch_range)
                else:
                    note_num = get_random_note(root_key, scale, flat_mode=flat_mode, quartertone_mode=quartertone_mode)

                ust += f'\n[#{note_id:04d}]\n'
                ust += f'Length={note_length}\n'
                ust += f'Lyric={stretch_phoneme}\n'
                note_num_safe = int(round(note_num))
                # QUARTER-TONE
                if quartertone_mode and note_num != int(note_num):
                    fraction = note_num - int(note_num)
                    pbs = int(fraction * 50)
                    ust += f'PBS={pbs}\nPBW=10\n'
                else:
                    ust += f'PBS=0\nPBW=0\n'
                ust += f'NoteNum={note_num_safe}\n'
                ust += f'PreUtterance={pre_utterance}\nVoiceOverlap={voice_overlap}\n'
                phrase_progress = getattr(melody_brain, 'phrase_len', 0) / 12.0
                last_note_safe = getattr(melody_brain, 'last_note', 0)
                base_intensity = intensity_base
                melody_offset = melody_brain.get_intensity(last_note_safe, phrase_progress)
                intensity = max(50, min(120, base_intensity + (melody_offset - 80)))
                ust += f'Intensity={max(50, min(120, intensity))}\n'
                ust += f'StartPoint=0\nEnvelope={envelope}\n'
                note_id += 1

    ust += '\n[#TRACKEND]\n'
    return ust


def get_random_note(root_midi, scale_name, intone_level="Tight (1)", flat_mode=False,
                    quarter_tone=False, use_motifs=True, chord_mode=False):
    scale = SCALES[scale_name]
    if flat_mode:
        return root_midi + 0

    base_semitone = random.choice(scale)
    if quarter_tone and random.random() < 0.5:
        base_semitone += random.choice([0, 0.5, -0.5])
    return root_midi + base_semitone


# GUI
class USTGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hiro UST v4.2 dev")
        self.root.geometry("900x800")
        self.root.minsize(850, 850)

        try:
            if getattr(sys, 'frozen', False):
                # PyInstaller EXE
                icon_path = os.path.join(sys._MEIPASS, 'hibiki.ico')
            else:
                icon_path = 'hibiki.ico'

            self.root.iconbitmap(icon_path)
            logger.info(f"Logo loaded: {icon_path}")
        except:
            logger.warning("hibiki.ico not found - using default")

        # =============== MAIN LYRICS ===============
        input_frame = ttk.LabelFrame(root, text="🎵 Song Lyrics (Romaji/Hiragana)", padding=12)
        input_frame.pack(fill="both", expand=True, padx=15, pady=(15, 10))

        self.lyrics_text = scrolledtext.ScrolledText(input_frame, height=10, font=("Consolas", 10))
        self.lyrics_text.pack(fill="both", expand=True, pady=(0, 12))
        self.lyrics_text.insert("1.0", """[Verse 1]
きゃっきゃ うれし いたい さぶり
ゆびさき きりさけ あかい つゆ

[Chorus]
いたみ いたみ きもちいい""")

        # =============== CONTROLS GRID ===============
        controls_main = ttk.Frame(root)
        controls_main.pack(fill="x", padx=15, pady=(0, 10))

        # Panel 1: Timing (Left)
        timing_panel = ttk.LabelFrame(controls_main, text="⏱️ Timing", padding=10)
        timing_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ttk.Label(timing_panel, text="Tempo (BPM):").pack(anchor="w")
        tempo_frame = ttk.Frame(timing_panel)
        tempo_frame.pack(fill="x", pady=(0, 8))
        self.tempo_var = tk.StringVar(value="120.00")
        ttk.Entry(tempo_frame, textvariable=self.tempo_var, width=12).pack(side="left")
        ttk.Label(tempo_frame, text="ticks/note", font=("TkDefaultFont", 8)).pack(side="right")

        ttk.Label(timing_panel, text="Base Length:").pack(anchor="w")
        base_frame = ttk.Frame(timing_panel)
        base_frame.pack(fill="x", pady=(0, 8))
        self.length_var = tk.StringVar(value="240")
        ttk.Entry(base_frame, textvariable=self.length_var, width=12).pack(side="left")
        ttk.Label(base_frame, text="ticks", font=("TkDefaultFont", 8)).pack(side="right")

        pause_frame = ttk.Frame(timing_panel)
        pause_frame.pack(fill="x", pady=(0, 8))

        line_row = ttk.Frame(pause_frame)
        line_row.pack(fill="x", pady=10)

        ttk.Label(line_row, text="Line:").pack(side="left")
        self.line_pause_var = tk.StringVar(value="960")
        ttk.Entry(line_row, textvariable=self.line_pause_var, width=10).pack(side="left", padx=(5, 15))
        ttk.Label(line_row, text="ticks", font=("TkDefaultFont", 8)).pack(side="right")

        sect_row = ttk.Frame(pause_frame)
        sect_row.pack(fill="x")
        ttk.Label(sect_row, text="Sect:").pack(side="left")
        self.section_pause_var = tk.StringVar(value="1920")
        ttk.Entry(sect_row, textvariable=self.section_pause_var, width=10).pack(side="left", padx=(5, 15))
        ttk.Label(sect_row, text="ticks", font=("TkDefaultFont", 8)).pack(side="right")

        # Panel 2: Voice & Length (Left-Center)
        voice_panel = ttk.LabelFrame(controls_main, text="🎤 Voice & Length", padding=10)
        voice_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ttk.Label(voice_panel, text="Voice:").pack(anchor="w")
        self.voice_var = ttk.Combobox(voice_panel, values=list(KEY_ROOTS.keys()), state="readonly", width=15)
        self.voice_var.set("Alto")
        self.voice_var.pack(fill="x", pady=(0, 8))

        ttk.Label(voice_panel, text="Scale:").pack(anchor="w")
        self.scale_var = ttk.Combobox(voice_panel, values=list(SCALES.keys()), state="readonly", width=15)
        self.scale_var.set("Major Pentatonic")
        self.scale_var.pack(fill="x", pady=(0, 8))

        length_frame = ttk.Frame(voice_panel)
        length_frame.pack(fill="x")
        ttk.Label(length_frame, text="Len Var:").pack(side="left")
        self.length_var_ctrl = tk.StringVar(value="0.3")
        ttk.Entry(length_frame, textvariable=self.length_var_ctrl, width=8).pack(side="left", padx=(5, 15))
        ttk.Label(length_frame, text="Stretch:").pack(side="left")
        self.stretch_var = tk.StringVar(value="0.25")
        ttk.Entry(length_frame, textvariable=self.stretch_var, width=8).pack(side="left", padx=5)

        # Panel 3: Melody Modes (Center)
        melody_panel = ttk.LabelFrame(controls_main, text="🎵 Melody Modes", padding=10)
        melody_panel.pack(side="left", fill="y", padx=(0, 8))

        self.motif_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(melody_panel, text="🎼 Motif Memory", variable=self.motif_var).pack(anchor="w", pady=2)

        self.lyrical_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(melody_panel, text="🎭 Lyrical Mode", variable=self.lyrical_mode_var).pack(anchor="w", pady=2)

        self.flat_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(melody_panel, text="🎹 Monotone (Flat)", variable=self.flat_var).pack(anchor="w", pady=2)

        self.quartertone_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(melody_panel, text="♯ Microtones (Qt)", variable=self.quartertone_var).pack(anchor="w", pady=2)

        self.chord_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(melody_panel, text="🎸 I-IV-V Chords", variable=self.chord_var).pack(anchor="w", pady=2)

        ttk.Label(melody_panel, text="Intone:").pack(anchor="w", pady=(8, 0))
        self.intone_var = ttk.Combobox(melody_panel, values=["Tight (1)", "Medium (2)", "Wide (3)", "Wild (5)"],
                                       state="readonly", width=15)
        self.intone_var.set("Medium (2)")
        self.intone_var.pack(fill="x")

        # CONTOUR CONTROLS
        ttk.Label(melody_panel, text="Curve:").pack(anchor="w")
        self.contour_var = tk.StringVar(value="0")
        ttk.Scale(melody_panel, from_=-50, to=50, orient="horizontal",
                  variable=self.contour_var, length=100).pack(fill="x", pady=(0, 2))  # ← 100px

        ttk.Label(melody_panel, text="Range:").pack(anchor="w")
        self.range_var = tk.StringVar(value="70")
        ttk.Scale(melody_panel, from_=40, to=120, orient="horizontal",
                  variable=self.range_var, length=100).pack(fill="x", pady=(0, 8))  # ← 100px

        # Panel 4: UST + Output (COMBINED)
        output_panel = ttk.LabelFrame(controls_main, text="⚙️ UST/Output", padding=6)
        output_panel.pack(side="right", fill="both", expand=True)

        # Compact UST controls
        ust_frame = ttk.Frame(output_panel)
        ust_frame.pack(fill="x", pady=2)

        # Pre + Ovl
        ttk.Label(ust_frame, text="P:").grid(row=0, column=0, sticky="w")
        self.pre_utter_var = tk.StringVar(value="25")
        ttk.Entry(ust_frame, textvariable=self.pre_utter_var, width=4).grid(row=0, column=1, padx=1)

        ttk.Label(ust_frame, text="O:").grid(row=0, column=2, sticky="w")
        self.voice_overlap_var = tk.StringVar(value="10")
        ttk.Entry(ust_frame, textvariable=self.voice_overlap_var, width=4).grid(row=0, column=3, padx=1)

        # Int + Env
        ttk.Label(ust_frame, text="I:").grid(row=0, column=4, sticky="w")
        self.intensity_base_var = tk.StringVar(value="80")
        ttk.Entry(ust_frame, textvariable=self.intensity_base_var, width=4).grid(row=0, column=5, padx=1)

        ttk.Label(ust_frame, text="E:").grid(row=0, column=6, sticky="w")
        self.envelope_var = tk.StringVar(value="Pop")
        env_presets = ["Pop", "Rock", "Breathy", "Sharp", "Opera", "Whisper", "Belt", "Falsetto", "Growl", "Vibrato"]
        self.env_combo = ttk.Combobox(ust_frame, textvariable=self.envelope_var,
                                      values=env_presets, state="readonly", width=6)
        self.env_combo.grid(row=0, column=7, padx=1)

        # SEED CONTROL
        ttk.Label(ust_frame, text="S:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.seed_var = tk.StringVar(value="1234")
        ttk.Entry(ust_frame, textvariable=self.seed_var, width=8).grid(row=1, column=1, padx=1)

        # Project + Buttons
        ttk.Label(output_panel, text="Proj:").pack(anchor="w")
        self.project_var = tk.StringVar(value="Hiro_Main")
        ttk.Entry(output_panel, textvariable=self.project_var).pack(fill="x", pady=(0, 6))

        btn_frame = ttk.Frame(output_panel)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="🎵 Gen", command=self.generate_ust).pack(fill="x", pady=1)
        ttk.Button(btn_frame, text="💾 Save", command=self.save_ust_only).pack(fill="x", pady=1)
        ttk.Button(btn_frame, text="📋 Prev", command=self.preview_phonemes).pack(fill="x", pady=1)
        ttk.Button(btn_frame, text="🧹 Clear", command=self.clear).pack(fill="x", pady=1)

        ttk.Button(btn_frame, text="💾 Preset", command=self.save_preset).pack(fill="x", pady=1)
        ttk.Button(btn_frame, text="📂 Load", command=self.load_preset).pack(fill="x", pady=1)

        # Status + Preview
        status_frame = ttk.Frame(root)
        status_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.status_var = tk.StringVar(value="✅ Ready - All controls visible!")
        ttk.Label(status_frame, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x")

        preview_frame = ttk.LabelFrame(root, text="👀 Preview", padding=8)
        preview_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=6, state="disabled", font=("Consolas", 9))
        self.preview_text.pack(fill="both", expand=True)

        # LOG
        try:
            from logger import TesterLogger
            self.logger = TesterLogger(self)
            self.logger.setup()
        except:
            print("No logger")

    def _get_envelope_preset(self, preset_name):
        presets = {
            "Pop": "0,10,35,0,100,100,0",
            "Rock": "0,20,50,0,90,80,0",
            "Breathy": "0,5,20,0,70,100,0",
            "Sharp": "0,30,70,0,100,50,0",
            "Opera": "0,5,15,0,100,95,0",
            "Whisper": "0,2,10,0,60,100,0",
            "Belt": "0,25,60,0,100,70,0",
            "Falsetto": "0,8,25,0,80,100,0",
            "Growl": "0,40,70,0,85,60,0",
            "Vibrato": "0,15,40,20,100,80,0"
        }
        return presets.get(preset_name, "0,10,35,0,100,100,0")

    def validate_inputs(self):
        errors = []

        # NUMERIC FIELDS
        try:
            tempo = float(self.tempo_var.get())
            if not 60 <= tempo <= 240:
                errors.append("Tempo: 60-240 BPM")
        except:
            errors.append("Tempo: Enter number")

        try:
            length = int(self.length_var.get())
            if not 120 <= length <= 1920:
                errors.append("Base Length: 120-1920 ticks")
        except:
            errors.append("Base Length: Enter number")

        for field, minv, maxv, name in [
            (self.line_pause_var, 240, 5000, "Line Pause"),
            (self.section_pause_var, 480, 10000, "Section Pause"),
            (self.length_var_ctrl, 0.0, 1.0, "Len Var"),
            (self.stretch_var, 0.0, 1.0, "Stretch"),
            (self.pre_utter_var, 0, 200, "PreUtterance"),
            (self.voice_overlap_var, 0, 100, "Voice Overlap"),
            (self.intensity_base_var, 30, 150, "Intensity")
        ]:
            try:
                val = float(field.get())
                if not minv <= val <= maxv:
                    errors.append(f"{name}: {minv}-{maxv}")
            except:
                errors.append(f"{name}: Enter number")

        # COMBOBOXES
        if self.voice_var.get() not in KEY_ROOTS:
            errors.append("Voice: Select from dropdown")
        if self.scale_var.get() not in SCALES:
            errors.append("Scale: Select from dropdown")

        # LYRICS
        lyrics = self.lyrics_text.get("1.0", tk.END).strip()
        if not lyrics or len(lyrics) < 10:
            errors.append("Lyrics: Add some text")

        return errors

    def _generate_content(self):
        # VALIDATE
        errors = self.validate_inputs()
        if errors:
            self.status_var.set(f"❌ Fix: {' | '.join(errors)}")
            return None

        try:
            melody_brain = MelodyBrain(seed=int(self.seed_var.get()))
            lyrics = self.lyrics_text.get("1.0", tk.END).strip()

            parts, elements = parse_song_structure(lyrics)
            self.status_var.set(f"✅ Parsed {len(elements)} elements ✓")
            phonemes_only = [e for e in elements if not e.startswith('PAUSE')]
            self.logger.log_phonemes(phonemes_only)
            self.logger.log_sections(parts)

            root_key = KEY_ROOTS[self.voice_var.get()]
            ust_content = text_to_ust(
                elements, str(self.project_var.get()), float(self.tempo_var.get()),
                int(self.length_var.get()), root_key, self.scale_var.get(),
                self.intone_var.get(), float(self.length_var_ctrl.get()),
                float(self.stretch_var.get()), melody_brain,
                int(self.pre_utter_var.get()), int(self.voice_overlap_var.get()),
                int(self.intensity_base_var.get()),
                self._get_envelope_preset(self.envelope_var.get()),
                self.flat_var.get(), self.quartertone_var.get(),
                self.lyrical_mode_var.get(), self.motif_var.get(),
                self.chord_var.get(),
                contour_bias=float(self.contour_var.get()),
                pitch_range=float(self.range_var.get())
            )
            return ust_content
        except Exception as e:
            self.status_var.set(f"⚠️ Rare error: {str(e)[:60]}")
            return None

            logger.info(f"Generated UST with seed={self.seed_var.get()}, {len(elements)} phonemes")
            return ust_content

    def generate_ust(self):
        """Generate + Auto-save NEXT TO EXE"""
        ust_content = self._generate_content()
        if not ust_content:
            self.logger.show_stats()
            return

        # Save NEXT TO EXE
        if getattr(sys, 'frozen', False):
            save_dir = os.path.dirname(sys.executable)  # EXE folder
        else:
            save_dir = os.path.dirname(os.path.abspath(__file__))  # Script folder

        filename = os.path.join(save_dir, f"{self.project_var.get().replace(' ', '_')}.ust")

        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(ust_content)
            self.status_var.set(f"✅ Saved {os.path.basename(filename)}!")

            self.preview_text.config(state="normal")
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", f"✅ UST Ready:\n\n{ust_content[:600]}...")
            self.preview_text.config(state="disabled")
        except Exception as e:
            self.status_var.set(f"❌ Save failed: {str(e)}")

    def save_ust_only(self):
        ust_content = self._generate_content()
        if not ust_content:
            return

        if getattr(sys, 'frozen', False):
            initial_dir = sys._MEIPASS
        else:
            initial_dir = os.path.dirname(os.path.abspath(__file__))

        default_name = f"{self.project_var.get()}.ust"

        filename = filedialog.asksaveasfilename(
            defaultextension=".ust",
            filetypes=[("UST files", "*.ust"), ("All files", "*.*")],
            initialfile=default_name,
            initialdir=initial_dir,
            title=f"Save UST as..."
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8-sig') as f:
                    f.write(ust_content)
                self.status_var.set(f"✅ Saved {os.path.basename(filename)}")
            except Exception as e:
                self.status_var.set(f"❌ Save failed: {str(e)}")

    def preview_phonemes(self):
        lyrics = self.lyrics_text.get("1.0", tk.END).strip()
        if not lyrics:
            self.status_var.set("❌ No lyrics to preview")
            return

        parts, elements = parse_song_structure(lyrics)
        preview = "Phoneme Breakdown (first 25):\n\n"

        for i, elem in enumerate(elements[:25]):
            if elem.startswith('PAUSE'):
                preview += f"{i:2d}: [PAUSE {elem.split(':')[1]}ms]\n"
            else:
                generator = HiroUSTGenerator()
                hiragana = generator.romaji_to_hiragana(elem)
                preview += f"{i:2d}: {elem:8} → {hiragana}\n"

        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", preview)
        self.preview_text.config(state="disabled")
        self.status_var.set(f"✅ Previewed {len([e for e in elements if not e.startswith('PAUSE')])} phonemes")

    def clear(self):
        self.lyrics_text.delete("1.0", tk.END)

        # Clear preview only
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.config(state="disabled")

        self.status_var.set("🧹 Lyrics cleared ✓")

    def save_preset(self):
        preset = {
            'tempo': self.tempo_var.get(),
            'length': self.length_var.get(),
            'voice': self.voice_var.get(),
            'scale': self.scale_var.get(),
            'intone': self.intone_var.get(),
            'length_var': self.length_var_ctrl.get(),
            'stretch': self.stretch_var.get(),
            'pre_utterance': self.pre_utter_var.get(),
            'voice_overlap': self.voice_overlap_var.get(),
            'intensity': self.intensity_base_var.get(),
            'motif': self.motif_var.get(),
            'lyrical': self.lyrical_mode_var.get(),
            'flat': self.flat_var.get(),
            'quartertone': self.quartertone_var.get(),
            'project': self.project_var.get(),
            'line_pause': self.line_pause_var.get(),
            'section_pause': self.section_pause_var.get(),
            'envelope': self.envelope_var.get()
        }
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Preset", "*.json")],
            initialfile=f"{self.project_var.get()}_preset.json"
        )
        if filename:
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(preset, f, indent=2, ensure_ascii=False)
            self.status_var.set(f"✅ Preset saved: {os.path.basename(filename)}")

    def load_preset(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON Preset", "*.json"), ("All files", "*.*")],
            title="Load Preset"
        )
        if not filename:
            return

        try:
            import json
            with open(filename, 'r', encoding='utf-8') as f:
                preset = json.load(f)

            # Set ALL controls
            var_map = {
                'tempo': self.tempo_var,
                'length': self.length_var,
                'voice': self.voice_var,
                'scale': self.scale_var,
                'intone': self.intone_var,
                'length_var': self.length_var_ctrl,
                'stretch': self.stretch_var,
                'pre_utterance': self.pre_utter_var,
                'voice_overlap': self.voice_overlap_var,
                'intensity': self.intensity_base_var,
                'project': self.project_var,
                'line_pause': self.line_pause_var,
                'section_pause': self.section_pause_var,
                'envelope': self.envelope_var
            }

            for key, var in var_map.items():
                if key in preset:
                    var.set(str(preset[key]))

            # Boolean checkboxes
            for checkbox, key in [
                (self.motif_var, 'motif'),
                (self.lyrical_mode_var, 'lyrical'),
                (self.flat_var, 'flat'),
                (self.quartertone_var, 'quartertone')
            ]:
                if key in preset:
                    checkbox.set(bool(preset[key]))

            self.status_var.set(f"✅ Loaded: {os.path.basename(filename)}")

        except Exception as e:
            self.status_var.set(f"❌ Load failed: {str(e)[:50]}")


if __name__ == "__main__":
    root = tk.Tk()
    app = USTGeneratorApp(root)
    root.mainloop()
