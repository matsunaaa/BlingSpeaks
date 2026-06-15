# BlingSpeak

Procedural alien vocalization generator. Creates expressive non-verbal sounds using formant synthesis, pitch contours, and spectral processing.

## Features

- **Emotion Presets**: Curious, excited, startled, happy, sad, confused, and more
- **Custom Designer**: Full control over pitch, timbre, envelope, and effects
- **Sequence Generator**: Create multi-blip expressions with randomization

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How It Works

### Formant Synthesis

Human vowel sounds are characterized by resonant frequencies called formants. BlingSpeak synthesizes vocal-like sounds by:

1. Generating a source signal (mix of oscillators)
2. Passing through parallel bandpass filters tuned to vowel formants
3. Shaping with amplitude envelopes

Standard vowel formants (F1, F2, F3 in Hz):

| Vowel | F1  | F2   | F3   |
|-------|-----|------|------|
| ah    | 700 | 1200 | 2600 |
| ee    | 300 | 2700 | 3400 |
| oo    | 300 | 870  | 2250 |

### Pitch Contours

Expressiveness comes from how pitch changes over time:

- **Rising**: Builds energy or asks a question
- **Falling**: Resolves or expresses sadness
- **Question**: Rises sharply at the end
- **Exclaim**: Peaks early then falls
- **Wobble**: Vibrato-like movement
- **Nervous**: Irregular jitter

Each contour is generated as a frequency curve applied via phase accumulation:

```
phase[n] = phase[n-1] + 2π × freq[n] / sr
output[n] = sin(phase[n])
```

### Envelope Shaping

ADSR (Attack, Decay, Sustain, Release) envelopes control amplitude over time:

```
    1.0 |    /\
        |   /  \____
    S   |  /        \____
        | /              \
    0.0 |/________________\____
        A   D    S      R
```

### Effects

Post-processing adds character:

- **Ring Modulation**: `y(t) = x(t) × sin(2πf_c × t)` creates metallic, alien tones
- **Bitcrushing**: Reduces bit depth for digital grit
- **Chorus/Flanger**: Modulated delays for thickness
- **Spectral Shimmer**: Pitch-shifted layer for sparkle
- **Granular Scatter**: Redistributes audio fragments for texture

## Project Structure

```
blingspeak/
├── app.py              # Streamlit interface
├── synth/
│   ├── oscillators.py  # Waveform generators
│   ├── filters.py      # Lowpass, bandpass, formant filters
│   ├── envelopes.py    # ADSR and other envelope shapes
│   ├── contours.py     # Pitch contour generators
│   ├── formant_synth.py # Vowel synthesis
│   └── generator.py    # Main sound generation
├── effects/
│   └── effects.py      # Post-processing effects
├── presets.py          # Emotion presets and categories
├── utils.py            # Audio utilities
└── README.md
```

## Technical Details

- Sample rate: 44100 Hz
- All synthesis from first principles using NumPy/SciPy
- No pre-recorded samples or black-box audio libraries
- Formant filter implemented as parallel bandpass filterbank
- Phase accumulation for time-varying frequency synthesis

## Credits

Built for the null.pointer._exception alien crew. Bling approved.