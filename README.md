# BlingSpeak
https://blingspeaks.streamlit.app/ 

A procedural alien vocalization generator. Creates expressive non-verbal sounds using formant synthesis, pitch contours, and spectral processing. Now with multi-character conversation generation.

## Features

- **Emotion Presets**: Curious, excited, startled, happy, sad, confused, and more
- **Custom Designer**: Full control over pitch, timbre, envelope, and effects
- **Sequence Generator**: Create multi-blip expressions with randomization
- **Alien Chatter**: Generate conversations between multiple alien characters with spatial audio and emotional arcs

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

### Alien Chatter: Conversation Generation

The Alien Chatter module generates multi-character conversations with realistic timing and spatial positioning.

#### Turn-Taking Model

Conversations follow probabilistic turn-taking rules:

```
P(speaker_change) = f(utterance_length, emotion, interruption_tendency)
```

Each character has traits affecting their speech patterns:
- **Interruption tendency**: How likely to cut others off
- **Response delay**: Pause before responding
- **Verbosity**: How long their utterances typically are

#### Emotional State Machine

Conversations have emotional arcs that evolve over time:

```
    Emotion
    Intensity
        │
    1.0 │      ╱╲
        │     ╱  ╲    ╱╲
    0.5 │    ╱    ╲  ╱  ╲
        │   ╱      ╲╱    ╲
    0.0 │──╱──────────────╲──
        └──────────────────────▶ Time
           intro  tension  resolve
```

States: `neutral → curious → excited → tense → resolved`

Transitions affect:
- Pitch range (tense = higher, resolved = lower)
- Speech rate (excited = faster)
- Interruption frequency (tense = more interruptions)

#### Spatial Audio

Characters are positioned in stereo field:

```
     Left ◄─────────────────► Right
      -1         0         +1
       │         │         │
    [Char A]  [Char C]  [Char B]
```

Panning uses constant-power law to maintain perceived loudness:

```
left_gain = cos(θ × π/2)
right_gain = sin(θ × π/2)

where θ = (pan + 1) / 2, pan ∈ [-1, 1]
```

#### Distance Modeling

Characters can be positioned at different distances:

```
Near (1.0):  Full volume, bright (no filtering)
Mid (0.5):   -6dB, slight lowpass at 8kHz
Far (0.2):   -14dB, lowpass at 4kHz, more reverb
```

Implemented as:
```
gain = distance²  (inverse square approximation)
cutoff = 2000 + distance × 10000
reverb_mix = 0.4 × (1 - distance)
```

#### Overlap and Interruption

When characters interrupt:

```
Speaker A: ────────────┐
                       │ overlap region
Speaker B:         ┌───┴────────────
                   │
            interrupt point
```

Overlap crossfades use equal-power curves to avoid volume dips:

```
fade_out = cos(t × π/2)²
fade_in = sin(t × π/2)²
```

### Character Voice Profiles

Each character has a distinct voice built from synthesis parameters:

| Parameter | Null | Smol | Mimo | Yun | Bling |
|-----------|------|------|------|-----|-------|
| Base Freq | 180 | 600 | 450 | 380 | 700 |
| Formant Shift | 0.85 | 1.4 | 1.2 | 1.1 | 1.5 |
| Breathiness | 0.05 | 0.15 | 0.1 | 0.2 | 0.1 |
| Vibrato | Low | High | Medium | Medium | Random |
| Contours | Flat, Falling | Question, Nervous | Rising, Flat | Rising, Wobble | Random |

## Project Structure

```
blingspeak/
├── app.py                  # Streamlit interface
├── synth/
│   ├── oscillators.py      # Waveform generators
│   ├── filters.py          # Lowpass, bandpass, formant filters
│   ├── envelopes.py        # ADSR and other envelope shapes
│   ├── contours.py         # Pitch contour generators
│   ├── formant_synth.py    # Vowel synthesis
│   └── generator.py        # Main sound generation
├── effects/
│   └── effects.py          # Post-processing effects
├── chatter/
│   ├── __init__.py         # Chatter module exports
│   ├── characters.py       # Character voice profiles and traits
│   ├── conversation.py     # Turn-taking and conversation generation
│   ├── emotions.py         # Emotional arc state machine
│   └── spatial.py          # Panning, distance, room simulation
├── presets.py              # Emotion presets and categories
├── utils.py                # Audio utilities
└── README.md
```

## Alien Chatter Conversation Modes

### Scripted Mode
Define exact sequence of speakers and emotions:

```python
script = [
    ('smol', 'curious', 'short'),
    ('mimo', 'explaining', 'medium'),
    ('null', 'annoyed', 'short'),
    ('smol', 'nervous', 'short'),
]
```

### Generative Mode
Set initial conditions and let the conversation evolve:

```python
config = {
    'characters': ['null', 'smol', 'mimo'],
    'duration': 10.0,  # seconds
    'initial_emotion': 'curious',
    'arc': 'tension_release',  # or 'escalating', 'calming', 'chaotic'
    'interruption_level': 0.3,
}
```

### Reaction Mode
One character responds to audio input with appropriate emotion:

```python
# Analyze input audio energy/pitch
# Generate contextual response
response = generate_reaction(
    input_audio,
    character='smol',
    reaction_type='surprised'  # or 'agreeing', 'questioning', 'dismissive'
)
```

## Technical Details

- Sample rate: 44100 Hz
- Output: Mono or stereo WAV
- All synthesis from first principles using NumPy/SciPy; No pre-recorded samples
- Formant filter implemented as parallel bandpass filterbank
- Spatial audio uses constant-power panning
- Conversation timing uses Poisson-distributed gaps for natural feel

## Example: Generating a Simple Conversation

```python
from chatter import generate_conversation, CHARACTER_PROFILES

conversation = generate_conversation(
    characters=['null', 'smol'],
    num_exchanges=4,
    emotional_arc='curious_to_resolved',
    include_interruptions=True,
    spatial_mode='stereo',  # null on left, smol on right
)

# Returns stereo audio array
```

## Credits

Built for the null.pointer._exception alien crew. 👽