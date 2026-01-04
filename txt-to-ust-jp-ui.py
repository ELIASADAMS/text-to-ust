import random
import tkinter as tk
from tkinter import ttk, scrolledtext

SCALES = {
    # 12-note (Chromatic)
    'Chromatic': list(range(12)),

    # 9-note (Nonatonic Blues)
    'Nonatonic Blues': [0, 2, 3, 5, 6, 7, 8, 10, 11],

    # 8-note (Octatonic)
    'Octatonic': [0, 1, 3, 4, 6, 7, 9, 10],

    # 7-note (Diatonic - your originals)
    'C Major': [0, 2, 4, 5, 7, 9, 11], 'C Minor': [0, 2, 3, 5, 7, 8, 10],
    'D Major': [2, 4, 6, 7, 9, 11, 1], 'D Minor': [2, 4, 5, 7, 9, 10, 0],
    'E Major': [4, 6, 8, 9, 11, 1, 3], 'E Minor': [4, 6, 7, 9, 11, 0, 2],
    'F Major': [5, 7, 9, 10, 0, 2, 4], 'F Minor': [5, 7, 8, 10, 0, 1, 3],
    'G Major': [7, 9, 11, 0, 2, 4, 6], 'G Minor': [7, 9, 10, 0, 2, 3, 5],
    'A Major': [9, 11, 1, 2, 4, 6, 8], 'A Minor': [9, 11, 0, 2, 4, 5, 7],

    # 6-note (Hexatonic/Whole Tone)
    'Whole Tone': [0, 2, 4, 6, 8, 10],
    'Hexatonic Blues': [0, 3, 5, 6, 9, 10],

    # 5-note (Pentatonic)
    'Major Pentatonic': [0, 2, 4, 7, 9],
    'Minor Pentatonic': [0, 3, 5, 7, 10],

    # 4-note (Tetratonic)
    'Tetratonic': [0, 4, 7, 11]
}


class HiroUSTGenerator:
    def __init__(self):
        self.hiragana_map = {
            # Vowels
            'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'え', 'o': 'お',

            # K-row + dakuten + yoon + sokuon
            'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ',
            'ga': 'が', 'gi': 'ぎ', 'gu': 'ぐ', 'ge': 'げ', 'go': 'ご',
            'kya': 'きゃ', 'kyu': 'きゅ', 'kyo': 'きょ',
            'gya': 'ぎゃ', 'gyu': 'ぎゅ', 'gyo': 'ぎょ',

            # S-row + dakuten + yoon
            'sa': 'さ', 'shi': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ',
            'za': 'ざ', 'ji': 'じ', 'zu': 'ず', 'ze': 'ぜ', 'zo': 'ぞ',
            'sha': 'しゃ', 'shu': 'しゅ', 'sho': 'しょ',
            'ja': 'じゃ', 'ju': 'じゅ', 'jo': 'じょ',

            # T-row + dakuten + yoon + sokuon
            'ta': 'た', 'chi': 'ち', 'tsu': 'つ', 'te': 'て', 'to': 'と',
            'da': 'だ', 'ji': 'ぢ', 'zu': 'づ', 'de': 'で', 'do': 'ど',
            'cha': 'ちゃ', 'chu': 'ちゅ', 'cho': 'ちょ',

            # N-row + yoon
            'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
            'nya': 'にゃ', 'nyu': 'にゅ', 'nyo': 'にょ',

            # H-row + b/p + yoon
            'ha': 'は', 'hi': 'ひ', 'fu': 'ふ', 'he': 'へ', 'ho': 'ほ',
            'ba': 'ば', 'bi': 'び', 'bu': 'ぶ', 'be': 'べ', 'bo': 'ぼ',
            'pa': 'ぱ', 'pi': 'ぴ', 'pu': 'ぷ', 'pe': 'ぺ', 'po': 'ぽ',
            'hya': 'ひゃ', 'hyu': 'ひゅ', 'hyo': 'ひょ',
            'bya': 'びゃ', 'byu': 'びゅ', 'byo': 'びょ',

            # M-row + yoon
            'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
            'mya': 'みゃ', 'myu': 'みゅ', 'myo': 'みょ',

            # Y-row
            'ya': 'や', 'yu': 'ゆ', 'yo': 'よ',

            # R-row + yoon
            'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
            'rya': 'りゃ', 'ryu': 'りゅ', 'ryo': 'りょ',

            # Others
            'wa': 'わ', 'wo': 'を', 'n': 'ん',

            # Sokuon combinations (っ + CV)
            'tsutsu': 'っつ', 'katsu': 'っか', 'kitsu': 'っき', 'kutsu': 'っく',
            'ketsu': 'っけ', 'kotsu': 'っこ', 'tatsu': 'った', 'chitsu': 'っち',
            'setsu': 'っせ', 'sotsu': 'っそ'
        }

    def romaji_to_hiragana(self, phoneme):
        # SPECIAL SOKUON COMBOS ONLY - otherwise RETURN ROMAJI
        sokuon_combos = {
            'katsu': 'っか', 'kitsu': 'っき', 'kutsu': 'っく', 'ketsu': 'っけ', 'kotsu': 'っこ',
            'tatsu': 'った', 'chitsu': 'っち', 'setsu': 'っせ', 'sotsu': 'っそ', 'tsutsu': 'っつ',
            'tta': 'った', 'ppa': 'っぱ', 'mma': 'っま', 'nna': 'んな', 'ssa': 'っさ'
        }

        if phoneme in sokuon_combos:
            return sokuon_combos[phoneme]
        return phoneme  # Returns 'な'→'な', 'tsu'→'tsu'


