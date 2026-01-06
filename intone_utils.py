# intone_utils.py

INTONE_SETTINGS = {
    "Tight (1)": {"leap": 1, "phrase": 6},
    "Medium (2)": {"leap": 2, "phrase": 8},
    "Wide (3)": {"leap": 3, "phrase": 10},
    "Wild (5)": {"leap": 5, "phrase": 12},
}


def get_intone_settings(intone_level: str):
    """Return intone settings dict for given level"""
    return INTONE_SETTINGS.get(intone_level, {"leap": 1, "phrase": 6})
