"""Envelope generators for amplitude and modulation shaping."""

import numpy as np


def adsr_envelope(duration, attack=0.05, decay=0.1, sustain_level=0.7, release=0.15, sr=44100):
    """
    Generate an ADSR envelope.
    
    Times are in seconds, sustain_level is 0-1.
    Sustain duration fills the remaining time.
    """
    n_samples = int(sr * duration)
    envelope = np.zeros(n_samples)
    
    a_samples = min(int(attack * sr), n_samples // 4)
    d_samples = min(int(decay * sr), n_samples // 4)
    r_samples = min(int(release * sr), n_samples // 4)
    s_samples = max(0, n_samples - a_samples - d_samples - r_samples)
    
    idx = 0
    
    # Attack
    if a_samples > 0:
        envelope[idx:idx + a_samples] = np.linspace(0, 1, a_samples)
        idx += a_samples
    
    # Decay
    if d_samples > 0:
        envelope[idx:idx + d_samples] = np.linspace(1, sustain_level, d_samples)
        idx += d_samples
    
    # Sustain
    if s_samples > 0:
        envelope[idx:idx + s_samples] = sustain_level
        idx += s_samples
    
    # Release
    if r_samples > 0:
        current_level = envelope[idx - 1] if idx > 0 else sustain_level
        envelope[idx:idx + r_samples] = np.linspace(current_level, 0, r_samples)
    
    return envelope


def pluck_envelope(duration, attack=0.005, decay_time=0.3, sr=44100):
    """Generate a pluck-like envelope with fast attack and exponential decay."""
    n_samples = int(sr * duration)
    a_samples = int(attack * sr)
    
    envelope = np.zeros(n_samples)
    
    # Fast attack
    if a_samples > 0:
        envelope[:a_samples] = np.linspace(0, 1, a_samples)
    
    # Exponential decay
    decay_samples = n_samples - a_samples
    if decay_samples > 0:
        t = np.linspace(0, duration - attack, decay_samples)
        envelope[a_samples:] = np.exp(-t / decay_time)
    
    return envelope


def swell_envelope(duration, swell_time=0.5, sr=44100):
    """Generate a swelling envelope that rises then falls."""
    n_samples = int(sr * duration)
    peak_sample = int(swell_time * n_samples)
    
    envelope = np.zeros(n_samples)
    
    # Rise
    if peak_sample > 0:
        envelope[:peak_sample] = np.linspace(0, 1, peak_sample) ** 2
    
    # Fall
    remaining = n_samples - peak_sample
    if remaining > 0:
        envelope[peak_sample:] = np.linspace(1, 0, remaining) ** 0.5
    
    return envelope


def tremolo_envelope(duration, rate=5, depth=0.3, sr=44100):
    """Generate a tremolo (amplitude modulation) envelope."""
    n_samples = int(sr * duration)
    t = np.linspace(0, duration, n_samples)
    return 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))


def random_envelope(duration, smoothness=0.1, sr=44100):
    """Generate a smoothed random envelope for organic variation."""
    n_samples = int(sr * duration)
    
    # Generate sparse random points
    n_points = max(3, int(duration / smoothness))
    random_points = np.random.uniform(0.3, 1.0, n_points)
    random_points[0] = 0
    random_points[-1] = 0
    
    # Interpolate to full length
    indices = np.linspace(0, n_points - 1, n_samples)
    envelope = np.interp(indices, np.arange(n_points), random_points)
    
    # Smooth
    from scipy.ndimage import gaussian_filter1d
    envelope = gaussian_filter1d(envelope, sigma=sr * 0.01)
    
    return envelope


def combine_envelopes(env1, env2, operation='multiply'):
    """Combine two envelopes with various operations."""
    min_len = min(len(env1), len(env2))
    e1, e2 = env1[:min_len], env2[:min_len]
    
    if operation == 'multiply':
        return e1 * e2
    elif operation == 'add':
        return np.clip(e1 + e2, 0, 1)
    elif operation == 'max':
        return np.maximum(e1, e2)
    elif operation == 'min':
        return np.minimum(e1, e2)
    else:
        return e1 * e2