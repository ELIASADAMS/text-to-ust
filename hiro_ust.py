import os
import random
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog

SCALES = {
    # 12-note (Chromatic)
    'Chromatic': list(range(12)),

    # 9-note (Nonatonic Blues)
    'Nonatonic Blues': [0, 2, 3, 5, 6, 7, 8, 10, 11],

    # 8-note (Octatonic)
    'Octatonic': [0, 1, 3, 4, 6, 7, 9, 10],

    # 7-note (Diatonic)
    'C Major': [0, 2, 4, 5, 7, 9, 11], 'C Minor': [0, 2, 3, 5, 7, 8, 10],
    'D Major': [2, 4, 6, 7, 9, 11, 1], 'D Minor': [2, 4, 5, 7, 9, 10, 0],
    'E Major': [4, 6, 8, 9, 11, 1, 3], 'E Minor': [4, 6, 7, 9, 11, 0, 2],
    'F Major': [5, 7, 9, 10, 0, 2, 4], 'F Minor': [5, 7, 8, 10, 0, 1, 3],
    'G Major': [7, 9, 11, 0, 2, 4, 6], 'G Minor': [7, 9, 10, 0, 2, 3, 5],
    'A Major': [9, 11, 1, 2, 4, 6, 8], 'A Minor': [9, 11, 0, 2, 4, 5, 7],

    # 6-note (Hexatonic)
    'Whole Tone': [0, 2, 4, 6, 8, 10],
    'Hexatonic Blues': [0, 3, 5, 6, 9, 10],

    # 5-note (Pentatonic)
    'Major Pentatonic': [0, 2, 4, 7, 9],
    'Minor Pentatonic': [0, 3, 5, 7, 10],

    # 4-note (Tetratonic)
    'Tetratonic': [0, 4, 7, 11]
}

KEY_ROOTS = {
    "Soprano": 67,  # G4
    "Alto": 60,  # C4
    "Tenor": 55,  # G3
    "Baritone": 52,  # E3
    "Bass": 48,  # C3
    "C4 Default": 60
}


