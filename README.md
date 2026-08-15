# 響 Hiro UST

**Procedural Japanese lyric → UTAU UST generator** with mora-aware phonemization, procedural melody, motif memory, Japanese pitch-accent support, timing variation, dynamics, and pitch-bend expression.

Hiro is designed as a **generative starting-point and tuning assistant**: instead of manually drawing every note and lyric assignment from scratch, it turns lyrics into a structured UST that can be opened in UTAU and refined further.

> Built by Ilya Minin (Eli) — artist, creative technologist, and generative-audio developer.

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
- optional quarter-tone / microtonal pitch-bend expression
- UST serialization

The project is intentionally **procedural rather than fully AI-generated**. The same seed can reproduce a generation, making musical experiments and algorithm changes easier to compare.

## Quick example

Input:

```text
[Verse]
きゃっきゃ うれしい
ゆびさき きりさけ

[Chorus]
いたみ いたみ
きもちいい
```

Conceptually:

```text
Lyrics
  ↓
Japanese normalization
  ↓
Mora / phoneme parsing
  ↓
Phrase analysis
  ↓
Procedural melody
  ↓
Timing + dynamics + pitch expression
  ↓
.ust
```

The generated UST can then be opened in UTAU and edited or tuned manually.

## Installation

### Python

Hiro uses a `src/` package layout. Install the project in editable mode during development:

```bash
pip install -e .
```

Then run the application entry point provided by the repository.

> `tkinter` is normally bundled with standard Python installations on Windows and macOS. It is not normally installed with `pip`.

### Windows executable

If a packaged executable is provided in Releases, the executable is the easiest option for users who do not want to install Python.

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

A mora trie performs longest-match parsing so that `きゃ` is recognized as one yōon unit instead of being incorrectly split into `き` and `ゃ`.

### Supported input styles

- Hiragana
- Katakana
- supported Japanese Romaji
- Japanese punctuation

Romaji is normalized through a Japanese kana representation before phoneme generation where appropriate.

### Punctuation matters

Punctuation is preserved because it can represent musical structure:

```text
、  。  ！  ？  …
```

These boundaries can influence rests, cadence, intensity, timing, breaths, and vibrato decisions.

## Melody generation

Hiro combines several procedural ideas instead of choosing every pitch randomly.

### Voice leading

The next note considers its relationship to the previous note. Lower `intone` settings favor smaller movements; higher settings permit wider melodic leaps.

### Scales

The melody can be constrained to configured scales, including common diatonic, pentatonic, blues, whole-tone, octatonic, chromatic, and other experimental palettes available in the project.

### Motif memory

Hiro can remember short melodic ideas and reuse them later.

Motifs are treated as **interval patterns**, not only absolute pitches. For example:

```text
C → D → E → G
```

can be remembered as:

```text
+2 → +2 → +3
```

and reused transposed to another part of the vocal range.

### Phrase behavior

Phrase and section boundaries can influence pitch resets, rests, cadence behavior, and melodic contour.

### Deterministic generation

A seed controls procedural choices. This makes it possible to regenerate the same result and compare changes to one algorithm without the entire song changing unpredictably.

## Japanese pitch accent

Japanese pitch accent is treated as a melodic/prosodic signal rather than ordinary stress accent.

The project contains support for patterns such as:

- Heiban
- Atamadaka
- Nakadaka
- Odaka

The intended model is a pitch contour across mora positions, including the location of the accent nucleus / pitch drop.

This is important because a natural Japanese vocal line should not treat every mora as an independent Western-style stressed syllable.

## Expression

Hiro separates musical pitch from expressive pitch information where possible.

Expression can include:

- pitch bends
- microtonal offsets
- intensity
- envelopes
- pre-utterance
- voice overlap
- timing variation

### Microtones

UST uses integer MIDI note numbers. A value such as MIDI `60.5` therefore cannot simply be rounded away.

Hiro can represent fractional pitch using UST pitch-bend information:

```text
60.5 MIDI
  ↓
MIDI 60 + pitch bend
```

This allows quarter-tone and other continuous pitch movements to survive UST serialization.

### Vibrato roadmap

