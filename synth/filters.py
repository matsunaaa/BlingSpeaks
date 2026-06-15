"""Filter implementations for sound shaping."""

import numpy as np
from scipy.signal import butter, lfilter, sosfilt, iirpeak


def lowpass(signal, cutoff, sr=44100, order=4):
    """Apply a lowpass filter."""
    nyq = sr / 2
    normalized_cutoff = min(cutoff / nyq, 0.99)
    b, a = butter(order, normalized_cutoff, btype='low')
    return lfilter(b, a, signal)


def highpass(signal, cutoff, sr=44100, order=4):
    """Apply a highpass filter."""
    nyq = sr / 2
    normalized_cutoff = max(cutoff / nyq, 0.01)
    b, a = butter(order, normalized_cutoff, btype='high')
    return lfilter(b, a, signal)


def bandpass(signal, low, high, sr=44100, order=4):
    """Apply a bandpass filter."""
    nyq = sr / 2
    low_norm = max(low / nyq, 0.01)
    high_norm = min(high / nyq, 0.99)
    
    if low_norm >= high_norm:
        return signal
    
    b, a = butter(order, [low_norm, high_norm], btype='band')
    return lfilter(b, a, signal)


def resonant_filter(signal, cutoff, resonance, sr=44100):
    """
    Apply a resonant lowpass filter.
    
    resonance: 0-1, where higher values create more resonant peak
    """
    nyq = sr / 2
    normalized_cutoff = min(cutoff / nyq, 0.99)
    
    # Base lowpass
    q = 0.707 + resonance * 10  # Q factor from 0.707 to ~10
    b, a = butter(2, normalized_cutoff, btype='low')
    filtered = lfilter(b, a, signal)
    
    # Add resonant peak if resonance > 0
    if resonance > 0.1:
        peak_freq = cutoff / nyq
        if peak_freq < 0.99:
            b_peak, a_peak = iirpeak(peak_freq, q)
            filtered = lfilter(b_peak, a_peak, filtered) * (1 - resonance * 0.3)
    
    return filtered


def formant_filter(signal, formants, bandwidths=None, sr=44100):
    """
    Apply parallel formant filters to simulate vocal tract resonances.
    
    formants: list of center frequencies [F1, F2, F3, ...]
    bandwidths: list of bandwidths for each formant (default: auto-calculated)
    """
    if bandwidths is None:
        bandwidths = [f * 0.1 + 50 for f in formants]  # Wider at higher freqs
    
    output = np.zeros_like(signal)
    
    for freq, bw in zip(formants, bandwidths):
        low = max(20, freq - bw / 2)
        high = min(sr / 2 - 100, freq + bw / 2)
        
        if low < high:
            filtered = bandpass(signal, low, high, sr, order=2)
            output += filtered
    
    return output / max(len(formants), 1)


def comb_filter(signal, delay_ms, feedback=0.5, sr=44100):
    """Apply a comb filter for metallic/resonant effects."""
    delay_samples = int(delay_ms * sr / 1000)
    output = np.zeros(len(signal) + delay_samples)
    output[:len(signal)] = signal
    
    for i in range(delay_samples, len(output)):
        output[i] += feedback * output[i - delay_samples]
    
    return output[:len(signal)]


def apply_filter_envelope(signal, cutoff_start, cutoff_end, resonance=0.3, sr=44100):
    """Apply a filter with time-varying cutoff frequency."""
    n_samples = len(signal)
    block_size = sr // 100  # 10ms blocks
    output = np.zeros(n_samples)
    
    cutoff_curve = np.linspace(cutoff_start, cutoff_end, n_samples // block_size + 1)
    
    for i, cutoff in enumerate(cutoff_curve):
        start = i * block_size
        end = min(start + block_size, n_samples)
        if start >= n_samples:
            break
        output[start:end] = resonant_filter(signal[start:end], cutoff, resonance, sr)
    
    return output