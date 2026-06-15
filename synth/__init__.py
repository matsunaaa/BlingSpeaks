"""Synthesis modules for BlingSpeak."""

from synth.oscillators import (
    sine_wave, sawtooth_wave, pulse_wave, triangle_wave,
    noise, pink_noise, sine_from_freq_curve, mix_oscillators
)
from synth.filters import (
    lowpass, highpass, bandpass, resonant_filter,
    formant_filter, comb_filter, apply_filter_envelope
)
from synth.envelopes import (
    adsr_envelope, pluck_envelope, swell_envelope,
    tremolo_envelope, random_envelope, combine_envelopes
)
from synth.contours import (
    flat_contour, rising_contour, falling_contour, question_contour,
    exclaim_contour, wobble_contour, nervous_contour, slide_contour,
    chirp_contour, stutter_contour, combine_contours
)
from synth.formant_synth import (
    VOWEL_FORMANTS, synthesize_vowel, synthesize_vowel_trajectory, alien_vowel
)
from synth.generator import (
    generate_bling_sound, generate_blip_sequence, generate_expression
)