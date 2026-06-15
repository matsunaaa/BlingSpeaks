"""Basic oscillator functions for sound synthesis."""

import numpy as np


def sine_wave(freq, duration, sr=44100, phase=0):
    """Generate a sine wave at a fixed frequency."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t + phase)


def sawtooth_wave(freq, duration, sr=44100):
    """Generate a sawtooth wave at a fixed frequency."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return 2 * (t * freq - np.floor(0.5 + t * freq))


def pulse_wave(freq, duration, duty=0.5, sr=44100):
    """Generate a pulse wave with variable duty cycle."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    phase = (t * freq) % 1.0
    return np.where(phase < duty, 1.0, -1.0)


def triangle_wave(freq, duration, sr=44100):
    """Generate a triangle wave at a fixed frequency."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    phase = (t * freq) % 1.0
    return 4 * np.abs(phase - 0.5) - 1


def noise(duration, sr=44100):
    """Generate white noise."""
    return np.random.uniform(-1, 1, int(sr * duration))


def pink_noise(duration, sr=44100):
    """Generate pink noise using the Voss-McCartney algorithm."""
    n_samples = int(sr * duration)
    n_rows = 16
    
    array = np.random.randn(n_rows, n_samples // n_rows + 1)
    reshaped = np.zeros(n_samples)
    
    for i in range(n_samples):
        idx = i // (2 ** np.arange(n_rows)) % array.shape[1]
        reshaped[i] = np.sum(array[np.arange(n_rows), idx.astype(int)])
    
    return reshaped / np.max(np.abs(reshaped))


def sine_from_freq_curve(freq_curve, sr=44100):
    """Generate a sine wave with time-varying frequency."""
    phase = np.cumsum(2 * np.pi * freq_curve / sr)
    return np.sin(phase)


def saw_from_freq_curve(freq_curve, sr=44100):
    """Generate a sawtooth wave with time-varying frequency."""
    phase = np.cumsum(freq_curve / sr) % 1.0
    return 2 * phase - 1


def mix_oscillators(freq_curve, mix_params, sr=44100):
    """
    Mix multiple oscillator types with time-varying frequency.
    
    mix_params: dict with keys 'sine', 'saw', 'pulse', 'triangle', 'noise'
                values are mix amounts (0-1)
    """
    n_samples = len(freq_curve)
    duration = n_samples / sr
    output = np.zeros(n_samples)
    
    phase = np.cumsum(2 * np.pi * freq_curve / sr)
    
    if mix_params.get('sine', 0) > 0:
        output += mix_params['sine'] * np.sin(phase)
    
    if mix_params.get('saw', 0) > 0:
        saw_phase = np.cumsum(freq_curve / sr) % 1.0
        output += mix_params['saw'] * (2 * saw_phase - 1)
    
    if mix_params.get('pulse', 0) > 0:
        pulse_phase = np.cumsum(freq_curve / sr) % 1.0
        duty = mix_params.get('pulse_duty', 0.5)
        output += mix_params['pulse'] * np.where(pulse_phase < duty, 1.0, -1.0)
    
    if mix_params.get('triangle', 0) > 0:
        tri_phase = np.cumsum(freq_curve / sr) % 1.0
        output += mix_params['triangle'] * (4 * np.abs(tri_phase - 0.5) - 1)
    
    if mix_params.get('noise', 0) > 0:
        output += mix_params['noise'] * np.random.uniform(-1, 1, n_samples)
    
    return output