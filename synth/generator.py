"""Main sound generator that combines all synthesis components."""

import numpy as np
from .oscillators import mix_oscillators, noise
from .filters import formant_filter, lowpass, resonant_filter, apply_filter_envelope
from .envelopes import adsr_envelope, pluck_envelope, swell_envelope, tremolo_envelope
from .contours import (
    flat_contour, rising_contour, falling_contour, question_contour,
    exclaim_contour, wobble_contour, nervous_contour, chirp_contour, stutter_contour
)
from .formant_synth import VOWEL_FORMANTS, synthesize_vowel_trajectory, alien_vowel
from utils import normalize, fade_in_out


# Contour functions mapped by name
CONTOUR_FUNCTIONS = {
    'flat': flat_contour,
    'rising': rising_contour,
    'falling': falling_contour,
    'question': question_contour,
    'exclaim': exclaim_contour,
    'wobble': wobble_contour,
    'nervous': nervous_contour,
}


def generate_bling_sound(
    # Pitch parameters
    base_freq=500,
    contour='question',
    contour_amount=0.3,
    vibrato_rate=5,
    vibrato_depth=0.02,
    
    # Timbre parameters
    oscillator_mix=None,
    vowel='o',
    formant_shift=1.0,
    breathiness=0.1,
    brightness=0.7,
    
    # Envelope parameters
    duration=0.3,
    attack=0.02,
    decay=0.1,
    sustain=0.6,
    release=0.1,
    
    # Modulation
    tremolo_rate=0,
    tremolo_depth=0,
    
    # Output
    sr=44100
):
    """
    Generate a single Bling-style vocal blip.
    
    Returns: numpy array of audio samples
    """
    n_samples = int(sr * duration)
    
    # Default oscillator mix: mostly sine with some character
    if oscillator_mix is None:
        oscillator_mix = {'sine': 0.6, 'saw': 0.2, 'pulse': 0.1, 'noise': 0.1}
    
    # Generate pitch contour
    contour_func = CONTOUR_FUNCTIONS.get(contour, flat_contour)

    # Dynamically determine the correct kwarg name for the amount parameter
    if contour == 'falling':
        contour_kwargs = {'fall_amount': contour_amount}
    elif contour == 'exclaim':
        contour_kwargs = {'peak_amount': contour_amount}
    elif contour in ['wobble', 'question']:
        contour_kwargs = {'depth': contour_amount} if contour == 'wobble' else {'rise_amount': contour_amount}
    elif contour in ['flat', 'nervous']:
        contour_kwargs = {}
    else:
        contour_kwargs = {'rise_amount': contour_amount}

    freq_contour = contour_func(base_freq, duration, sr=sr, **contour_kwargs)
    
    # Add vibrato on top of contour
    if vibrato_depth > 0:
        t = np.linspace(0, duration, n_samples)
        vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        freq_contour = freq_contour * vibrato
    
    # Generate source signal
    source = mix_oscillators(freq_contour, oscillator_mix, sr=sr)
    
    # Add breathiness
    if breathiness > 0:
        breath = lowpass(noise(duration, sr), 3000, sr)
        source = source * (1 - breathiness) + breath * breathiness
    
    # Get formants and apply shift
    formants = VOWEL_FORMANTS.get(vowel, VOWEL_FORMANTS['o'])
    shifted_formants = [f * formant_shift for f in formants]
    
    # Apply formant filtering
    output = formant_filter(source, shifted_formants, sr=sr)
    
    # Apply brightness (lowpass filter)
    cutoff = 1000 + brightness * 7000  # 1kHz to 8kHz
    output = lowpass(output, cutoff, sr)
    
    # Generate amplitude envelope
    envelope = adsr_envelope(duration, attack, decay, sustain, release, sr)
    
    # Apply tremolo if specified
    if tremolo_depth > 0 and tremolo_rate > 0:
        trem = tremolo_envelope(duration, tremolo_rate, tremolo_depth, sr)
        envelope = envelope * trem
    
    # Apply envelope
    output = output * envelope
    
    # Fade to avoid clicks
    output = fade_in_out(output, fade_in=0.005, fade_out=0.01, sr=sr)
    
    return normalize(output)


