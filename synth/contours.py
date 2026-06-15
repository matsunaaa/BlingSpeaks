"""Pitch contour generators for expressive intonation."""

import numpy as np


def flat_contour(base_freq, duration, sr=44100):
    """Constant pitch."""
    n_samples = int(sr * duration)
    return np.full(n_samples, base_freq)


def rising_contour(base_freq, duration, rise_amount=0.5, sr=44100):
    """Pitch rises over duration."""
    n_samples = int(sr * duration)
    t = np.linspace(0, 1, n_samples)
    return base_freq * (1 + rise_amount * t)


def falling_contour(base_freq, duration, fall_amount=0.5, sr=44100):
    """Pitch falls over duration."""
    n_samples = int(sr * duration)
    t = np.linspace(0, 1, n_samples)
    return base_freq * (1 + fall_amount * (1 - t))


def question_contour(base_freq, duration, rise_amount=0.3, sr=44100):
    """Pitch rises at the end like a question."""
    n_samples = int(sr * duration)
    t = np.linspace(0, 1, n_samples)
    return base_freq * (1 + rise_amount * (t ** 3))


def exclaim_contour(base_freq, duration, peak_amount=0.4, sr=44100):
    """Pitch peaks early then falls, like excitement."""
    n_samples = int(sr * duration)
    t = np.linspace(0, 1, n_samples)
    curve = np.exp(-((t - 0.2) ** 2) / 0.1)  # Peak at 20%
    return base_freq * (1 + peak_amount * curve)


def wobble_contour(base_freq, duration, rate=5, depth=0.05, sr=44100):
    """Vibrato-like pitch wobble."""
    n_samples = int(sr * duration)
    t = np.linspace(0, duration, n_samples)
    return base_freq * (1 + depth * np.sin(2 * np.pi * rate * t))


def nervous_contour(base_freq, duration, sr=44100):
    """Irregular, jittery pitch for nervous sounds."""
    n_samples = int(sr * duration)
    t = np.linspace(0, duration, n_samples)
    
    # Multiple overlapping wobbles at different rates
    wobble1 = 0.03 * np.sin(2 * np.pi * 7 * t)
    wobble2 = 0.02 * np.sin(2 * np.pi * 11 * t)
    wobble3 = 0.01 * np.random.randn(n_samples)
    
    # Smooth the random component
    from scipy.ndimage import gaussian_filter1d
    wobble3 = gaussian_filter1d(wobble3, sigma=100)
    
    return base_freq * (1 + wobble1 + wobble2 + wobble3)


def slide_contour(start_freq, end_freq, duration, curve='linear', sr=44100):
    """Slide from one pitch to another."""
    n_samples = int(sr * duration)
    t = np.linspace(0, 1, n_samples)
    
    if curve == 'linear':
        return start_freq + (end_freq - start_freq) * t
    elif curve == 'exponential':
        return start_freq * (end_freq / start_freq) ** t
    elif curve == 'ease_in':
        return start_freq + (end_freq - start_freq) * (t ** 2)
    elif curve == 'ease_out':
        return start_freq + (end_freq - start_freq) * (1 - (1 - t) ** 2)
    else:
        return start_freq + (end_freq - start_freq) * t


def chirp_contour(base_freq, duration, chirp_range=2.0, direction='up', sr=44100):
    """Rapid pitch sweep for chirpy sounds."""
    n_samples = int(sr * duration)
    t = np.linspace(0, 1, n_samples)
    
    if direction == 'up':
        return base_freq * (1 + (chirp_range - 1) * t)
    else:
        return base_freq * chirp_range * (1 - (chirp_range - 1) / chirp_range * t)


def stutter_contour(base_freq, duration, stutter_rate=10, variation=0.1, sr=44100):
    """Stuttering pitch for glitchy effects."""
    n_samples = int(sr * duration)
    
    # Create stepped random values
    n_steps = int(duration * stutter_rate)
    step_values = 1 + np.random.uniform(-variation, variation, n_steps)
    
    # Repeat each step
    samples_per_step = n_samples // n_steps
    contour = np.repeat(step_values, samples_per_step)
    
    # Pad or trim to exact length
    if len(contour) < n_samples:
        contour = np.pad(contour, (0, n_samples - len(contour)), mode='edge')
    else:
        contour = contour[:n_samples]
    
    return base_freq * contour


def combine_contours(contour1, contour2, blend=0.5):
    """Blend two pitch contours together."""
    min_len = min(len(contour1), len(contour2))
    return (1 - blend) * contour1[:min_len] + blend * contour2[:min_len]