Vibrato is intended to be context-dependent rather than automatically applied to every note. Strong candidates include long sustained vowels, phrase-final notes, important melodic notes, and expressive climaxes.

## Configuration

| Setting | Purpose |
|---|---|
| Tempo | Song tempo in BPM |
| Base Length | Default note duration |
| Root Key | Musical root / MIDI reference |
| Voice | Voice-range / preset selection |
| Scale | Allowed pitch palette |
| Intone Level | Melodic leap behavior |
| Length Variation | Timing variation amount |
| Stretch Probability | Probability of extended notes |
| Pre-Utterance | UST vocal timing |
| Voice Overlap | UST overlap |
| Intensity | Base note dynamics |
| Envelope | UST envelope preset |
| Flat Mode | Reduce melodic movement |
| Quartertone Mode | Enable microtonal pitch behavior |
| Lyrical Mode | Phoneme-aware melodic behavior |
| Motifs | Enable motif memory |
| Chords | Enable harmonic constraints |
| Seed | Reproducible procedural generation |

Configuration values are validated before generation so invalid tempo, MIDI, duration, and rendering values fail early rather than producing malformed output.

## Architecture

```text
                    LYRICS
                       │
                       ▼
              ┌────────────────┐
              │ Text / Parser  │
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ Phonemizer     │
              │ Mora + Accent  │
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ Melody Brain   │
              │ Scale / Motif  │
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ Note Generator │
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ Expression     │
              │ Pitch / Timing │
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │ UST / USTX     │
              │ Writer         │
              └────────────────┘
```

Detailed developer documentation is available in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

The architectural goal is to keep linguistic analysis, musical decisions, expression, and file serialization independent from each other.

## Project structure

```text
src/hiro_ust/
├── config.py
├── constants.py
├── core.py
├── converter/
│   └── phonemizer.py
├── data/
│   └── mora_trie_data.py
├── generator/
│   ├── note_generator.py
│   ├── ust_strings.py
│   └── ...
├── melody/
│   ├── melody_logic.py
│   └── envelopes.py
├── voice/
│   ├── key_roots.py
│   ├── presets.py
│   └── phonetic_utils.py
└── ui/
```

Some legacy/development code is still being migrated toward this modular architecture.

## Testing and development

The generator is procedural, so regression testing is especially important.

Recommended test areas include mora parsing, Romaji conversion, yōon and small-tsu handling, punctuation preservation, deterministic generation, scale membership, voice-range limits, pitch-bend serialization, valid UST syntax, and UTF-8 output.

For development, a fixed seed should be used when comparing algorithm changes.

## Current limitations

Hiro is a **procedural generator and starting point**, not a replacement for a professional human UTAU tuner.

Current development areas include:

- deeper Japanese pitch-accent modeling
- more realistic phrase-level melody decisions
- richer expression generation
- intelligent vibrato and portamento
- stronger voicebank-specific phonetic handling
- continued removal of legacy generation paths
- expanded automated regression coverage

English phonemization is also intentionally less mature than the Japanese pipeline and should not currently be treated as equivalent to a full English phoneme dictionary or ARPABET/G2P system.

## Roadmap

### Phase 1 — Correctness

- configuration validation
- deterministic random generation
- punctuation preservation
- microtone serialization
- regression tests

### Phase 2 — Architecture

- remove duplicate legacy generation paths
- introduce explicit musical note/event models
- isolate UST and USTX writers
- separate UI from generation logic

### Phase 3 — Musical intelligence

- candidate-based pitch scoring
- stronger phrase contours
- interval-based motif development
- improved Japanese accent contours
- note-importance modeling

### Phase 4 — Vocal expression

- intelligent vibrato
- portamento
- timing expression
- dynamic curves
- breath/rest modeling
- ornaments

### Phase 5 — Learning and style

- learn melodic tendencies from existing UST projects
- voicebank-specific tuning profiles
- style presets
- natural / pop / traditional / experimental tuning modes

## License

MIT — see the repository license for details.

## Author

**Ilya Minin (Eli)**

Artist / creative technologist working with generative audio, interactive installations, vocal synthesis, UTAU, and experimental Japanese media.

Repository: `ELIASADAMS/text-to-ust`