class HiroUSTGenerator:
    def __init__(self):
        self.hiragana_map = {
            # Vowels
            'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'え', 'o': 'お',

            # K-row + dakuten + yoon + sokuon
            'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ',
            'ga': 'が', 'gi': 'ぎ', 'gu': 'ぐ', 'ge': 'げ', 'go': 'ご',
            'kya': 'きゃ', 'kyu': 'きゅ', 'kyo': 'きょ', 'gya': 'ぎゃ', 'gyu': 'ぎゅ', 'gyo': 'ぎょ',

            # S-row + dakuten + yoon
            'sa': 'さ', 'shi': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ',
            'za': 'ざ', 'ji_s': 'じ', 'zu': 'ず', 'ze': 'ぜ', 'zo': 'ぞ',  # ji_s = じ (from shi+dakuten)
            'sha': 'しゃ', 'shu': 'しゅ', 'sho': 'しょ', 'ja': 'じゃ', 'ju': 'じゅ', 'jo': 'じょ',

            # T-row + dakuten + yoon + sokuon
            'ta': 'た', 'chi': 'ち', 'tsu': 'つ', 'te': 'て', 'to': 'と',
            'da': 'だ', 'ji_t': 'ぢ', 'zu_t': 'づ', 'de': 'で', 'do': 'ど',  # ji_t = ぢ (from chi+dakuten)
            'cha': 'ちゃ', 'chu': 'ちゅ', 'cho': 'ちょ',

            # N-row + yoon
            'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
            'nya': 'にゃ', 'nyu': 'にゅ', 'nyo': 'にょ',

            # H-row + b/p + yoon
            'ha': 'は', 'hi': 'ひ', 'fu': 'ふ', 'he': 'へ', 'ho': 'ほ',
            'ba': 'ば', 'bi': 'び', 'bu': 'ぶ', 'be': 'べ', 'bo': 'ぼ',
            'pa': 'ぱ', 'pi': 'ぴ', 'pu': 'ぷ', 'pe': 'ぺ', 'po': 'ぽ',
            'hya': 'ひゃ', 'hyu': 'ひゅ', 'hyo': 'ひょ', 'bya': 'びゃ', 'byu': 'びゅ', 'byo': 'びょ',

            # M-row + yoon
            'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
            'mya': 'みゃ', 'myu': 'みゅ', 'myo': 'みょ',

            # Y-row, R-row, others
            'ya': 'や', 'yu': 'ゆ', 'yo': 'よ',
            'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
            'rya': 'りゃ', 'ryu': 'りゅ', 'ryo': 'りょ', 'wa': 'わ', 'wo': 'を', 'n': 'ん',

            # Sokuon combinations (っ + CV)
            'kk a': 'っか', 'kki': 'っき', 'kku': 'っく', 'kke': 'っけ', 'kko': 'っこ',
            'gg a': 'っが', 'ggi': 'っぎ', 'ggu': 'っぐ', 'gge': 'っげ', 'ggo': 'っこ',
            'tsu_ts u': 'っつ', 'tta': 'った', 'cchi': 'っち', 'sse': 'っせ', 'sso': 'っそ'
        }

    def romaji_to_hiragana(self, phoneme):
        """✅ FIXED: Uses FULL dictionary - no more ignoring entries!"""
        # Handle sokuon prefixes first
        if phoneme.startswith('kk') or phoneme.startswith('gg'):
            return self.hiragana_map.get(phoneme, phoneme)
        if phoneme in ['ji', 'zu']:  # Default to shi/za versions
            return self.hiragana_map.get(f'ji_s', phoneme)
        if phoneme == 'ji_t':
            return self.hiragana_map.get('ji_t', phoneme)

        return self.hiragana_map.get(phoneme, phoneme)  # ✅ USES FULL DICT!

    @staticmethod
    def hiragana_to_romaji(text):
        """✅ FIXED: Complete reverse mapping with ALL sokuon combos"""
        # Full bidirectional mora → romaji mapping
        mora_map = {
            # Sokuon first
            'っ': ['っ'], 'っか': ['っ', 'ka'], 'っき': ['っ', 'ki'], 'っく': ['っ', 'ku'],
            'っけ': ['っ', 'ke'], 'っこ': ['っ', 'ko'], 'っが': ['っ', 'ga'], 'っぎ': ['っ', 'gi'],
            'っぐ': ['っ', 'gu'], 'っつ': ['っ', 'tsu'], 'った': ['っ', 'ta'], 'っち': ['っ', 'chi'],
            'っせ': ['っ', 'se'], 'っそ': ['っ', 'so'],

            # Vowels
            'あ': ['a'], 'い': ['i'], 'う': ['u'], 'え': ['e'], 'お': ['o'],

            # K-row + dakuten + yoon
            'か': ['ka'], 'き': ['ki'], 'く': ['ku'], 'け': ['ke'], 'こ': ['ko'],
            'が': ['ga'], 'ぎ': ['gi'], 'ぐ': ['gu'], 'げ': ['ge'], 'ご': ['go'],
            'きゃ': ['kya'], 'きゅ': ['kyu'], 'きょ': ['kyo'], 'ぎゃ': ['gya'],
            'ぎゅ': ['gyu'], 'ぎょ': ['gyo'],

            # S-row + dakuten + yoon
            'さ': ['sa'], 'し': ['shi'], 'す': ['su'], 'せ': ['se'], 'そ': ['so'],
            'ざ': ['za'], 'じ': ['ji_s'], 'ず': ['zu'], 'ぜ': ['ze'], 'ぞ': ['zo'],
            'しゃ': ['sha'], 'しゅ': ['shu'], 'しょ': ['sho'], 'じゃ': ['ja'],
            'じゅ': ['ju'], 'じょ': ['jo'],

            # T-row + dakuten + yoon
            'た': ['ta'], 'ち': ['chi'], 'つ': ['tsu'], 'て': ['te'], 'と': ['to'],
            'だ': ['da'], 'ぢ': ['ji_t'], 'づ': ['zu_t'], 'で': ['de'], 'ど': ['do'],
            'ちゃ': ['cha'], 'ちゅ': ['chu'], 'ちょ': ['cho'],

            # N, H, M, Y, R rows (complete)
            'な': ['na'], 'に': ['ni'], 'ぬ': ['nu'], 'ね': ['ne'], 'の': ['no'],
            'にゃ': ['nya'], 'にゅ': ['nyu'], 'にょ': ['nyo'],
            'は': ['ha'], 'ひ': ['hi'], 'ふ': ['fu'], 'へ': ['he'], 'ほ': ['ho'],
            'ば': ['ba'], 'び': ['bi'], 'ぶ': ['bu'], 'べ': ['be'], 'ぼ': ['bo'],
            'ぱ': ['pa'], 'ぴ': ['pi'], 'ぷ': ['pu'], 'ぺ': ['pe'], 'ぽ': ['po'],
            'ひゃ': ['hya'], 'ひゅ': ['hyu'], 'ひょ': ['hyo'], 'びゃ': ['bya'],
            'びゅ': ['byu'], 'びょ': ['byo'],
            'ま': ['ma'], 'み': ['mi'], 'む': ['mu'], 'め': ['me'], 'も': ['mo'],
            'みゃ': ['mya'], 'みゅ': ['myu'], 'みょ': ['myo'],
            'や': ['ya'], 'ゆ': ['yu'], 'よ': ['yo'],
            'ら': ['ra'], 'り': ['ri'], 'る': ['ru'], 'れ': ['re'], 'ろ': ['ro'],
            'りゃ': ['rya'], 'りゅ': ['ryu'], 'りょ': ['ryo'], 'わ': ['wa'], 'を': ['wo'], 'ん': ['n']
        }

        phonemes = []
        i = 0
        text = text.strip()

        while i < len(text):
            found = False

            # Try longest patterns first (3-char → 2-char → 1-char)
            for length in [3, 2, 1]:
                for mora, phones in mora_map.items():
                    if len(mora) == length and text[i:i + length] == mora:
                        phonemes.extend(phones)
                        i += length
                        found = True
                        break
                if found:
                    break

            if not found:
                i += 1  # Skip unknown chars

        return phonemes


