# presets.py

import json
import os
from typing import Dict, Any


def build_preset_from_app(app) -> Dict[str, Any]:
    """Read all relevant Tk variables from app and return a serializable dict"""
    return {
        "tempo": app.tempo_var.get(),
        "length": app.length_var.get(),
        "voice": app.voice_var.get(),
        "scale": app.scale_var.get(),
        "intone": app.intone_var.get(),
        "length_var": app.length_var_ctrl.get(),
        "stretch": app.stretch_var.get(),
        "pre_utterance": app.pre_utter_var.get(),
        "voice_overlap": app.voice_overlap_var.get(),
        "intensity": app.intensity_base_var.get(),
        "motif": app.motif_var.get(),
        "lyrical": app.lyrical_mode_var.get(),
        "flat": app.flat_var.get(),
        "quartertone": app.quartertone_var.get(),
        "project": app.project_var.get(),
        "line_pause": app.line_pause_var.get(),
        "section_pause": app.section_pause_var.get(),
        "envelope": app.envelope_var.get(),
        "seed": app.seed_var.get(),
    }


def apply_preset_to_app(app, preset: Dict[str, Any]):
    """Apply values from preset dict back to Tk variables and checkboxes"""
    var_map = {
        "tempo": app.tempo_var,
        "length": app.length_var,
        "voice": app.voice_var,
        "scale": app.scale_var,
        "intone": app.intone_var,
        "length_var": app.length_var_ctrl,
        "stretch": app.stretch_var,
        "pre_utterance": app.pre_utter_var,
        "voice_overlap": app.voice_overlap_var,
        "intensity": app.intensity_base_var,
        "project": app.project_var,
        "line_pause": app.line_pause_var,
        "section_pause": app.section_pause_var,
        "envelope": app.envelope_var,
        "seed": app.seed_var,
    }

    for key, var in var_map.items():
        if key in preset:
            var.set(str(preset[key]))

    # Boolean checkboxes
    bool_pairs = [
        (app.motif_var, "motif"),
        (app.lyrical_mode_var, "lyrical"),
        (app.flat_var, "flat"),
        (app.quartertone_var, "quartertone"),
    ]
    for tk_bool, name in bool_pairs:
        if name in preset:
            tk_bool.set(bool(preset[name]))


def save_preset_to_file(preset: Dict[str, Any], filename: str):
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(preset, f, indent=2, ensure_ascii=False)


def load_preset_from_file(filename: str) -> Dict[str, Any]:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