def hiragana_to_romaji(text):
    # COMPLETE Japanese mora → phoneme mapping
    mora_map = {
        # Sokuon (small tsu)
        'っ': ['っ'],

        # Vowels (5)
        'あ': ['a'], 'い': ['i'], 'う': ['u'], 'え': ['e'], 'お': ['o'],

        # K-row (かきくけこ) + dakuten/handakuten + yoon + sokuon
        'か': ['ka'], 'き': ['ki'], 'く': ['ku'], 'け': ['ke'], 'こ': ['ko'],
        'が': ['ga'], 'ぎ': ['gi'], 'ぐ': ['gu'], 'げ': ['ge'], 'ご': ['go'],
        'きゃ': ['kya'], 'きゅ': ['kyu'], 'きょ': ['kyo'],
        'ぎゃ': ['gya'], 'ぎゅ': ['gyu'], 'ぎょ': ['gyo'],
        'っか': ['っ', 'ka'], 'っき': ['っ', 'ki'], 'っく': ['っ', 'ku'],
        'っけ': ['っ', 'ke'], 'っこ': ['っ', 'ko'],
        'っが': ['っ', 'ga'], 'っぎ': ['っ', 'gi'], 'っぐ': ['っ', 'gu'],

        # S-row (さしすせそ)
        'さ': ['sa'], 'し': ['shi'], 'す': ['su'], 'せ': ['se'], 'そ': ['so'],
        'ざ': ['za'], 'じ': ['ji'], 'ず': ['zu'], 'ぜ': ['ze'], 'ぞ': ['zo'],
        'しゃ': ['sha'], 'しゅ': ['shu'], 'しょ': ['sho'],
        'じゃ': ['ja'], 'じゅ': ['ju'], 'じょ': ['jo'],

        # T-row (たちつてと)
        'た': ['ta'], 'ち': ['chi'], 'つ': ['tsu'], 'て': ['te'], 'と': ['to'],
        'だ': ['da'], 'ぢ': ['ji'], 'づ': ['zu'], 'で': ['de'], 'ど': ['do'],
        'ちゃ': ['cha'], 'ちゅ': ['chu'], 'ちょ': ['cho'],
        'っつ': ['っ', 'tsu'],

        # N-row (なにぬねの)
        'な': ['na'], 'に': ['ni'], 'ぬ': ['nu'], 'ね': ['ne'], 'の': ['no'],
        'にゃ': ['nya'], 'にゅ': ['nyu'], 'にょ': ['nyo'],

        # H-row (はひふへほ) + p/b
        'は': ['ha'], 'ひ': ['hi'], 'ふ': ['fu'], 'へ': ['he'], 'ほ': ['ho'],
        'ば': ['ba'], 'び': ['bi'], 'ぶ': ['bu'], 'べ': ['be'], 'ぼ': ['bo'],
        'ぱ': ['pa'], 'ぴ': ['pi'], 'ぷ': ['pu'], 'ぺ': ['pe'], 'ぽ': ['po'],
        'ひゃ': ['hya'], 'ひゅ': ['hyu'], 'ひょ': ['hyo'],
        'びゃ': ['bya'], 'びゅ': ['byu'], 'びょ': ['byo'],

        # M-row (まみむめも)
        'ま': ['ma'], 'み': ['mi'], 'む': ['mu'], 'め': ['me'], 'も': ['mo'],
        'みゃ': ['mya'], 'みゅ': ['myu'], 'みょ': ['myo'],

        # Y-row (やゆよ)
        'や': ['ya'], 'ゆ': ['yu'], 'よ': ['yo'],

        # R-row (らりるれろ)
        'ら': ['ra'], 'り': ['ri'], 'る': ['ru'], 'れ': ['re'], 'ろ': ['ro'],
        'りゃ': ['rya'], 'りゅ': ['ryu'], 'りょ': ['ryo'],

        # W-row + N
        'わ': ['wa'], 'を': ['wo'], 'ん': ['n']
    }

    phonemes = []
    i = 0
    text = text.strip()

    while i < len(text):
        # Try 3-char patterns first (っか, っきゃ etc.)
        found = False
        for mora, phones in mora_map.items():
            if len(mora) == 3 and text[i:i + 3] == mora:
                phonemes.extend(phones)
                i += 3
                found = True
                break

        if found: continue

        # Try 2-char patterns (きゃ, しゃ etc.)
        for mora, phones in mora_map.items():
            if len(mora) == 2 and text[i:i + 2] == mora:
                phonemes.extend(phones)
                i += 2
                found = True
                break

        if found: continue

        # Try 1-char patterns (か, あ etc.)
        for mora, phones in mora_map.items():
            if len(mora) == 1 and text[i:i + 1] == mora:
                phonemes.extend(phones)
                i += 1
                found = True
                break

        if not found:
            i += 1  # Skip unknown chars

    return phonemes