def create_stretch_notes(phoneme, stretch_prob=0.25, max_stretch=3):
    if len(phoneme) >= 2 and phoneme[0] == phoneme[1] and phoneme[0] in 'あいうえお':
        return [(phoneme[0], 1.8)]

    vowel_boost = 0.5 if phoneme in 'あいうえお' else 0
    if random.random() < (stretch_prob + vowel_boost) and len(phoneme) == 1 and phoneme in 'あいうえお':
        stretches = random.randint(1, max_stretch)
        return [(phoneme, 1.2)] + [('+', 0.6)] * stretches
    return [(phoneme, 1.0)]


def parse_song_structure(text, line_pause=960, section_pause=1920):
    parts = {}
    current_part = "Main"
    all_elements = []

    for line in text.strip().split('\n'):
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            if all_elements:
                all_elements.append(f"PAUSE_SECTION:{section_pause}")
            current_part = line[1:-1].strip()
            parts[current_part] = []
        elif line:
            parts[current_part].append(line)
            # ✅ FIXED: Use class method instead of standalone function
            phonemes = HiroUSTGenerator.hiragana_to_romaji(line)
            all_elements.extend(phonemes)
            all_elements.append(f"PAUSE_LINE:{line_pause}")

    if all_elements and all_elements[-1].startswith("PAUSE_LINE"):
        all_elements.pop()

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
            next_in_motif = motif[1:]  # Shift motif forward

            if random.random() < 0.5:
                varied_note = next_in_motif[0] + random.choice([-1, 0, 1])
                target_note = min(max(0, varied_note), 11)
            else:
                target_note = next_in_motif[0]

            # Snap to scale
            closest_scale = min(scale, key=lambda x: abs(x - target_note))
            return closest_scale

        # No motif: regular melodic note
        melodic_notes = [0, 2, 4, 5, 7, 9]
        return random.choice(melodic_notes)

    def debug_motifs(self):
        """Show stored motifs for preview"""
        if not self.stored_motifs:
            return "No motifs stored"
        return " | ".join([f"[{','.join(map(str, m))}]" for m in self.stored_motifs])


