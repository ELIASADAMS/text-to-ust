# ustx_writer.py
import yaml
import random

EXPRESSIONS = {
    "dyn": {
        "name": "dynamics (curve)",
        "abbr": "dyn",
        "type": "Curve",
        "min": -240,
        "max": 120,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "pitd": {
        "name": "pitch deviation (curve)",
        "abbr": "pitd",
        "type": "Curve",
        "min": -1200,
        "max": 1200,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "clr": {
        "name": "voice color",
        "abbr": "clr",
        "type": "Options",
        "min": 0,
        "max": -1,
        "default_value": 0,
        "is_flag": False,
        "options": [],
    },
    "eng": {
        "name": "resampler engine",
        "abbr": "eng",
        "type": "Options",
        "min": 0,
        "max": 1,
        "default_value": 0,
        "is_flag": False,
        "options": ["", "worldline"],
    },
    "vel": {
        "name": "velocity",
        "abbr": "vel",
        "type": "Numerical",
        "min": 0,
        "max": 200,
        "default_value": 100,
        "is_flag": False,
        "flag": "",
    },
    "vol": {
        "name": "volume",
        "abbr": "vol",
        "type": "Numerical",
        "min": 0,
        "max": 200,
        "default_value": 100,
        "is_flag": False,
        "flag": "",
    },
    "atk": {
        "name": "attack",
        "abbr": "atk",
        "type": "Numerical",
        "min": 0,
        "max": 200,
        "default_value": 100,
        "is_flag": False,
        "flag": "",
    },
    "dec": {
        "name": "decay",
        "abbr": "dec",
        "type": "Numerical",
        "min": 0,
        "max": 100,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "gen": {
        "name": "gender",
        "abbr": "gen",
        "type": "Numerical",
        "min": -100,
        "max": 100,
        "default_value": 0,
        "is_flag": True,
        "flag": "g",
    },
    "genc": {
        "name": "gender (curve)",
        "abbr": "genc",
        "type": "Curve",
        "min": -100,
        "max": 100,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "bre": {
        "name": "breath",
        "abbr": "bre",
        "type": "Numerical",
        "min": 0,
        "max": 100,
        "default_value": 0,
        "is_flag": True,
        "flag": "B",
    },
    "brec": {
        "name": "breathiness (curve)",
        "abbr": "brec",
        "type": "Curve",
        "min": -100,
        "max": 100,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "lpf": {
        "name": "lowpass",
        "abbr": "lpf",
        "type": "Numerical",
        "min": 0,
        "max": 100,
        "default_value": 0,
        "is_flag": True,
        "flag": "H",
    },
    "norm": {
        "name": "normalize",
        "abbr": "norm",
        "type": "Numerical",
        "min": 0,
        "max": 100,
        "default_value": 86,
        "is_flag": True,
        "flag": "P",
    },
    "mod": {
        "name": "modulation",
        "abbr": "mod",
        "type": "Numerical",
        "min": 0,
        "max": 100,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "mod+": {
        "name": "modulation plus",
        "abbr": "mod+",
        "type": "Numerical",
        "min": 0,
        "max": 100,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "alt": {
        "name": "alternate",
        "abbr": "alt",
        "type": "Numerical",
        "min": 0,
        "max": 16,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "dir": {
        "name": "direct",
        "abbr": "dir",
        "type": "Options",
        "min": 0,
        "max": 1,
        "default_value": 0,
        "is_flag": False,
        "options": ["off", "on"],
    },
    "shft": {
        "name": "tone shift",
        "abbr": "shft",
        "type": "Numerical",
        "min": -36,
        "max": 36,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "shfc": {
        "name": "tone shift (curve)",
        "abbr": "shfc",
        "type": "Curve",
        "min": -1200,
        "max": 1200,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "tenc": {
        "name": "tension (curve)",
        "abbr": "tenc",
        "type": "Curve",
        "min": -100,
        "max": 100,
        "default_value": 0,
        "is_flag": False,
        "flag": "",
    },
    "voic": {
        "name": "voicing (curve)",
        "abbr": "voic",
        "type": "Curve",
        "min": 0,
        "max": 100,
        "default_value": 100,
        "is_flag": False,
        "flag": "",
    },
}


class USTXWriter:
    def __init__(self, project_name, tempo, singer_name="イーライ(JPN)"):
        self.project_name = str(project_name)
        self.tempo = tempo
        self.singer_name = singer_name
        self.notes = []
        self.position = 0
        self.resolution = 480

    def add_rest(self, length):
        self.position += length

    def add_small_tsu(self, root_key, length=60):
        self.notes.append(
            {
                "position": self.position,
                "duration": length,
                "tone": int(root_key),
                "lyric": "っ",
                "pitch": {
                    "data": [{"x": 0, "y": 20, "shape": "io"}],
                    "snap_first": True,
                },
                "vibrato": {
                    "length": 0,
                    "period": 175,
                    "depth": 25,
                    "in": 10,
                    "out": 10,
                    "shift": 0,
                    "drift": 0,
                    "vol_link": 0,
                },
                "phoneme_expressions": [
                    {"index": 0, "abbr": "norm", "value": 86},
                    {"index": 0, "abbr": "vol", "value": 30},
                ],
                "phoneme_overrides": [],
            }
        )
        self.position += length

    def add_note(
        self,
        length,
        lyric,
        note_num,
        pre_utter,
        voice_overlap,
        intensity,
        envelope,
        pbs="0;0",
        pbw="0",
        flags="",
        bpm=120,
    ):
        length = max(60, min(1920, length))

        # PITCH DROP
        pitch_data = [{"x": 0, "y": 0, "shape": "io"}]

        if pbs != "0;0" and ";" in pbs:
            try:
                drop_strength = int(pbs.split(";")[1])
                if drop_strength < -20:  # Pitch drop
                    pitch_data = [
                        {
                            "x": -60,
                            "y": drop_strength * 0.8,
                            "shape": "io",
                        },  # Sharp drop
                        {"x": 59, "y": 0, "shape": "io"},
                    ]
                elif drop_strength > 20:
                    # Pitch rise
                    pitch_data = [
                        {"x": -45, "y": drop_strength * 0.6, "shape": "io"},
                        {"x": 44, "y": 0, "shape": "io"},
                    ]
                else:
                    pitch_data = [
                        {"x": -40, "y": drop_strength, "shape": "io"},
                        {"x": 40, "y": 0, "shape": "io"},
                    ]
            except:
                pass
        else:
            # Natural melodic curve
            if random.random() < 0.3:
                pitch_data = [
                    {"x": -45, "y": random.randint(-30, 30), "shape": "io"},
                    {"x": 44, "y": 0, "shape": "io"},
                ]

        # 30% chance long vibrato
        vibrato_length = random.randint(70, 100) if random.random() < 0.3 else 0
        vibrato = {
            "length": vibrato_length,
            "period": random.randint(120, 180),
            "depth": random.randint(25, 80),
            "in": 20,
            "out": 20,
            "shift": 0,
            "drift": random.randint(0, 57),
            "vol_link": 0,
        }

        phoneme_expressions = [
            {"index": 0, "abbr": "mod", "value": 10},
            {"index": 0, "abbr": "vel", "value": 180},
            {"index": 0, "abbr": "vol", "value": max(50, min(200, intensity))},
        ]

        self.notes.append(
            {
                "position": self.position,
                "duration": length,
                "tone": int(max(21, min(108, round(note_num)))),
                "lyric": lyric,
                "pitch": {"data": pitch_data, "snap_first": lyric == "っ"},
                "vibrato": vibrato,
                "phoneme_expressions": phoneme_expressions,
                "phoneme_overrides": [],
            }
        )
        self.position += length

    def finalize(self):
        return yaml.dump(
            {
                "name": self.project_name,
                "comment": "",
                "output_dir": "Vocal",
                "cache_dir": "UCache",
                "ustx_version": "0.7",
                "resolution": self.resolution,
                "bpm": self.tempo,
                "beat_per_bar": 4,
                "beat_unit": 4,
                "expressions": EXPRESSIONS,
                "exp_selectors": [
                    "dyn",
                    "pitd",
                    "clr",
                    "eng",
                    "vel",
                    "vol",
                    "atk",
                    "dec",
                    "gen",
                    "bre",
                ],
                "exp_primary": 0,
                "exp_secondary": 1,
                "key": 0,
                "time_signatures": [
                    {"bar_position": 0, "beat_per_bar": 4, "beat_unit": 4}
                ],
                "tempos": [{"position": 0, "bpm": self.tempo}],
                "tracks": [
                    {
                        "singer": self.singer_name,
                        "phonemizer": "OpenUtau.Plugin.Builtin.JapanesePresampPhonemizer",
                        "renderer_settings": {
                            "renderer": "CLASSIC",
                            "resampler": "moresampler.exe",
                            "wavtool": "moresampler.exe",
                        },
                        "track_name": "Track1",
                        "track_color": "Blue",
                        "mute": False,
                        "solo": False,
                        "volume": 0,
                        "pan": 0,
                        "track_expressions": [],
                        "voice_color_names": [""],
                    }
                ],
                "voice_parts": [
                    {
                        "duration": self.position,
                        "name": self.project_name,
                        "comment": "",
                        "track_no": 0,
                        "position": 0,
                        "notes": self.notes,
                    }
                ],
                "wave_parts": [],
            },
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
