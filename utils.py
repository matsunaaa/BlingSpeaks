"""Audio utilities for BlingSpeak."""

import numpy as np


def normalize(audio, target_peak=0.95):
    """Normalize audio to target peak amplitude."""
    peak = np.max(np.abs(audio))
    if peak > 0:
        return audio * (target_peak / peak)
    return audio


def fade_in_out(audio, fade_in=0.01, fade_out=0.01, sr=44100):
    """Apply fade in and fade out to avoid clicks."""
    fade_in_samples = int(fade_in * sr)
    fade_out_samples = int(fade_out * sr)
    
    audio = audio.copy()
    
    if fade_in_samples > 0 and fade_in_samples < len(audio):
        audio[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples)
    
    if fade_out_samples > 0 and fade_out_samples < len(audio):
        audio[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)
    
    return audio


def mix_signals(signals, weights=None):
    """Mix multiple signals together with optional weights."""
    if weights is None:
        weights = [1.0 / len(signals)] * len(signals)
    
    max_len = max(len(s) for s in signals)
    output = np.zeros(max_len)
    
    for signal, weight in zip(signals, weights):
        output[:len(signal)] += signal * weight
    
    return output


def resample_envelope(envelope, target_length):
    """Resample an envelope to a target length."""
    indices = np.linspace(0, len(envelope) - 1, target_length)
    return np.interp(indices, np.arange(len(envelope)), envelope)