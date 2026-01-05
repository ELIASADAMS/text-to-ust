
# 響 Hiro UST

**Procedural UTAU `.ust` generator** for Japanese lyrics with mora-accurate parsing, motif memory, voice leading, and musical scales.
Built by Ilya Minin (Eli) - interactive installations & generative audio specialist.

## 🎛️ Purpose

Converts Romaji/Hiragana lyrics → UST files with **procedural melodies** that respect:
- Japanese phonetics (mora boundaries, gemination `っ`, yoon)
- Musical structure (phrase endings, motif repetition) 
- Voice ranges (Soprano→Bass)

## 🎵 Usage

```
[Verse]
きゃっきゃ うれし いたい さぶり
ゆびさき きりさけ あかい つゆ

[Chorus]  
いたみ いたみ きもちいい
```

**→** Single-click UST generation with melody, timing, dynamics.

## ✨ Core Mechanics

### **1. Mora Trie Parser**
```
Romaji → Hiragana → Phonemes (O(1) lookup)
っか → ['っ','ka'], きゃ → ['kya']
```
- Small tsu gemination (`っ`)
- Full yoon support (`kya`, `sha`, `nya`)
- Vowel/consonant timing differentiation

### **2. Procedural Melody Engine**
```
Voice Leading: Tight(±1) → Wild(±5) semitones
Motif Memory: Learns/reuses 4-note patterns (40% prob)
Phrase Structure: Resets to tonic/dominant every 6-12 notes
Chord Awareness: I-IV-V progression cycle
```

### **3. 20+ Scales**
```
- Major/Minor Pentatonic (Japanese traditional)
- Diatonic majors/minors (C→A)
- Whole Tone, Octatonic (generative/experimental)
- Chromatic, Blues, Hexatonic
```

## 🚀 Get Started

**EXE (Recommended)**
```bash
# Download from Releases
HiroUST_v4.1.exe → Double-click → Generate UST
```

**Python**
```bash
pip install tkinter  # Usually pre-installed
python hiro_ust.py
```

## 🎚️ Controls

| Section | Parameters | Effect |
|---------|------------|--------|
| **⏱️ Timing** | Tempo, Base Length, Line/Section Pauses | Song structure |
| **🎤 Voice** | Soprano(67)-Bass(48), Scale | Pitch range + palette |
| **🎵 Behavior** | Motif Memory, Lyrical Mode, Microtones, Chords | Melodic character |
| **⚙️ UST** | PreUtterance, Overlap, Intensity, Envelope | Rendering quality |

## 🎼 Modes

- **🎼 Motif Memory** - Remembers + varies 4-note patterns
- **🎭 Lyrical** - Vowels ↑ high, Consonants ↓ low  
- **♯ Microtones** - Quarter-tone vowel bends
- **🎸 Chords** - I(0-2), IV(3-4), V(5-7) beat cycle
- **📏 Intone** - Tight(1)→Wild(5) leap control

## 💾 Presets

Save/load complete configurations:
```
Pop_Idol.json, Horror_Ambient.json, Experimental.json
```

## 🧮 Technical

```
Parser: Trie-based O(n) mora lookup
Melody: Semi-procedual, semi-random
State: Persistent phrase/motif memory
Output: UTF-8-sig UST (UTAU v1.2 compatible)
```

## 🎨 By Ilya Minin (Eli)

**Background:** Interactive installations, generative audio (MAX/MSP) → UTAU, SynthV and Japan)))

**Eli_lab** - Moscow-based contemporary artist & creative technologist

**License:** MIT - Free for all uses
