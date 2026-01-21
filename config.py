# config.py


class HiroConfig:
    # Tempo
    MIN_TEMPO = 60.0
    MAX_TEMPO = 240.0

    # Note lengths (ticks)
    MIN_NOTE_LEN = 120
    MAX_NOTE_LEN = 1920

    # Pauses (ticks)
    MIN_LINE_PAUSE = 240
    MAX_LINE_PAUSE = 5000
    MIN_SECTION_PAUSE = 480
    MAX_SECTION_PAUSE = 10000

    # Length variation
    MIN_LENGTH_VAR = 0.0
    MAX_LENGTH_VAR = 1.0

    # Stretch probability
    MIN_STRETCH = 0.0
    MAX_STRETCH = 1.0

    # Pre‑utterance / overlap
    MIN_PRE_UTTER = 0
    MAX_PRE_UTTER = 200
    MIN_VOICE_OVERLAP = 0
    MAX_VOICE_OVERLAP = 100

    # Intensity
    MIN_INTENSITY = 30
    MAX_INTENSITY = 150
    RENDER_INTENSITY_MIN = 50
    RENDER_INTENSITY_MAX = 120

    # Default rests for generated pauses
    PAUSE_LINE_UNIT = 240  # line rests
    PAUSE_SECTION_UNIT = 480  # section rests

    # Quarter‑tone → PBS scaling
    PBS_SCALE = 50  # fraction * PBS_SCALE

    # Default envelope
    DEFAULT_ENVELOPE = "0,10,35,0,100,100,0"