def generate_blip_sequence(
    n_blips=3,
    base_freq=500,
    freq_variation=0.2,
    duration_range=(0.1, 0.4),
    gap_range=(0.05, 0.15),
    contour_options=None,
    vowel_options=None,
    **kwargs
):
    """
    Generate a sequence of blips for more complex Bling expressions.
    
    Returns: numpy array of concatenated blips with gaps
    """
    sr = kwargs.get('sr', 44100)
    
    if contour_options is None:
        contour_options = ['question', 'flat', 'rising', 'falling']
    
    if vowel_options is None:
        vowel_options = ['o', 'u', 'i', 'a']
    
    segments = []
    
    for i in range(n_blips):
        # Randomize parameters
        freq = base_freq * (1 + np.random.uniform(-freq_variation, freq_variation))
        duration = np.random.uniform(*duration_range)
        contour = np.random.choice(contour_options)
        vowel = np.random.choice(vowel_options)
        
        # Generate blip
        blip = generate_bling_sound(
            base_freq=freq,
            contour=contour,
            duration=duration,
            vowel=vowel,
            **kwargs
        )
        segments.append(blip)
        
        # Add gap (silence) between blips
        if i < n_blips - 1:
            gap_duration = np.random.uniform(*gap_range)
            gap = np.zeros(int(sr * gap_duration))
            segments.append(gap)
    
    return np.concatenate(segments)


def generate_expression(emotion, duration=0.4, intensity=0.7, sr=44100):
    """
    Generate a Bling sound based on an emotion preset.
    
    emotion: 'curious', 'excited', 'startled', 'happy', 'confused', 'agreeing', 'sad'
    intensity: 0-1, how pronounced the expression is
    """
    # Base parameters that vary by emotion
    params = {
        'curious': {
            'base_freq': 600,
            'contour': 'question',
            'contour_amount': 0.3 * intensity,
            'vowel': 'o',
            'formant_shift': 1.2,
            'attack': 0.05,
            'brightness': 0.6,
        },
        'excited': {
            'base_freq': 800,
            'contour': 'exclaim',
            'contour_amount': 0.4 * intensity,
            'vowel': 'i',
            'formant_shift': 1.4,
            'attack': 0.01,
            'brightness': 0.9,
            'tremolo_rate': 8,
            'tremolo_depth': 0.15 * intensity,
        },
        'startled': {
            'base_freq': 900,
            'contour': 'falling',
            'contour_amount': 0.5 * intensity,
            'vowel': 'ae',
            'formant_shift': 1.5,
            'attack': 0.005,
            'decay': 0.05,
            'brightness': 1.0,
        },
        'happy': {
            'base_freq': 650,
            'contour': 'rising',
            'contour_amount': 0.25 * intensity,
            'vowel': 'i',
            'formant_shift': 1.3,
            'attack': 0.03,
            'brightness': 0.8,
            'vibrato_rate': 6,
            'vibrato_depth': 0.02 * intensity,
        },
        'confused': {
            'base_freq': 500,
            'contour': 'wobble',
            'contour_amount': 0.08 * intensity,
            'vowel': 'uh',
            'formant_shift': 1.1,
            'attack': 0.08,
            'brightness': 0.5,
        },
        'agreeing': {
            'base_freq': 550,
            'contour': 'falling',
            'contour_amount': 0.15 * intensity,
            'vowel': 'u',
            'formant_shift': 1.0,
            'attack': 0.02,
            'sustain': 0.8,
            'brightness': 0.6,
        },
        'sad': {
            'base_freq': 350,
            'contour': 'falling',
            'contour_amount': 0.3 * intensity,
            'vowel': 'o',
            'formant_shift': 0.9,
            'attack': 0.1,
            'brightness': 0.3,
        },
        'thinking': {
            'base_freq': 450,
            'contour': 'nervous',
            'contour_amount': 0.1,
            'vowel': 'er',
            'formant_shift': 1.0,
            'attack': 0.06,
            'brightness': 0.5,
        },
        'delighted': {
            'base_freq': 750,
            'contour': 'exclaim',
            'contour_amount': 0.35 * intensity,
            'vowel': 'i',
            'formant_shift': 1.5,
            'attack': 0.01,
            'brightness': 0.95,
            'vibrato_rate': 7,
            'vibrato_depth': 0.03 * intensity,
        },
    }
    
    preset = params.get(emotion, params['curious'])
    preset['duration'] = duration
    preset['sr'] = sr
    
    return generate_bling_sound(**preset)