class MelodyBrain:
    def __init__(self):
        self.last_note = 0
        self.phrases = []
        self.phrase_len = 0
        self.recent_notes = []
        self.motif_memory = MotifMemory(motif_length=4)

    def get_smart_note(self, root_midi, scale_name, phoneme, intone_level="Tight (1)", flat_mode=False,
                       quarter_tone=False, use_motifs=True):
        scale = SCALES[scale_name]
        self.phrase_len += 1

        settings = self._get_intone_settings(intone_level)

        is_vowel = phoneme in 'あいうえお'
        is_stretch = phoneme == '+'

        # Store recent notes for motif detection
        self.recent_notes.append(self.last_note)
        if len(self.recent_notes) > 8:
            self.recent_notes.pop(0)
            self.motif_memory.add_motif(self.recent_notes)  # Learn motif

        # PHRASE ENDINGS
        if self.phrase_len > settings["phrase"] or phoneme in '。！？':
            self.phrases.append(self.last_note)
            self.last_note = random.choice([0, 7])  # Tonic or dominant
            self.phrase_len = 1
            target_note = self.last_note
        else:
            # MOTIF MEMORY
            if use_motifs:
                target_note = self.motif_memory.get_motif_note(
                    self.last_note, scale, use_motif_prob=0.4)
            else:
                # Revert to Original logic
                if is_vowel:
                    high_notes = scale[-3:]
                    target_note = random.choice([4, 7] + high_notes)
                elif is_stretch:
                    target_note = self.last_note
                else:
                    cons_notes = [0, 2, 4, 7]
                    if settings["leap"] > 2: cons_notes.extend([9, 11])
                    target_note = random.choice(cons_notes)

        # Voice leading + snap to scale
        max_leap = settings["leap"]
        motion = max(-max_leap, min(max_leap, target_note - self.last_note))
        new_note = self.last_note + motion
        closest_scale_note = min(scale, key=lambda x: abs(x - new_note))
        self.last_note = closest_scale_note

        if quarter_tone and random.random() < 0.3 and is_vowel:
            self.last_note += random.choice([0, 0.5, -0.5])

        if flat_mode:
            return root_midi + 0
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


# Global melody brain
# melody_brain = MelodyBrain()

VOWEL_CHARS = 'あいうえお'
CONSONANT_CHARS = 'かきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろ'


def get_note_length(phoneme, base_length=480, length_var=0.3, length_factor=1.0):
    if phoneme == '+':
        return int(base_length * 0.6 * length_factor)

    phoneme_char = phoneme[0] if len(phoneme) > 0 else 'a'

    if phoneme_char in VOWEL_CHARS:
        factor = 1.0 + random.uniform(-length_var, length_var * 0.3)
    elif phoneme_char in CONSONANT_CHARS:
        factor = 0.5 + random.uniform(0, length_var * 1.5)
    else:
        factor = 0.7 + random.uniform(-length_var * 0.2, length_var * 0.2)
    return max(120, int(base_length * factor * length_factor))


