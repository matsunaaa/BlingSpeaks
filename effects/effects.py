"""Post-processing effects for BlingSpeak sounds."""

import numpy as np
from scipy.signal import hilbert


def ring_modulate(audio, carrier_freq=200, mix=0.5, sr=44100):
    """Apply ring modulation for metallic/alien quality."""
    t = np.arange(len(audio)) / sr
    carrier = np.sin(2 * np.pi * carrier_freq * t)
    modulated = audio * carrier
    return audio * (1 - mix) + modulated * mix


def bitcrush(audio, bit_depth=8, mix=0.5, sr=44100):
    """Reduce bit depth for crunchy digital texture."""
    levels = 2 ** bit_depth
    crushed = np.round(audio * levels) / levels
    return audio * (1 - mix) + crushed * mix


def chorus(audio, rate=1.5, depth=0.003, mix=0.4, sr=44100):
    """Add chorus for thickness."""
    n_samples = len(audio)
    t = np.arange(n_samples) / sr
    
    delay_samples = int(0.025 * sr)
    mod_samples = int(depth * sr)
    
    output = np.zeros(n_samples + delay_samples + mod_samples)
    output[:n_samples] = audio
    
    modulation = mod_samples * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))
    
    for i in range(n_samples):
        delay = int(delay_samples + modulation[i])
        if i + delay < len(output):
            output[i] += audio[i] * mix
    
    return output[:n_samples]


def flanger(audio, rate=0.5, depth=0.002, feedback=0.3, mix=0.5, sr=44100):
    """Apply flanging effect."""
    n_samples = len(audio)
    t = np.arange(n_samples) / sr
    
    max_delay = int(depth * sr)
    output = audio.copy()
    buffer = np.zeros(max_delay + 1)
    
    for i in range(n_samples):
        delay = int(max_delay * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t[i])))
        buffer_idx = i % (max_delay + 1)
        
        delayed = buffer[(buffer_idx - delay) % (max_delay + 1)]
        output[i] = audio[i] + delayed * mix
        buffer[buffer_idx] = audio[i] + delayed * feedback
    
    return output


def reverb_simple(audio, decay=0.4, delays=None, sr=44100):
    """Simple comb filter reverb."""
    if delays is None:
        delays = [0.029, 0.037, 0.041, 0.053]
    
    output = audio.copy()
    
    for delay in delays:
        delay_samples = int(delay * sr)
        delayed = np.zeros(len(audio))
        if delay_samples < len(audio):
            delayed[delay_samples:] = audio[:-delay_samples] * decay
        output += delayed
    
    return output / (1 + len(delays) * decay)


def spectral_shimmer(audio, shift_cents=1200, mix=0.3, sr=44100):
    """Add shimmering octave-shifted layer via spectral processing."""
    from scipy.fft import fft, ifft
    
    n = len(audio)
    spectrum = fft(audio)
    
    ratio = 2 ** (shift_cents / 1200)
    new_spectrum = np.zeros_like(spectrum)
    
    for i in range(n // 2):
        new_idx = int(i * ratio)
        if new_idx < n // 2:
            new_spectrum[new_idx] = spectrum[i]
            new_spectrum[n - new_idx - 1] = spectrum[n - i - 1]
    
    shifted = np.real(ifft(new_spectrum))
    
    return audio * (1 - mix) + shifted * mix


def granular_scatter(audio, grain_size=0.03, scatter=0.5, density=1.0, sr=44100):
    """Granular processing for textured sounds."""
    grain_samples = int(grain_size * sr)
    n_grains = int(len(audio) / grain_samples * density)
    
    output = np.zeros(len(audio))
    window = np.hanning(grain_samples)
    
    for _ in range(n_grains):
        src_pos = np.random.randint(0, max(1, len(audio) - grain_samples))
        
        scatter_range = int(scatter * len(audio))
        dest_pos = src_pos + np.random.randint(-scatter_range // 2, scatter_range // 2)
        dest_pos = max(0, min(len(audio) - grain_samples, dest_pos))
        
        grain = audio[src_pos:src_pos + grain_samples] * window
        
        output[dest_pos:dest_pos + len(grain)] += grain
    
    return output


def apply_effects_chain(audio, effects_list, sr=44100):
    """
    Apply a chain of effects.
    
    effects_list: list of tuples (effect_name, params_dict)
    """
    effect_functions = {
        'ring_mod': ring_modulate,
        'bitcrush': bitcrush,
        'chorus': chorus,
        'flanger': flanger,
        'reverb': reverb_simple,
        'shimmer': spectral_shimmer,
        'granular': granular_scatter,
    }
    
    output = audio.copy()
    
    for effect_name, params in effects_list:
        if effect_name in effect_functions:
            func = effect_functions[effect_name]
            output = func(output, sr=sr, **params)
    
    return output