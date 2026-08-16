"""Controls for melodic articulation and interval behavior."""

INTONE_SETTINGS = {
    # Tight: mostly stepwise motion, very small register movement.
    "Tight (1)": {
        "leap": 2,
        "large_leap": 0,
        "phrase": 6,
        "repeat": 0.42,
        "temperature": 0.32,
    },
    # Medium: normal melodic motion with occasional 3rds/4ths.
    "Medium (2)": {
        "leap": 4,
        "large_leap": 5,
        "large_leap_prob": 0.10,
        "phrase": 8,
        "repeat": 0.28,
        "temperature": 0.48,
    },
    # Wide: expressive leaps become a regular part of the vocabulary.
    "Wide (3)": {
        "leap": 6,
        "large_leap": 8,
        "large_leap_prob": 0.20,
        "phrase": 10,
        "repeat": 0.20,
        "temperature": 0.68,
    },
    # Wild: can make octave-like gestures and strong contrast.
    "Wild (5)": {
        "leap": 8,
        "large_leap": 12,
        "large_leap_prob": 0.34,
        "phrase": 12,
        "repeat": 0.14,
        "temperature": 0.90,
    },
}

# Compatibility defaults used when an unknown preset is supplied.
DEFAULT_INTONE = {
    "leap": 2,
    "large_leap": 0,
    "large_leap_prob": 0.0,
    "phrase": 6,
    "repeat": 0.42,
    "temperature": 0.32,
}


def get_intone_settings(intone_level: str) -> dict:
    """Return a copy of the selected melodic-behavior preset."""
    return dict(INTONE_SETTINGS.get(intone_level, DEFAULT_INTONE))


__all__ = ["INTONE_SETTINGS", "DEFAULT_INTONE", "get_intone_settings"]