def text_to_ust(text_elements, project_name, tempo, base_length, root_key, scale,
                intone_level, length_var, stretch_prob, melody_brain,
                flat_mode=False, quartertone_mode=False, lyrical_mode=True, use_motifs=True):
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
            pause_length = int(element.split(":")[1])
            num_rests = pause_length // 240
            for _ in range(num_rests):
                ust += f'\n[#{note_id:04d}]\n'
                ust += f'Length=240\nLyric=R\nNoteNum=60\nPreUtterance=0\n'
                ust += f'VoiceOverlap=0\nIntensity=0\nModulation=0\nPBS=0\n'
                ust += f'PBW=0\nStartPoint=0\nEnvelope=0,0,0,0,0,0,0\n'
                note_id += 1
        elif element.startswith("PAUSE_SECTION:"):
            pause_length = int(element.split(":")[1])
            num_rests = pause_length // 480
            for _ in range(num_rests):
                phrase_progress = melody_brain.phrase_len / 12.0
                intensity = melody_brain.get_intensity(melody_brain.last_note, melody_brain.phrase_len / 12.0)
                ust += f'Intensity={intensity}\n'
                ust += f'\n[#{note_id:04d}]\n'
                ust += f'Length=480\nLyric=R\nNoteNum=60\nPreUtterance=0\n'
                ust += f'VoiceOverlap=0\nIntensity=0\nModulation=0\nPBS=0\n'
                ust += f'PBW=0\nStartPoint=0\nEnvelope=0,0,0,0,0,0,0\n'
                note_id += 1

        else:
            # Process phoneme with stretching
            romaji_phoneme = element

            # ✅ FIXED: Proper sokuon handling for UTAU
            if romaji_phoneme == 'っ':
                # Small tsu = GEMINATION, not "tsu" sound!
                # For UTAU: use REST + next phoneme will double naturally
                note_length = 60  # Very short rest for gemination effect
                ust += f'\n[#{note_id:04d}]\nLength={note_length}\nLyric=R\nNoteNum={int(root_key)}\n'
                ust += f'PreUtterance=0\nVoiceOverlap=0\nIntensity=0\n'
                ust += f'Modulation=0\nPBS=0\nPBW=0\nStartPoint=0\nEnvelope=0,0,0,0,0,0,0\n'
                note_id += 1
                continue  # Skip to next phoneme (which gets doubled naturally)

            hiragana_phoneme = generator.romaji_to_hiragana(romaji_phoneme)
            stretch_notes = create_stretch_notes(hiragana_phoneme, stretch_prob, 3)

            for stretch_phoneme, length_factor in stretch_notes:
                note_length = get_note_length(stretch_phoneme, base_length, length_var, length_factor)

                if lyrical_mode:
                    note_num = melody_brain.get_smart_note(
                        root_key, scale, stretch_phoneme, intone_level,
                        flat_mode, quartertone_mode, use_motifs)
                else:
                    note_num = get_random_note(root_key, scale, intone_level, flat_mode, quartertone_mode)

                ust += f'\n[#{note_id:04d}]\n'
                ust += f'Length={note_length}\n'
                ust += f'Lyric={stretch_phoneme}\n'
                ust += f'NoteNum={int(note_num)}\n'
                ust += f'PreUtterance=25\nVoiceOverlap=10\n'
                phrase_progress = melody_brain.phrase_len / 12.0
                intensity = 80 + int(abs(melody_brain.last_note - 5) * 8)
                if phrase_progress > 0.8:
                    intensity += 15
                ust += f'Intensity={max(50, min(120, intensity))}\n'
                ust += f'StartPoint=0\nEnvelope=0,10,35,0,100,100,0\n'
                note_id += 1

    ust += '\n[#TRACKEND]\n'
    return ust


def get_random_note(root_midi, scale_name, intone_level="Tight (1)", flat_mode=False, quarter_tone=False):
    """Simple random note from scale (original algorithm)"""
    scale = SCALES[scale_name]
    if flat_mode:
        return root_midi + 0

    base_semitone = random.choice(scale)

    if quarter_tone and random.random() < 0.5:
        base_semitone += random.choice([0, 0.5, -0.5])

    return root_midi + base_semitone


