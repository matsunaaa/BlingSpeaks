"""Formant-based vocal synthesis."""

import numpy as np
from synth.oscillators import mix_oscillators, noise
from synth.filters import formant_filter, lowpass


# Standard vowel formants (F1, F2, F3) in Hz
VOWEL_FORMANTS = {
    'a': [700, 1200, 2600],
    'e': [500, 1700, 2500],
    'i': [300, 2700, 3400],
    'o': [450, 800, 2600],
    'u': [300, 870, 2250],
    'ae': [660, 1700, 2400],
    'uh': [600, 1000, 2400],
    'er': [500, 1500, 1700],
}


def interpolate_formants(formants1, formants2, t):
    """Interpolate between two sets of formants."""
    return [f1 + (f2 - f1) * t for f1, f2 in zip(formants1, formants2)]


def get_formant_trajectory(vowel_sequence, duration, sr=44100):
    """
    Create a trajectory through vowel formants.
    
    vowel_sequence: list of vowels, e.g., ['u', 'i'] for "oo-ee"
    Returns: array of shape (n_samples, 3) with F1, F2, F3 values
    """
    n_samples = int(sr * duration)
    n_vowels = len(vowel_sequence)
    
    if n_vowels == 1:
        formants = VOWEL_FORMANTS.get(vowel_sequence[0], VOWEL_FORMANTS['a'])
        return np.tile(formants, (n_samples, 1))
    
    trajectory = np.zeros((n_samples, 3))
    samples_per_segment = n_samples // (n_vowels - 1)
    
    for i in range(n_vowels - 1):
        start_formants = VOWEL_FORMANTS.get(vowel_sequence[i], VOWEL_FORMANTS['a'])
        end_formants = VOWEL_FORMANTS.get(vowel_sequence[i + 1], VOWEL_FORMANTS['a'])
        
        start_idx = i * samples_per_segment
        end_idx = start_idx + samples_per_segment if i < n_vowels - 2 else n_samples
        
        for j in range(end_idx - start_idx):
            t = j / samples_per_segment
            trajectory[start_idx + j] = interpolate_formants(start_formants, end_formants, t)
    
    return trajectory


def synthesize_vowel(vowel, freq, duration, breathiness=0.1, sr=44100):
    """
    Synthesize a vowel sound at a given fundamental frequency.
    
    vowel: vowel character ('a', 'e', 'i', 'o', 'u', etc.)
    freq: fundamental frequency in Hz
    breathiness: 0-1, amount of noise to add
    """
    n_samples = int(sr * duration)
    formants = VOWEL_FORMANTS.get(vowel, VOWEL_FORMANTS['a'])
    
    t = np.linspace(0, duration, n_samples)
    
    # Glottal pulse approximation (sawtooth)
    source = np.zeros(n_samples)
    phase = (t * freq) % 1.0
    source = 2 * phase - 1
    
    # Add breathiness
    if breathiness > 0:
        breath = noise(duration, sr)
        breath = lowpass(breath, 3000, sr)
        source = source * (1 - breathiness) + breath * breathiness
    
    # Apply formant filtering
    output = formant_filter(source, formants, sr=sr)
    
    return output


def synthesize_vowel_trajectory(vowel_sequence, freq_contour, duration, breathiness=0.1, sr=44100):
    """
    Synthesize a sound that moves through vowel formants with a pitch contour.
    
    vowel_sequence: list of vowels to move through
    freq_contour: array of frequencies over time
    """
    n_samples = int(sr * duration)
    
    # Ensure freq_contour matches duration
    if len(freq_contour) != n_samples:
        freq_contour = np.interp(
            np.linspace(0, 1, n_samples),
            np.linspace(0, 1, len(freq_contour)),
            freq_contour
        )
    
    # Generate source with time-varying pitch
    phase = np.cumsum(2 * np.pi * freq_contour / sr)
    source = np.sin(phase) * 0.5 + (np.cumsum(freq_contour / sr) % 1.0 * 2 - 1) * 0.5
    
    # Add breathiness
    if breathiness > 0:
        breath = lowpass(noise(duration, sr), 3000, sr)
        source = source * (1 - breathiness) + breath * breathiness
    
    # Get formant trajectory
    formant_trajectory = get_formant_trajectory(vowel_sequence, duration, sr)
    
    # Apply time-varying formant filter (block-based)
    block_size = sr // 50
    output = np.zeros(n_samples)
    
    for i in range(0, n_samples, block_size):
        end = min(i + block_size, n_samples)
        mid_idx = (i + end) // 2
        formants = formant_trajectory[mid_idx]
        output[i:end] = formant_filter(source[i:end], formants, sr=sr)
    
    return output


def alien_vowel(base_freq, duration, formant_shift=1.2, breathiness=0.2, vowel='o', sr=44100):
    """
    Synthesize an alien-like vowel by shifting formants to unusual ranges.
    
    formant_shift: multiplier for formant frequencies (>1 = smaller vocal tract)
    """
    formants = VOWEL_FORMANTS.get(vowel, VOWEL_FORMANTS['o'])
    shifted_formants = [f * formant_shift for f in formants]
    
    n_samples = int(sr * duration)
    t = np.linspace(0, duration, n_samples)
    
    # Slightly inharmonic source for alien quality
    source = np.sin(2 * np.pi * base_freq * t)
    source += 0.3 * np.sin(2 * np.pi * base_freq * 2.02 * t)
    source += 0.15 * np.sin(2 * np.pi * base_freq * 3.01 * t)
    
    if breathiness > 0:
        breath = lowpass(noise(duration, sr), 4000, sr)
        source = source * (1 - breathiness) + breath * breathiness
    
    output = formant_filter(source, shifted_formants, sr=sr)
    
    return output