# 響 Hiro UST

**Procedural Japanese lyric → UTAU UST generator** with mora-aware phonemization, procedural melody, motif memory, Japanese pitch-accent support, timing variation, dynamics, and pitch-bend expression.

Hiro is designed as a **generative starting-point and tuning assistant**: instead of manually drawing every note and lyric assignment from scratch, it turns lyrics into a structured UST that can be opened in UTAU and refined further.

> Built by Ilya Minin (Eli) — artist, creative technologist, and generative-audio developer.

---

## Run Hiro

### PyCharm

Open the repository root and configure a **Python** run configuration with:

```text
Module name: hiro_ust
Working directory: repository root
Interpreter: project virtual environment
```

Then run it. This is equivalent to:

```bash
python -m hiro_ust
```

Detailed PyCharm instructions: [`docs/PYCHARM.md`](docs/PYCHARM.md)

### Terminal

```bash
python -m pip install -e .
python -m hiro_ust
```

### Build the Windows EXE

Install development/build dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Then:

```bash
python build_exe.py
```

The resulting executable is:

```text
dist/Hiro_UST_Generator.exe
```

---

## What Hiro does

Hiro takes Japanese lyrics written in Hiragana/Katakana or supported Romaji forms and generates a UST with:

- mora-aware lyric parsing
- yōon such as `きゃ`, `しゅ`, `ちょ`
- small-tsu gemination `っ`
- moraic nasal `ん`
- phrase and section boundaries
- procedural pitch selection
- scale-aware melody generation
- voice-range constraints
- motif reuse and variation
- deterministic seeded generation
- timing variation
- intensity/dynamics heuristics
- Japanese pitch-accent-aware behavior
- optional microtonal pitch-bend expression
- UST serialization

The project is intentionally **procedural rather than fully AI-generated**. The same seed can reproduce a generation, making musical experiments and algorithm changes easier to compare.

---

## Project structure

```text
text-to-ust/
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── build_exe.py
├── hibiki.ico
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── PYCHARM.md
│
├── tests/
│
└── src/
    └── hiro_ust/
        ├── __init__.py
        ├── __main__.py        ← canonical application entry point
        ├── cli.py             ← launcher
        ├── core.py            ← public programmatic API
        ├── config.py
        ├── constants.py
        ├── logger.py
        ├── converter/
        ├── data/
        ├── generator/
        ├── melody/
        ├── voice/
        └── hiro_ust_dev.py    ← legacy/internal runtime code under migration
```

Do not launch individual internal modules as the application. Use:

```bash
python -m hiro_ust
```

---

## Installation

Hiro uses a `src/` package layout. Install it in editable mode during development:

```bash
python -m pip install -e .
```

Runtime dependencies are kept in `requirements.txt` / `pyproject.toml`. Development and packaging tools such as PyInstaller are kept in `requirements-dev.txt`.

`tkinter` is normally bundled with standard Python distributions on Windows and macOS; it is not normally installed with `pip`.

---

## Input and phonemization

Japanese lyrics are fundamentally **mora-oriented**, so Hiro does not simply split Japanese text into individual characters.

Examples:

```text
きゃ → kya
しょ → sho
にゃ → nya
っ → っ
ん → n
```

A mora trie performs longest-match parsing so that:

```text
きゃ
```

is recognized as one yōon unit instead of being incorrectly split into `き` and `ゃ`.

Punctuation such as `、`, `。`, `！`, `？`, and `…` is preserved because it can carry musical phrase information.

---

## Melody generation

Hiro combines several procedural ideas instead of choosing every pitch randomly.

### Voice leading

The next note considers its relationship to the previous note. Lower intone settings favor smaller movements; higher settings permit wider melodic leaps.

### Scales

The melody can be constrained to configured scales, including common diatonic, pentatonic, blues, whole-tone, octatonic, chromatic, and experimental palettes available in the project.

### Motif memory

Hiro can remember short melodic ideas and reuse them later. Motifs are represented as interval patterns, allowing the same shape to recur transposed to another pitch level.

### Deterministic generation

The seed controls procedural choices, making it possible to reproduce a result for debugging and algorithm comparison.

---

## Expression

Expression can include pitch bends, microtonal offsets, intensity, envelopes, pre-utterance, voice overlap, and timing variation.

UST stores integer MIDI note numbers, so fractional pitches such as `60.5` must be represented with pitch-bend information instead of simply being rounded away.

Vibrato is intended to become context-dependent rather than being applied indiscriminately to every note.

---

## Current limitations

Hiro is a **procedural generator and starting point**, not a replacement for a professional human UTAU tuner.

Current development areas include deeper Japanese pitch-accent modeling, richer phrase-level melody decisions, stronger voicebank-specific phonetic handling, intelligent vibrato/portamento, and extraction of the remaining legacy logic from `hiro_ust_dev.py`.

---

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — architecture and developer guide
- [`docs/PYCHARM.md`](docs/PYCHARM.md) — PyCharm setup, execution, and EXE building

## License

MIT.

## Author

**Ilya Minin (Eli)**