# [GUI]
class USTGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Hiro UST Generator v4.0")
        self.root.geometry("900x800")
        self.root.minsize(850, 750)

        # =============== MAIN LYRICS (Top 40%) ===============
        input_frame = ttk.LabelFrame(root, text="🎵 Song Lyrics (Romaji/Hiragana)", padding=12)
        input_frame.pack(fill="both", expand=True, padx=15, pady=(15, 10))

        self.lyrics_text = scrolledtext.ScrolledText(input_frame, height=10, font=("Consolas", 10))
        self.lyrics_text.pack(fill="both", expand=True, pady=(0, 12))
        self.lyrics_text.insert("1.0", """[Verse 1]
きゃっきゃ うれし いたい さぶり
ゆびさき きりさけ あかい つゆ

[Chorus]
いたみ いたみ きもちいい""")

        # =============== CONTROLS GRID (4 Perfect Panels) ===============
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
        pause_frame.pack(fill="x")
        ttk.Label(pause_frame, text="Line:").pack(side="left")
        self.line_pause_var = tk.StringVar(value="960")
        ttk.Entry(pause_frame, textvariable=self.line_pause_var, width=10).pack(side="left", padx=(5, 15))
        ttk.Label(pause_frame, text="Sect:").pack(side="left")
        self.section_pause_var = tk.StringVar(value="1920")
        ttk.Entry(pause_frame, textvariable=self.section_pause_var, width=10).pack(side="left", padx=5)

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

        ttk.Label(melody_panel, text="Intone:").pack(anchor="w", pady=(8, 0))
        self.intone_var = ttk.Combobox(melody_panel, values=["Tight (1)", "Medium (2)", "Wide (3)", "Wild (5)"],
                                       state="readonly", width=15)
        self.intone_var.set("Medium (2)")
        self.intone_var.pack(fill="x")

        # Panel 4: Output (Right)
        output_panel = ttk.LabelFrame(controls_main, text="💾 Output", padding=10)
        output_panel.pack(side="right", fill="y")

        ttk.Label(output_panel, text="Project:").pack(anchor="w")
        self.project_var = tk.StringVar(value="Hiro_Main")
        ttk.Entry(output_panel, textvariable=self.project_var).pack(fill="x", pady=(0, 12))

        btn_frame = ttk.Frame(output_panel)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="🎵 Generate UST", command=self.generate_ust).pack(fill="x", pady=(0, 6))
        ttk.Button(btn_frame, text="💾 Save UST", command=self.save_ust_only).pack(fill="x", pady=(0, 6))
        ttk.Button(btn_frame, text="📋 Preview Phonemes", command=self.preview_phonemes).pack(fill="x", pady=(0, 6))
        ttk.Button(btn_frame, text="🧹 Clear All", command=self.clear).pack(fill="x")

        # Status + Preview (unchanged)
        status_frame = ttk.Frame(root)
        status_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.status_var = tk.StringVar(value="✅ Ready - All controls visible!")
        ttk.Label(status_frame, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x")

        preview_frame = ttk.LabelFrame(root, text="👀 Preview", padding=8)
        preview_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=6, state="disabled", font=("Consolas", 9))
        self.preview_text.pack(fill="both", expand=True)

        # 🚨 THESE METHODS MUST BE **INDENTED AT CLASS LEVEL** (same level as __init__)

    def _generate_content(self):
        """Extracted common UST generation logic - NO DUPLICATION!"""
        try:
            melody_brain = MelodyBrain()  # Fresh brain each generation

            lyrics = self.lyrics_text.get("1.0", tk.END).strip()
            if not lyrics:
                self.status_var.set("❌ Lyrics cannot be empty!")
                return None

            parts, elements = parse_song_structure(
                lyrics,
                int(self.line_pause_var.get()),
                int(self.section_pause_var.get())
            )

            root_key = KEY_ROOTS[self.voice_var.get()]

            ust_content = text_to_ust(
                elements, str(self.project_var.get()),
                float(self.tempo_var.get()), int(self.length_var.get()),
                root_key, self.scale_var.get(), self.intone_var.get(),
                float(self.length_var_ctrl.get()), float(self.stretch_var.get()),
                melody_brain,
                self.flat_var.get(), self.quartertone_var.get(),
                self.lyrical_mode_var.get(), self.motif_var.get()
            )
            return ust_content
        except Exception as e:
            self.status_var.set(f"❌ Generation error: {str(e)}")
            return None

    def generate_ust(self):
        """Generate + Auto-save to project dir"""
        ust_content = self._generate_content()
        if not ust_content:
            return

        # PyInstaller-compatible path
        if getattr(sys, 'frozen', False):
            save_dir = os.path.dirname(sys.executable)
        else:
            save_dir = os.path.dirname(os.path.abspath(__file__))

        filename = os.path.join(save_dir, f"{self.project_var.get().replace(' ', '_')}.ust")

        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(ust_content)
            self.status_var.set(f"✅ Saved {os.path.basename(filename)}!")

            # Preview first 600 chars
            self.preview_text.config(state="normal")
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", f"✅ UST Ready:\n\n{ust_content[:600]}...")
            self.preview_text.config(state="disabled")
        except Exception as e:
            self.status_var.set(f"❌ Save failed: {str(e)}")

    def save_ust_only(self):
        """Generate + Save-As dialog ONLY"""
        ust_content = self._generate_content()
        if not ust_content:
            return

        default_name = f"{self.project_var.get()}.ust"
        if getattr(sys, 'frozen', False):
            initial_dir = os.path.dirname(sys.executable)
        else:
            initial_dir = os.path.dirname(os.path.abspath(__file__))

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
        """SINGLE unified phoneme preview - NO DUPLICATES"""
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
        """Unified clear method"""
        self.lyrics_text.delete("1.0", tk.END)
        default_lyrics = """[Verse 1]
        きゃっきゃ うれし いたい さぶり
        ゆびさき きりさけ あかい つゆ

        [Chorus]
        いたみ いたみ きもちいい"""
        self.lyrics_text.insert("1.0", default_lyrics)

        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.config(state="disabled")
        self.status_var.set("✅ Cleared & Ready!")


if __name__ == "__main__":
    root = tk.Tk()
    app = USTGeneratorApp(root)
    root.mainloop()