def create_stretch_notes(phoneme, stretch_prob=0.25, max_stretch=3):
    if len(phoneme) >= 2 and phoneme[0] == phoneme[1] and phoneme[0] in 'あいうえお':
        return [(phoneme[0], 1.8)]  # Single long note
    if random.random() < stretch_prob and len(phoneme) == 1 and phoneme in 'あいうえお':
        stretches = random.randint(1, max_stretch)
        return [(phoneme, 1.2)] + [('+', 0.8)] * stretches
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
            phonemes = hiragana_to_romaji(line)
            all_elements.extend(phonemes)
            all_elements.append(f"PAUSE_LINE:{line_pause}")

    if all_elements and all_elements[-1].startswith("PAUSE_LINE"):
        all_elements.pop()

    return parts, all_elements


class MotifMemory:
    def __init__(self, motif_length=4):
        self.motif_length = motif_length  # 3-5 notes
        self.stored_motifs = []  # List of [note1, note2, note3, note4]
        self.max_motifs = 5

    def add_motif(self, notes):
        """Store recent notes as motif"""
        if len(notes) >= self.motif_length:
            motif = notes[-self.motif_length:]  # Last N notes
            # Avoid duplicate motifs
            if motif not in self.stored_motifs:
                self.stored_motifs.append(motif)
                # Keep only top 5 motifs
                if len(self.stored_motifs) > self.max_motifs:
                    self.stored_motifs.pop(0)

    def get_motif_note(self, current_note, scale, use_motif_prob=0.4):
        """Get note from motif memory OR new note"""
        if (self.stored_motifs and
                random.random() < use_motif_prob and
                len(self.stored_motifs[-1]) > 1):

            # 🎵 REUSE MOTIF WITH VARIATION
            motif = self.stored_motifs[-1]
            next_in_motif = motif[1:]  # Shift motif forward

            # Variation: ±1 semitone with 50% chance
            if random.random() < 0.5:
                varied_note = next_in_motif[0] + random.choice([-1, 0, 1])
                target_note = min(max(0, varied_note), 11)
            else:
                target_note = next_in_motif[0]

            # Snap to scale
            closest_scale = min(scale, key=lambda x: abs(x - target_note))
            return closest_scale

        # No motif: regular melodic note
        melodic_notes = [0, 2, 4, 5, 7, 9]  # Scale degrees
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

        # PHRASE ENDINGS first
        if self.phrase_len > settings["phrase"] or phoneme in '。！？':
            self.phrases.append(self.last_note)
            self.last_note = random.choice([0, 7])  # Tonic or dominant
            self.phrase_len = 1
            target_note = self.last_note
        else:
            # MOTIF MEMORY (toggleable!)
            if use_motifs:
                target_note = self.motif_memory.get_motif_note(
                    self.last_note, scale, use_motif_prob=0.4)
            else:
                # Original logic
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
melody_brain = MelodyBrain()

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
                intone_level, length_var, stretch_prob, flat_mode=False,
                quartertone_mode=False, lyrical_mode=True, use_motifs=True):
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

            if romaji_phoneme == 'っ':
                note_length = 120
                note_num = melody_brain.get_smart_note(root_key, scale, 'tsu', intone_level, flat_mode,
                                                       quartertone_mode, use_motifs)
                ust += f'\n[#{note_id:04d}]\nLength={note_length}\nLyric=tsu\nNoteNum={int(note_num)}\n'
                ust += f'PreUtterance=10\nVoiceOverlap=0\nIntensity=60\n'
                ust += f'Modulation=0\nPBS=0\nPBW=0\nStartPoint=0\nEnvelope=0,10,35,0,100,100,0\n'
                note_id += 1
                continue

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
                # Fixed dynamic intensity
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


