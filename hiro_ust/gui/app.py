# src/hiro_ust/gui/app.py
import os
import os.path
import random
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# ===== REPLACE ALL IMPORTS (lines 11-19) =====
from hiro_ust.core.generator import (
    USTWriter,
    HiroUSTGenerator,
    text_to_ustx,
    parse_song_structure,
    create_stretch_notes,
    get_note_length,
    get_random_note,
)

try:
    from hiro_ust.ustx_writer import USTXWriter

    USTX_AVAILABLE = True
except ImportError:
    USTX_AVAILABLE = False

from hiro_ust.utils.config import HiroConfig
from hiro_ust.constants import VOWEL_CHARS, CONSONANT_CHARS
from hiro_ust.utils.phonemizer import Phonemizer
from hiro_ust.utils.envelopes import ENVELOPE_PRESETS  # Your envelopes.py ✓
from hiro_ust.data.hiragana_map import HIRAGANA_MAP
from hiro_ust.utils.intone_utils import get_intone_settings
from hiro_ust.utils.kana_to_hiragana import convert_lyrics
from hiro_ust.data.key_roots import KEY_ROOTS
from hiro_ust.core.brain import MelodyBrain  # melody_logic → brain.py
from hiro_ust.data.mora_trie_data import MORA_DATA
from hiro_ust.utils.presets import (
    build_preset_from_app,
    apply_preset_to_app,
    save_preset_to_file,
    load_preset_from_file,
)
from hiro_ust.data.scales import SCALES

from hiro_ust.ust_strings import (
    UST_HEADER_TEMPLATE,
    REST_NOTE_TEMPLATE,
    SMALL_TSU_TEMPLATE,
    NOTE_BLOCK_TEMPLATE,
    TRACK_END,
)


# GUI
class USTGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hiro UST v4.2")
        self.root.geometry("900x800")
        self.root.minsize(850, 850)

        try:
            if getattr(sys, "frozen", False):
                # running from EXE
                icon_path = os.path.join(sys._MEIPASS, "hibiki.ico")
            else:
                # running from .py
                icon_path = os.path.join(os.path.dirname(__file__), "hibiki.ico")

            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        # =============== MAIN LYRICS ===============
        input_frame = ttk.LabelFrame(
            root, text="🎵 Song Lyrics (Romaji/Hiragana/Katakana)", padding=12
        )
        input_frame.pack(fill="both", expand=True, padx=15, pady=(15, 10))

        self.lyrics_text = scrolledtext.ScrolledText(
            input_frame, height=10, font=("Consolas", 10)
        )
        self.lyrics_text.pack(fill="both", expand=True, pady=(0, 12))
        self.lyrics_text.insert(
            "1.0",
            """[Verse 1]
きゃっきゃ うれし いたい さぶり
ゆびさき きりさけ あかい つゆ

[Chorus]
いたみ いたみ きもちいい""",
        )

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
        ttk.Label(tempo_frame, text="ticks/note", font=("TkDefaultFont", 8)).pack(
            side="right"
        )

        ttk.Label(timing_panel, text="Base Length:").pack(anchor="w")
        base_frame = ttk.Frame(timing_panel)
        base_frame.pack(fill="x", pady=(0, 8))
        self.length_var = tk.StringVar(value="240")
        ttk.Entry(base_frame, textvariable=self.length_var, width=12).pack(side="left")
        ttk.Label(base_frame, text="ticks", font=("TkDefaultFont", 8)).pack(
            side="right"
        )

        pause_frame = ttk.Frame(timing_panel)
        pause_frame.pack(fill="x", pady=(0, 8))

        line_row = ttk.Frame(pause_frame)
        line_row.pack(fill="x", pady=10)

        ttk.Label(line_row, text="Line:").pack(side="left")
        self.line_pause_var = tk.StringVar(value="960")
        ttk.Entry(line_row, textvariable=self.line_pause_var, width=10).pack(
            side="left", padx=(5, 15)
        )
        ttk.Label(line_row, text="ticks", font=("TkDefaultFont", 8)).pack(side="right")

        sect_row = ttk.Frame(pause_frame)
        sect_row.pack(fill="x")
        ttk.Label(sect_row, text="Sect:").pack(side="left")
        self.section_pause_var = tk.StringVar(value="1920")
        ttk.Entry(sect_row, textvariable=self.section_pause_var, width=10).pack(
            side="left", padx=(5, 15)
        )
        ttk.Label(sect_row, text="ticks", font=("TkDefaultFont", 8)).pack(side="right")

        # Panel 2: Voice & Length (Left-Center)
        voice_panel = ttk.LabelFrame(
            controls_main, text="🎤 Voice & Length", padding=10
        )
        voice_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ttk.Label(voice_panel, text="Voice:").pack(anchor="w")
        self.voice_var = ttk.Combobox(
            voice_panel, values=list(KEY_ROOTS.keys()), state="readonly", width=15
        )
        self.voice_var.set("Alto")
        self.voice_var.pack(fill="x", pady=(0, 8))

        ttk.Label(voice_panel, text="Scale:").pack(anchor="w")
        self.scale_var = ttk.Combobox(
            voice_panel, values=list(SCALES.keys()), state="readonly", width=15
        )
        self.scale_var.set("Major Pentatonic")
        self.scale_var.pack(fill="x", pady=(0, 8))

        length_frame = ttk.Frame(voice_panel)
        length_frame.pack(fill="x")
        ttk.Label(length_frame, text="Len Var:").pack(side="left")
        self.length_var_ctrl = tk.StringVar(value="0.3")
        ttk.Entry(length_frame, textvariable=self.length_var_ctrl, width=8).pack(
            side="left", padx=(5, 15)
        )
        ttk.Label(length_frame, text="Stretch:").pack(side="left")
        self.stretch_var = tk.StringVar(value="0.25")
        ttk.Entry(length_frame, textvariable=self.stretch_var, width=8).pack(
            side="left", padx=5
        )

        # Panel 3: Melody Modes (Center)
        melody_panel = ttk.LabelFrame(controls_main, text="🎵 Melody Modes", padding=10)
        melody_panel.pack(side="left", fill="y", padx=(0, 8))

        self.motif_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            melody_panel, text="🎼 Motif Memory", variable=self.motif_var
        ).pack(anchor="w", pady=2)

        self.lyrical_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            melody_panel, text="🎭 Lyrical Mode", variable=self.lyrical_mode_var
        ).pack(anchor="w", pady=2)

        self.flat_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            melody_panel, text="🎹 Monotone (Flat)", variable=self.flat_var
        ).pack(anchor="w", pady=2)

        self.quartertone_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            melody_panel, text="♯ Microtones (Qt)", variable=self.quartertone_var
        ).pack(anchor="w", pady=2)

        self.chord_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            melody_panel, text="🎸 I-IV-V Chords", variable=self.chord_var
        ).pack(anchor="w", pady=2)

        ttk.Label(melody_panel, text="Intone:").pack(anchor="w", pady=(8, 0))
        self.intone_var = ttk.Combobox(
            melody_panel,
            values=["Tight (1)", "Medium (2)", "Wide (3)", "Wild (5)"],
            state="readonly",
            width=15,
        )
        self.intone_var.set("Medium (2)")
        self.intone_var.pack(fill="x")

        # ACCENT
        ttk.Label(melody_panel, text="Accent:").pack(anchor="w")
        self.accent_var = ttk.Combobox(
            melody_panel,
            values=["None", "Heiban", "Atamadaka", "Nakadaka", "Odaka"],
            state="readonly",
            width=15,
        )
        self.accent_var.set("None")
        self.accent_var.pack(fill="x", pady=(0, 8))

        # CONTOUR CONTROLS
        ttk.Label(melody_panel, text="Curve:").pack(anchor="w")
        self.contour_var = tk.StringVar(value="0")
        ttk.Scale(
            melody_panel,
            from_=-50,
            to=50,
            orient="horizontal",
            variable=self.contour_var,
            length=100,
        ).pack(fill="x", pady=(0, 2))

        ttk.Label(melody_panel, text="Range:").pack(anchor="w")
        self.range_var = tk.StringVar(value="70")
        ttk.Scale(
            melody_panel,
            from_=40,
            to=120,
            orient="horizontal",
            variable=self.range_var,
            length=100,
        ).pack(fill="x", pady=(0, 8))

        ttk.Label(voice_panel, text="Phoneme:").pack(anchor="w")
        self.phoneme_mode_var = ttk.Combobox(
            voice_panel,
            values=["Japanese", "Hepburn", "Wapuro", "English"],
            state="readonly",
            width=15,
        )
        self.phoneme_mode_var.set("Japanese")
        self.phoneme_mode_var.pack(fill="x", pady=(0, 8))

        # Panel 4: UST + Output (COMBINED)
        output_panel = ttk.LabelFrame(controls_main, text="⚙️ UST/Output", padding=6)
        output_panel.pack(side="right", fill="both", expand=True)

        # Compact UST controls
        ust_frame = ttk.Frame(output_panel)
        ust_frame.pack(fill="x", pady=2)

        # Pre + Ovl
        ttk.Label(ust_frame, text="P:").grid(row=0, column=0, sticky="w")
        self.pre_utter_var = tk.StringVar(value="25")
        ttk.Entry(ust_frame, textvariable=self.pre_utter_var, width=4).grid(
            row=0, column=1, padx=1
        )

        ttk.Label(ust_frame, text="O:").grid(row=0, column=2, sticky="w")
        self.voice_overlap_var = tk.StringVar(value="10")
        ttk.Entry(ust_frame, textvariable=self.voice_overlap_var, width=4).grid(
            row=0, column=3, padx=1
        )

        # Int + Env
        ttk.Label(ust_frame, text="I:").grid(row=0, column=4, sticky="w")
        self.intensity_base_var = tk.StringVar(value="80")
        ttk.Entry(ust_frame, textvariable=self.intensity_base_var, width=4).grid(
            row=0, column=5, padx=1
        )

        ttk.Label(ust_frame, text="E:").grid(row=0, column=6, sticky="w")
        self.envelope_var = tk.StringVar(value="Pop")
        env_presets = [
            "Pop",
            "Rock",
            "Breathy",
            "Sharp",
            "Opera",
            "Whisper",
            "Belt",
            "Falsetto",
            "Growl",
            "Vibrato",
        ]
        self.env_combo = ttk.Combobox(
            ust_frame,
            textvariable=self.envelope_var,
            values=env_presets,
            state="readonly",
            width=6,
        )
        self.env_combo.grid(row=0, column=7, padx=1)

        # SEED CONTROL
        ttk.Label(ust_frame, text="S:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.seed_var = tk.StringVar(value="1234")
        ttk.Entry(ust_frame, textvariable=self.seed_var, width=8).grid(
            row=1, column=1, padx=1
        )

        # Randomize seed button
        ttk.Button(ust_frame, text="🎲", width=3, command=self.randomize_seed).grid(
            row=1, column=2, padx=(2, 0), pady=(5, 0)
        )

        # Project + Buttons
        ttk.Label(output_panel, text="Proj:").pack(anchor="w")
        self.project_var = tk.StringVar(value="Hiro_Main")
        ttk.Entry(output_panel, textvariable=self.project_var).pack(
            fill="x", pady=(0, 6)
        )
        if USTX_AVAILABLE:
            self.ustx_mode_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                output_panel, text="🌟 USTX Mode", variable=self.ustx_mode_var
            ).pack(anchor="w", pady=2)

        btn_frame = ttk.Frame(output_panel)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="🎵 Gen", command=self.generate_ust).pack(
            fill="x", pady=1
        )
        ttk.Button(btn_frame, text="💾 Save", command=self.save_ust_only).pack(
            fill="x", pady=1
        )
        ttk.Button(btn_frame, text="📋 Prev", command=self.preview_phonemes).pack(
            fill="x", pady=1
        )
        ttk.Button(btn_frame, text="🧹 Clear", command=self.clear).pack(
            fill="x", pady=1
        )

        ttk.Button(btn_frame, text="💾 Preset", command=self.save_preset).pack(
            fill="x", pady=1
        )
        ttk.Button(btn_frame, text="📂 Load", command=self.load_preset).pack(
            fill="x", pady=1
        )

        # Status + Preview
        status_frame = ttk.Frame(root)
        status_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.status_var = tk.StringVar(value="✅ Ready - All controls visible!")
        status_entry = tk.Entry(
            status_frame,
            textvariable=self.status_var,
            state="readonly",
            font=("Consolas", 9),
            relief="sunken",
            bd=1,
            bg="white",
        )
        status_entry.pack(fill="x", ipady=4)

        preview_frame = ttk.LabelFrame(root, text="👀 Preview", padding=8)
        preview_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame, height=6, state="disabled", font=("Consolas", 9)
        )
        self.preview_text.pack(fill="both", expand=True)

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

    def randomize_seed(self):
        new_seed = random.randint(0, 2**31 - 1)
        self.seed_var.set(str(new_seed))
        self.status_var.set(f"🎲 New seed: {new_seed}")

    def _get_envelope_preset(self, preset_name):
        return ENVELOPE_PRESETS.get(preset_name, HiroConfig.DEFAULT_ENVELOPE)

    def validate_inputs(self):
        errors = []

        # NUMERIC FIELDS
        try:
            tempo = float(self.tempo_var.get())
            if not HiroConfig.MIN_TEMPO <= tempo <= HiroConfig.MAX_TEMPO:
                errors.append(
                    f"Tempo: {HiroConfig.MIN_TEMPO}-{HiroConfig.MAX_TEMPO} BPM"
                )
        except:
            errors.append("Tempo: Enter number")

        try:
            length = int(self.length_var.get())
            if not HiroConfig.MIN_NOTE_LEN <= length <= HiroConfig.MAX_NOTE_LEN:
                errors.append(
                    f"Base Length: {HiroConfig.MIN_NOTE_LEN}-{HiroConfig.MAX_NOTE_LEN} ticks"
                )
        except:
            errors.append("Base Length: Enter number")

        for field, minv, maxv, name in [
            (
                self.line_pause_var,
                HiroConfig.MIN_LINE_PAUSE,
                HiroConfig.MAX_LINE_PAUSE,
                "Line Pause",
            ),
            (
                self.section_pause_var,
                HiroConfig.MIN_SECTION_PAUSE,
                HiroConfig.MAX_SECTION_PAUSE,
                "Section Pause",
            ),
            (
                self.length_var_ctrl,
                HiroConfig.MIN_LENGTH_VAR,
                HiroConfig.MAX_LENGTH_VAR,
                "Len Var",
            ),
            (
                self.stretch_var,
                HiroConfig.MIN_STRETCH,
                HiroConfig.MAX_STRETCH,
                "Stretch",
            ),
            (
                self.pre_utter_var,
                HiroConfig.MIN_PRE_UTTER,
                HiroConfig.MAX_PRE_UTTER,
                "PreUtterance",
            ),
            (
                self.voice_overlap_var,
                HiroConfig.MIN_VOICE_OVERLAP,
                HiroConfig.MAX_VOICE_OVERLAP,
                "Voice Overlap",
            ),
            (
                self.intensity_base_var,
                HiroConfig.MIN_INTENSITY,
                HiroConfig.MAX_INTENSITY,
                "Intensity",
            ),
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
            melodybrain = MelodyBrain(seed=int(self.seed_var.get()))
            lyrics = self.lyrics_text.get("1.0", tk.END).strip()

            phonemizer = Phonemizer()
            mode_map = {
                "Japanese": "japanese",
                "Hepburn": "hepburn",
                "Wapuro": "wapuro",
                "English": "english",
            }
            phonemizer.set_mode(mode_map[self.phoneme_mode_var.get()])

            parts, elements = parse_song_structure(
                lyrics,
                int(self.line_pause_var.get()),
                int(self.section_pause_var.get()),
                on_warning=lambda msg: self.status_var.set(msg),
                phonemizer=phonemizer,
            )

            self.status_var.set(f"✅ Parsed {len(elements)} elements ✓")

            root_key = KEY_ROOTS[self.voice_var.get()]

            if USTX_AVAILABLE and self.ustx_mode_var.get():

                writer = USTXWriter(self.project_var.get(), float(self.tempo_var.get()))

                ust_content = text_to_ustx(
                    elements,
                    str(self.project_var.get()),
                    float(self.tempo_var.get()),
                    int(self.length_var.get()),
                    root_key,
                    self.scale_var.get(),
                    self.intone_var.get(),
                    float(self.length_var_ctrl.get()),
                    float(self.stretch_var.get()),
                    melodybrain,
                    int(self.pre_utter_var.get()),
                    int(self.voice_overlap_var.get()),
                    int(self.intensity_base_var.get()),
                    self._get_envelope_preset(self.envelope_var.get()),
                    self.flat_var.get(),
                    self.quartertone_var.get(),
                    self.lyrical_mode_var.get(),
                    self.motif_var.get(),
                    self.chord_var.get(),
                    contour_bias=float(self.contour_var.get()),
                    pitch_range=float(self.range_var.get()),
                    accent=self.accent_var.get(),
                )
            else:
                # UST MODE
                generator = HiroUSTGenerator()

                writer = USTWriter(
                    project_name=self.project_var.get(),
                    tempo=float(self.tempo_var.get()),
                )

                pbs = "0;0"
                pbw = "0"
                flags = "g0B0H0P86"
                word_phonemes = []
                word_start = True

                for element in elements:
                    if element.startswith("PAUSE_WORD:"):
                        pause_length = int(element.split(":")[1])
                        writer.add_rest(pause_length)
                        continue

                    if element.startswith("PAUSE_LINE:"):
                        melodybrain.phrase_len = 0
                        melodybrain.recent_notes.clear()
                        pause_length = int(element.split(":")[1])
                        num_rests = pause_length // HiroConfig.PAUSE_LINE_UNIT
                        for _ in range(num_rests):
                            writer.add_rest(HiroConfig.PAUSE_LINE_UNIT)
                        continue

                    if element.startswith("PAUSE_SECTION:"):
                        melodybrain.phrase_len = 0
                        melodybrain.recent_notes.clear()
                        pause_length = int(element.split(":")[1])
                        num_rests = pause_length // HiroConfig.PAUSE_SECTION_UNIT
                        for _ in range(num_rests):
                            writer.add_rest(HiroConfig.PAUSE_SECTION_UNIT)
                        continue

                    romaji_phoneme = element
                    if romaji_phoneme == "っ":
                        writer.add_small_tsu(root_key, length=60)
                        continue

                    hiragana_phoneme = generator.romaji_to_hiragana(romaji_phoneme)
                    generator = HiroUSTGenerator()
                    stretch_notes = create_stretch_notes(
                        hiragana_phoneme, float(self.stretch_var.get()), 3, melodybrain
                    )

                    if self.accent_var.get() != "None" and romaji_phoneme not in [
                        "っ",
                        "+",
                    ]:
                        if word_start or romaji_phoneme in [" ", "　", "、", "，"]:
                            if word_phonemes:
                                word_length = len(word_phonemes)
                                melodybrain.set_accent_pattern(
                                    self.accent_var.get(), max(2, word_length)
                                )
                            word_phonemes = []
                            word_start = False
                        word_phonemes.append(romaji_phoneme)
                    else:
                        word_start = True

                    for stretch_phoneme, length_factor in stretch_notes:
                        note_length = get_note_length(
                            stretch_phoneme,
                            int(self.length_var.get()),
                            float(self.length_var_ctrl.get()),
                            length_factor,
                            melodybrain,
                        )

                        if self.lyrical_mode_var.get():
                            note_num = melodybrain.get_smart_note(
                                root_key,
                                self.scale_var.get(),
                                stretch_phoneme,
                                self.intone_var.get(),
                                self.flat_var.get(),
                                self.quartertone_var.get(),
                                self.motif_var.get(),
                                self.chord_var.get(),
                                float(self.contour_var.get()),
                                float(self.range_var.get()),
                                accent=self.accent_var.get(),
                            )
                        else:
                            note_num = get_random_note(
                                root_key,
                                self.scale_var.get(),
                                flat_mode=self.flat_var.get(),
                                quarter_tone=self.quartertone_var.get(),
                            )

                        intensity = int(self.intensity_base_var.get())
                        envelope = self._get_envelope_preset(self.envelope_var.get())

                        writer.add_note(
                            length=note_length,
                            lyric=stretch_phoneme,
                            note_num=note_num,
                            pre_utter=int(self.pre_utter_var.get()),
                            voice_overlap=int(self.voice_overlap_var.get()),
                            intensity=intensity,
                            envelope=envelope,
                            pbs=pbs,
                            pbw=pbw,
                            flags=flags,
                        )

                ust_content = writer.finalize()

            return ust_content
        except Exception as e:
            self.status_var.set(f"⚠️ Rare error: {str(e)[:60]}")
            return None

    def generate_ust(self):
        """Generate + Auto-save NEXT TO EXE"""
        ust_content = self._generate_content()
        if not ust_content:
            return

        if getattr(sys, "frozen", False):
            save_dir = os.path.dirname(sys.executable)  # EXE folder
        else:
            save_dir = os.path.dirname(os.path.abspath(__file__))  # Script folder

        ext = ".ustx" if USTX_AVAILABLE and self.ustx_mode_var.get() else ".ust"
        filename = os.path.join(
            save_dir, f"{self.project_var.get().replace(' ', '_')}{ext}"
        )

        try:
            with open(filename, "w", encoding="utf-8-sig") as f:
                f.write(ust_content)
            self.status_var.set(f"✅ Saved {os.path.basename(filename)}!")

            self.preview_text.config(state="normal")
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", f"✅ USTX Ready:\n\n{ust_content[:600]}...")
            self.preview_text.config(state="disabled")
        except Exception as e:
            self.status_var.set(f"❌ Save failed: {str(e)}")

        accent = self.accent_var.get()

    def save_ust_only(self):
        ust_content = self._generate_content()
        if not ust_content:
            return

        if getattr(sys, "frozen", False):
            initial_dir = sys._MEIPASS
        else:
            initial_dir = os.path.dirname(os.path.abspath(__file__))

        default_name = f"{self.project_var.get()}.ustx"

        filename = filedialog.asksaveasfilename(
            defaultextension=(
                ".ust" if not (USTX_AVAILABLE and self.ustx_mode_var.get()) else ".ustx"
            ),
            initialfile=(
                f"{self.project_var.get()}.ust"
                if not (USTX_AVAILABLE and self.ustx_mode_var.get())
                else f"{self.project_var.get()}.ustx"
            ),
            filetypes=[
                ("UST files", "*.ust"),
                ("USTX files", "*.ustx"),
                ("All files", "*.*"),
            ],
            initialdir=initial_dir,
            title=f"Save USTX as...",
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8-sig") as f:
                    f.write(ust_content)
                self.status_var.set(f"✅ Saved {os.path.basename(filename)}")
            except Exception as e:
                self.status_var.set(f"❌ Save failed: {str(e)}")

    def preview_phonemes(self):
        lyrics = self.lyrics_text.get("1.0", tk.END).strip()
        if not lyrics:
            self.status_var.set("❌ No lyrics to preview")
            return

        phonemizer = Phonemizer()
        mode_map = {
            "Japanese": "japanese",
            "Hepburn": "hepburn",
            "Wapuro": "wapuro",
            "English": "english",
        }
        phonemizer.set_mode(mode_map[self.phoneme_mode_var.get()])

        # Parse with phonemizer
        parts, elements = parse_song_structure(
            lyrics,
            int(self.line_pause_var.get()),
            int(self.section_pause_var.get()),
            phonemizer=phonemizer,
            on_warning=lambda msg: self.status_var.set(msg),
        )

        preview = f"🔤 {self.phoneme_mode_var.get()} Mode (first 30):\n\n"
        non_pause_count = 0

        for i, elem in enumerate(elements[:30]):
            if elem.startswith("PAUSE"):
                pause_len = elem.split(":")[1]
                preview += f"{i:2d}: [PAUSE {pause_len} ticks]\n"
            else:
                generator = HiroUSTGenerator()
                hiragana = generator.romaji_to_hiragana(elem)
                preview += f"{i:2d}: '{elem}' → {hiragana}\n"
                non_pause_count += 1

        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", preview)
        self.preview_text.config(state="disabled")

        self.status_var.set(
            f"✅ {self.phoneme_mode_var.get()}: {non_pause_count} phonemes"
        )

    def clear(self):
        self.lyrics_text.delete("1.0", tk.END)

        # Clear preview only
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.config(state="disabled")

        self.status_var.set("🧹 Lyrics cleared ✓")

    def save_preset(self):
        preset = build_preset_from_app(self)
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Preset", "*.json")],
            initialfile=f"{self.project_var.get()}_preset.json",
        )
        if filename:
            try:
                save_preset_to_file(preset, filename)
                self.status_var.set(f"✅ Preset saved: {os.path.basename(filename)}")
            except Exception as e:
                self.status_var.set(f"❌ Preset save failed: {str(e)[:50]}")

    def load_preset(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON Preset", "*.json"), ("All files", "*.*")],
            title="Load Preset",
        )
        if not filename:
            return
        try:
            preset = load_preset_from_file(filename)
            apply_preset_to_app(self, preset)
            self.status_var.set(f"✅ Loaded: {os.path.basename(filename)}")
        except Exception as e:
            self.status_var.set(f"❌ Load failed: {str(e)[:50]}")


# ===== ADD TO BOTTOM OF generator.py =====
import random  # Add if missing


def create_stretch_notes(phoneme, stretch_prob=0.25, max_stretch=3, brain=None):
    """Create stretched vowel notes for natural singing"""
    vowel_chars = (
        brain.VOWEL_CHARS
        if brain
        else ["あ", "い", "う", "え", "お", "a", "i", "u", "e", "o"]
    )

    # Double vowels → long vowel
    if len(phoneme) >= 2 and phoneme[0] == phoneme[1] and phoneme[0] in vowel_chars:
        return [(phoneme[0], 1.8)]

    # Single vowel stretch
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
    """Calculate realistic note lengths"""
    if phoneme == "+":
        length = int(base_length * 0.6 * length_factor)
        return max(120, min(480, length))

    phoneme_char = phoneme[0] if len(phoneme) > 0 else "a"
    vowel_chars = ["あ", "い", "う", "え", "お", "a", "i", "u", "e", "o"]

    if phoneme_char in vowel_chars:
        factor = 1.0 + random.uniform(-length_var, length_var * 0.3)
    else:
        factor = 0.7 + random.uniform(-length_var * 0.2, length_var * 0.2)

    length = int(base_length * factor * length_factor)
    return max(120, min(1920, length))


def get_random_note(root_midi, scale_name, flat_mode=False, quarter_tone=False):
    """Simple random note from scale"""
    from hiro_ust.data.scales import SCALES

    scale = SCALES[scale_name]

    if flat_mode:
        return root_midi + 5

    note = random.choice(scale)
    if quarter_tone and random.random() < 0.3:
        note += random.choice([0, 0.5, -0.5])

    return root_midi + note


if __name__ == "__main__":
    root = tk.Tk()
    app = USTGeneratorApp(root)
    root.mainloop()