# [GUI stays exactly the same as previous version]
class USTGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hiro v3.2")
        self.root.geometry("750x700")

        input_frame = ttk.LabelFrame(root, text="🎵 Song Lyrics", padding=10)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.lyrics_text = scrolledtext.ScrolledText(input_frame, height=8)
        self.lyrics_text.pack(fill="both", expand=True, pady=(0, 10))
        self.lyrics_text.insert("1.0", """[Verse 1]
きゃっきゃ うれし いたい さぶり
ゆびさき きりさけ あかい つゆ

[Chorus]
いたみ いたみ きもちいい""")

        controls_frame = ttk.LabelFrame(root, text="⚙️ Generation Settings", padding=10)
        controls_frame.pack(fill="x", padx=10, pady=5)

        row1 = ttk.Frame(controls_frame)
        row1.pack(fill="x", pady=(0, 5))
        ttk.Label(row1, text="Tempo:").pack(side="left")
        self.tempo_var = tk.StringVar(value="120.00")
        ttk.Entry(row1, textvariable=self.tempo_var, width=8).pack(side="left", padx=(5, 20))
        ttk.Label(row1, text="Base Length:").pack(side="left")
        self.length_var = tk.StringVar(value="240")
        ttk.Entry(row1, textvariable=self.length_var, width=8).pack(side="left", padx=5)

        row2 = ttk.Frame(controls_frame)
        row2.pack(fill="x", pady=(0, 5))
        ttk.Label(row2, text="Line Pause:").pack(side="left")
        self.line_pause_var = tk.StringVar(value="960")
        ttk.Entry(row2, textvariable=self.line_pause_var, width=8).pack(side="left", padx=(5, 5))
        ttk.Label(row2, text="Section Pause:").pack(side="left", padx=(20, 0))
        self.section_pause_var = tk.StringVar(value="1920")
        ttk.Entry(row2, textvariable=self.section_pause_var, width=8).pack(side="left", padx=5)

        row3 = ttk.Frame(controls_frame)
        row3.pack(fill="x", pady=(0, 5))
        ttk.Label(row3, text="Length Var:").pack(side="left")
        self.length_var_ctrl = tk.StringVar(value="0.3")
        ttk.Entry(row3, textvariable=self.length_var_ctrl, width=8).pack(side="left", padx=5)
        ttk.Label(row3, text="Stretch Prob:").pack(side="left", padx=(20, 0))
        self.stretch_var = tk.StringVar(value="0.25")
        ttk.Entry(row3, textvariable=self.stretch_var, width=8).pack(side="left", padx=5)

        row4 = ttk.Frame(controls_frame)
        row4.pack(fill="x", pady=(0, 10))
        ttk.Label(row4, text="Root:").pack(side="left")
        self.root_var = tk.StringVar(value="60")
        ttk.Entry(row4, textvariable=self.root_var, width=8).pack(side="left", padx=(5, 10))
        ttk.Label(row4, text="Scale:").pack(side="left")
        self.scale_var = ttk.Combobox(row4, values=list(SCALES.keys()), state="readonly", width=12)
        self.scale_var.set("Major Pentatonic")
        self.scale_var.pack(side="left", padx=(5, 10))

        self.motif_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row4, text="🎼 Motif Memory", variable=self.motif_var).pack(side="left", padx=5)

        # Intonation slider + dropdown
        ttk.Label(row4, text="Intone:").pack(side="left")
        self.intone_var = ttk.Combobox(row4, values=["Tight (1)", "Medium (2)", "Wide (3)", "Wild (5)"],
                                       state="readonly", width=10)
        self.intone_var.set("Tight (1)")
        self.intone_var.pack(side="left", padx=5)

        self.flat_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row4, text="🎹 Flat", variable=self.flat_var).pack(side="left", padx=5)

        self.quartertone_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row4, text="🎼 Quarter-Tone", variable=self.quartertone_var).pack(side="left", padx=5)

        self.lyrical_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row4, text="🎭 Lyrical Mode", variable=self.lyrical_mode_var).pack(side="left", padx=5)

        ttk.Label(controls_frame, text="Project:").pack(anchor="w")
        self.project_var = tk.StringVar(value="Main")
        ttk.Entry(controls_frame, textvariable=self.project_var).pack(fill="x", pady=(0, 10))

        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="🎵 Generate UST", command=self.generate_ust).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📋 Preview", command=self.preview_phonemes).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🧹 Clear", command=self.clear).pack(side="right")

        self.status_var = tk.StringVar(value="Ready!")
        ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x", padx=10,
                                                                                        pady=(0, 5))

        self.preview_text = scrolledtext.ScrolledText(root, height=6, state="disabled")
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def preview_phonemes(self):
        lyrics = self.lyrics_text.get("1.0", tk.END).strip()
        parts, elements = parse_song_structure(lyrics)
        preview = "\n\n"
        for i, elem in enumerate(elements[:20]):  # First 20
            if not elem.startswith('PAUSE'):
                preview += f"{i}: {elem} → {HiroUSTGenerator().romaji_to_hiragana(elem)}\n"
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", preview)
        self.preview_text.config(state="disabled")

    def generate_ust(self):
        try:
            global melody_brain
            melody_brain = MelodyBrain()
            lyrics = self.lyrics_text.get("1.0", tk.END).strip()
            parts, elements = parse_song_structure(
                lyrics,
                int(self.line_pause_var.get()),
                int(self.section_pause_var.get())
            )

            ust_content = text_to_ust(
                elements,  # 1
                str(self.project_var.get()),  # 2
                float(self.tempo_var.get()),  # 3
                int(self.length_var.get()),  # 4
                int(self.root_var.get()),  # 5
                self.scale_var.get(),  # 6
                self.intone_var.get(),  # 7
                float(self.length_var_ctrl.get()),  # 8
                float(self.stretch_var.get()),  # 9
                self.flat_var.get(),  # 10
                self.quartertone_var.get(),  # 11
                self.lyrical_mode_var.get(),  # 12
                self.motif_var.get()
            )

            filename = f"{str(self.project_var.get()).replace(' ', '_')}.ust"
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(ust_content)

            self.status_var.set(f"✅ Saved {filename}!")
            self.preview_text.config(state="normal")
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", f"✅ FIXED: {filename}\n\n{ust_content[:600]}...")
            self.preview_text.config(state="disabled")
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")

    def clear(self):
        self.lyrics_text.delete("1.0", tk.END)
        self.lyrics_text.insert("1.0", """[Verse 1]
きゃっきゃ うれし いたい さぶり""")
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.config(state="disabled")
        self.status_var.set("Ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = USTGeneratorApp(root)
    root.mainloop()
