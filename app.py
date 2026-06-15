"""BlingSpeak - Procedural alien vocalization generator."""

import streamlit as st
import numpy as np
import io
from scipy.io import wavfile

from synth import generate_bling_sound, generate_blip_sequence
from effects import apply_effects_chain
from presets import (
    EMOTION_PRESETS, PRESET_CATEGORIES, PARAMETER_RANGES,
    CONTOUR_OPTIONS, VOWEL_OPTIONS
)
from conversation import (
    CHARACTER_PROFILES, CONVERSATION_TEMPLATES,
    generate_conversation, generate_quick_exchange,
    generate_character_utterance, apply_stereo_pan
)
from utils import normalize


st.set_page_config(
    page_title="BlingSpeak",
    page_icon="⭐",
    layout="wide"
)

st.title("BlingSpeak")
st.markdown("*Procedural alien vocalization generator*")

# Initialize session state
if 'current_audio' not in st.session_state:
    st.session_state.current_audio = None
if 'current_audio_stereo' not in st.session_state:
    st.session_state.current_audio_stereo = False
if 'variation_seed' not in st.session_state:
    st.session_state.variation_seed = 42
if 'conversation_metadata' not in st.session_state:
    st.session_state.conversation_metadata = None


def audio_to_bytes(audio, sr=44100):
    """Convert numpy audio array to WAV bytes."""
    audio_normalized = np.clip(audio, -1, 1)
    audio_int16 = (audio_normalized * 32767).astype(np.int16)
    
    buffer = io.BytesIO()
    wavfile.write(buffer, sr, audio_int16)
    buffer.seek(0)
    return buffer


def generate_with_preset(preset_key, duration, intensity):
    """Generate audio using a preset."""
    preset = EMOTION_PRESETS[preset_key]
    params = preset['params'].copy()
    effects = preset.get('effects', [])
    
    if 'contour_amount' in params:
        params['contour_amount'] *= intensity
    if 'tremolo_depth' in params:
        params['tremolo_depth'] *= intensity
    if 'vibrato_depth' in params:
        params['vibrato_depth'] *= intensity
    
    params['duration'] = duration
    
    audio = generate_bling_sound(**params)
    
    if effects:
        audio = apply_effects_chain(audio, effects)
    
    return normalize(audio)


def generate_custom(params_dict, effects_list):
    """Generate audio with custom parameters."""
    audio = generate_bling_sound(**params_dict)
    
    if effects_list:
        audio = apply_effects_chain(audio, effects_list)
    
    return normalize(audio)


# Sidebar: Mode selection
mode = st.sidebar.radio(
    "Mode",
    ["Emotion Presets", "Custom Designer", "Sequence Generator", "Alien Chatter"]
)

sr = 44100

# ============================================================
# EMOTION PRESETS TAB
# ============================================================
if mode == "Emotion Presets":
    st.header("Emotion Presets")
    st.markdown("Generate expressive sounds based on emotional states.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        category = st.selectbox("Category", list(PRESET_CATEGORIES.keys()))
        
        preset_options = PRESET_CATEGORIES[category]
        preset_key = st.selectbox(
            "Emotion",
            preset_options,
            format_func=lambda x: EMOTION_PRESETS[x]['name']
        )
        
        st.caption(EMOTION_PRESETS[preset_key]['description'])
        
        st.markdown("---")
        duration = st.slider("Duration", 0.1, 1.0, 0.35, 0.05)
        intensity = st.slider("Intensity", 0.3, 1.0, 0.7, 0.1)
        
        if st.button("Generate", type="primary", use_container_width=True):
            audio = generate_with_preset(preset_key, duration, intensity)
            st.session_state.current_audio = audio
            st.session_state.current_audio_stereo = False
        
        if st.button("Generate Variation", use_container_width=True):
            st.session_state.variation_seed = np.random.randint(0, 10000)
            np.random.seed(st.session_state.variation_seed)
            
            preset = EMOTION_PRESETS[preset_key]
            params = preset['params'].copy()
            params['base_freq'] *= np.random.uniform(0.9, 1.1)
            params['formant_shift'] *= np.random.uniform(0.95, 1.05)
            params['duration'] = duration
            
            audio = generate_bling_sound(**params)
            effects = preset.get('effects', [])
            if effects:
                audio = apply_effects_chain(audio, effects)
            
            st.session_state.current_audio = normalize(audio)
            st.session_state.current_audio_stereo = False
    
    with col2:
        if st.session_state.current_audio is not None and not st.session_state.current_audio_stereo:
            st.subheader("Output")
            audio_bytes = audio_to_bytes(st.session_state.current_audio, sr)
            st.audio(audio_bytes, format='audio/wav')
            
            st.download_button(
                "Download WAV",
                audio_bytes,
                file_name=f"bling_{preset_key}.wav",
                mime="audio/wav"
            )
            
            st.subheader("Waveform")
            import plotly.graph_objects as go
            
            audio = st.session_state.current_audio
            time_axis = np.arange(len(audio)) / sr
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=time_axis,
                y=audio,
                mode='lines',
                line=dict(color='#00ff88', width=1)
            ))
            fig.update_layout(
                xaxis_title="Time (s)",
                yaxis_title="Amplitude",
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0.1)',
            )
            st.plotly_chart(fig, use_container_width=True)


# ============================================================
# CUSTOM DESIGNER TAB
# ============================================================
elif mode == "Custom Designer":
    st.header("Custom Designer")
    st.markdown("Design your own Bling sound from scratch.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Pitch")
        base_freq = st.slider("Base Frequency (Hz)", *PARAMETER_RANGES['base_freq'])
        contour = st.selectbox("Contour Shape", CONTOUR_OPTIONS)
        contour_amount = st.slider("Contour Amount", *PARAMETER_RANGES['contour_amount'])
        vibrato_rate = st.slider("Vibrato Rate (Hz)", *PARAMETER_RANGES['vibrato_rate'])
        vibrato_depth = st.slider("Vibrato Depth", *PARAMETER_RANGES['vibrato_depth'])
    
    with col2:
        st.subheader("Timbre")
        vowel = st.selectbox("Vowel Shape", VOWEL_OPTIONS)
        formant_shift = st.slider("Formant Shift", *PARAMETER_RANGES['formant_shift'])
        breathiness = st.slider("Breathiness", *PARAMETER_RANGES['breathiness'])
        brightness = st.slider("Brightness", *PARAMETER_RANGES['brightness'])
        
        st.subheader("Oscillator Mix")
        osc_sine = st.slider("Sine", 0.0, 1.0, 0.6)
        osc_saw = st.slider("Sawtooth", 0.0, 1.0, 0.2)
        osc_noise = st.slider("Noise", 0.0, 1.0, 0.1)
    
    with col3:
        st.subheader("Envelope")
        duration = st.slider("Duration (s)", *PARAMETER_RANGES['duration'])
        attack = st.slider("Attack (s)", *PARAMETER_RANGES['attack'])
        decay = st.slider("Decay (s)", *PARAMETER_RANGES['decay'])
        sustain = st.slider("Sustain Level", *PARAMETER_RANGES['sustain'])
        release = st.slider("Release (s)", *PARAMETER_RANGES['release'])
        
        st.subheader("Tremolo")
        tremolo_rate = st.slider("Tremolo Rate (Hz)", *PARAMETER_RANGES['tremolo_rate'])
        tremolo_depth = st.slider("Tremolo Depth", *PARAMETER_RANGES['tremolo_depth'])
    
    st.markdown("---")
    st.subheader("Effects")
    
    eff_col1, eff_col2, eff_col3 = st.columns(3)
    
    with eff_col1:
        use_ring_mod = st.checkbox("Ring Modulation")
        if use_ring_mod:
            ring_freq = st.slider("Carrier Freq (Hz)", 20, 2000, 150)
            ring_mix = st.slider("Ring Mix", 0.0, 1.0, 0.3)
    
    with eff_col2:
        use_bitcrush = st.checkbox("Bitcrush")
        if use_bitcrush:
            bit_depth = st.slider("Bit Depth", 2, 16, 8)
            crush_mix = st.slider("Crush Mix", 0.0, 1.0, 0.3)
    
    with eff_col3:
        use_reverb = st.checkbox("Reverb")
        if use_reverb:
            reverb_decay = st.slider("Reverb Decay", 0.1, 0.9, 0.4)
    
    params = {
        'base_freq': base_freq,
        'contour': contour,
        'contour_amount': contour_amount,
        'vibrato_rate': vibrato_rate,
        'vibrato_depth': vibrato_depth,
        'vowel': vowel,
        'formant_shift': formant_shift,
        'breathiness': breathiness,
        'brightness': brightness,
        'oscillator_mix': {'sine': osc_sine, 'saw': osc_saw, 'noise': osc_noise},
        'duration': duration,
        'attack': attack,
        'decay': decay,
        'sustain': sustain,
        'release': release,
        'tremolo_rate': tremolo_rate,
        'tremolo_depth': tremolo_depth,
    }
    
    effects_list = []
    if use_ring_mod:
        effects_list.append(('ring_mod', {'carrier_freq': ring_freq, 'mix': ring_mix}))
    if use_bitcrush:
        effects_list.append(('bitcrush', {'bit_depth': bit_depth, 'mix': crush_mix}))
    if use_reverb:
        effects_list.append(('reverb', {'decay': reverb_decay}))
    
    st.markdown("---")
    gen_col1, gen_col2 = st.columns([1, 2])
    
    with gen_col1:
        if st.button("Generate Custom Sound", type="primary", use_container_width=True):
            audio = generate_custom(params, effects_list)
            st.session_state.current_audio = audio
            st.session_state.current_audio_stereo = False
    
    with gen_col2:
        if st.session_state.current_audio is not None and not st.session_state.current_audio_stereo:
            audio_bytes = audio_to_bytes(st.session_state.current_audio, sr)
            st.audio(audio_bytes, format='audio/wav')
            
            st.download_button(
                "Download WAV",
                audio_bytes,
                file_name="bling_custom.wav",
                mime="audio/wav"
            )


# ============================================================
# SEQUENCE GENERATOR TAB
# ============================================================
elif mode == "Sequence Generator":
    st.header("Sequence Generator")
    st.markdown("Generate sequences of blips for complex expressions.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        n_blips = st.slider("Number of Blips", 2, 8, 4)
        base_freq = st.slider("Base Frequency (Hz)", 200, 1000, 500)
        freq_variation = st.slider("Frequency Variation", 0.0, 0.5, 0.2)
        
        st.markdown("---")
        st.subheader("Duration Range")
        min_duration = st.slider("Min Duration (s)", 0.05, 0.3, 0.1)
        max_duration = st.slider("Max Duration (s)", 0.2, 0.8, 0.4)
        
        st.markdown("---")
        st.subheader("Gap Range")
        min_gap = st.slider("Min Gap (s)", 0.02, 0.1, 0.05)
        max_gap = st.slider("Max Gap (s)", 0.05, 0.3, 0.15)
        
        st.markdown("---")
        contour_choices = st.multiselect(
            "Contour Options",
            CONTOUR_OPTIONS,
            default=['question', 'flat', 'rising']
        )
        
        vowel_choices = st.multiselect(
            "Vowel Options",
            VOWEL_OPTIONS,
            default=['o', 'u', 'i']
        )
        
        if st.button("Generate Sequence", type="primary", use_container_width=True):
            if not contour_choices:
                contour_choices = ['flat']
            if not vowel_choices:
                vowel_choices = ['o']
            
            audio = generate_blip_sequence(
                n_blips=n_blips,
                base_freq=base_freq,
                freq_variation=freq_variation,
                duration_range=(min_duration, max_duration),
                gap_range=(min_gap, max_gap),
                contour_options=contour_choices,
                vowel_options=vowel_choices,
            )
            st.session_state.current_audio = audio
            st.session_state.current_audio_stereo = False
        
        if st.button("Regenerate (New Random)", use_container_width=True):
            np.random.seed(None)
            if not contour_choices:
                contour_choices = ['flat']
            if not vowel_choices:
                vowel_choices = ['o']
            
            audio = generate_blip_sequence(
                n_blips=n_blips,
                base_freq=base_freq,
                freq_variation=freq_variation,
                duration_range=(min_duration, max_duration),
                gap_range=(min_gap, max_gap),
                contour_options=contour_choices,
                vowel_options=vowel_choices,
            )
            st.session_state.current_audio = audio
            st.session_state.current_audio_stereo = False
    
    with col2:
        if st.session_state.current_audio is not None and not st.session_state.current_audio_stereo:
            st.subheader("Output")
            audio_bytes = audio_to_bytes(st.session_state.current_audio, sr)
            st.audio(audio_bytes, format='audio/wav')
            
            st.download_button(
                "Download WAV",
                audio_bytes,
                file_name="bling_sequence.wav",
                mime="audio/wav"
            )
            
            st.subheader("Waveform")
            import plotly.graph_objects as go
            
            audio = st.session_state.current_audio
            time_axis = np.arange(len(audio)) / sr
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=time_axis,
                y=audio,
                mode='lines',
                line=dict(color='#ff8800', width=1)
            ))
            fig.update_layout(
                xaxis_title="Time (s)",
                yaxis_title="Amplitude",
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0.1)',
            )
            st.plotly_chart(fig, use_container_width=True)


# ============================================================
# ALIEN CHATTER TAB
# ============================================================
elif mode == "Alien Chatter":
    st.header("Alien Chatter")
    st.markdown("Generate conversations between alien characters.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Characters")
        
        available_chars = list(CHARACTER_PROFILES.keys())
        selected_chars = st.multiselect(
            "Select characters (2-5)",
            available_chars,
            default=['smol', 'mimo', 'null'],
            format_func=lambda x: f"{CHARACTER_PROFILES[x]['name']}"
        )
        
        # Show character info
        if selected_chars:
            st.markdown("**Selected:**")
            for char in selected_chars:
                profile = CHARACTER_PROFILES[char]
                st.caption(f"• {profile['name']}: {profile['description']}")
        
        st.markdown("---")
        st.subheader("Conversation")
        
        template = st.selectbox(
            "Scenario",
            list(CONVERSATION_TEMPLATES.keys()),
            format_func=lambda x: CONVERSATION_TEMPLATES[x]['name']
        )
        st.caption(CONVERSATION_TEMPLATES[template]['description'])
        
        n_turns = st.slider("Number of turns", 3, 12, 6)
        
        st.markdown("---")
        st.subheader("Timing")
        
        base_duration = st.slider("Base utterance duration", 0.2, 0.6, 0.35, 0.05)
        gap_min = st.slider("Min gap between turns", 0.05, 0.3, 0.12, 0.02)
        gap_max = st.slider("Max gap between turns", 0.15, 0.6, 0.35, 0.05)
        
        st.markdown("---")
        
        generate_disabled = len(selected_chars) < 2
        
        if st.button(
            "Generate Conversation",
            type="primary",
            use_container_width=True,
            disabled=generate_disabled
        ):
            if len(selected_chars) >= 2:
                stereo_audio, metadata = generate_conversation(
                    characters=selected_chars,
                    template_key=template,
                    n_turns=n_turns,
                    base_duration=base_duration,
                    gap_range=(gap_min, gap_max),
                    sr=sr
                )
                st.session_state.current_audio = stereo_audio
                st.session_state.current_audio_stereo = True
                st.session_state.conversation_metadata = metadata
        
        if generate_disabled:
            st.warning("Select at least 2 characters")
        
        if st.button("Regenerate", use_container_width=True, disabled=generate_disabled):
            np.random.seed(None)
            if len(selected_chars) >= 2:
                stereo_audio, metadata = generate_conversation(
                    characters=selected_chars,
                    template_key=template,
                    n_turns=n_turns,
                    base_duration=base_duration,
                    gap_range=(gap_min, gap_max),
                    sr=sr
                )
                st.session_state.current_audio = stereo_audio
                st.session_state.current_audio_stereo = True
                st.session_state.conversation_metadata = metadata
    
    with col2:
        if st.session_state.current_audio is not None and st.session_state.current_audio_stereo:
            st.subheader("Output")
            
            audio_bytes = audio_to_bytes(st.session_state.current_audio, sr)
            st.audio(audio_bytes, format='audio/wav')
            
            st.download_button(
                "Download WAV",
                audio_bytes,
                file_name="alien_chatter.wav",
                mime="audio/wav"
            )
            
            # Show conversation transcript
            if st.session_state.conversation_metadata:
                st.subheader("Transcript")
                
                for i, turn in enumerate(st.session_state.conversation_metadata):
                    char_name = CHARACTER_PROFILES[turn['character']]['name']
                    emotion = turn['emotion']
                    st.markdown(f"**{char_name}**: *[{emotion}]*")
            
            # Stereo waveform
            st.subheader("Waveform (Stereo)")
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            audio = st.session_state.current_audio
            time_axis = np.arange(len(audio)) / sr
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                               subplot_titles=("Left", "Right"),
                               vertical_spacing=0.1)
            
            fig.add_trace(
                go.Scatter(x=time_axis, y=audio[:, 0], mode='lines',
                          line=dict(color='#00ff88', width=1), name='Left'),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=time_axis, y=audio[:, 1], mode='lines',
                          line=dict(color='#ff8800', width=1), name='Right'),
                row=2, col=1
            )
            
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0.1)',
                showlegend=False
            )
            fig.update_xaxes(title_text="Time (s)", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Quick exchange section
        st.markdown("---")
        st.subheader("Quick Exchange")
        st.markdown("Generate a quick back-and-forth between two characters.")
        
        qe_col1, qe_col2 = st.columns(2)
        
        with qe_col1:
            char1 = st.selectbox("Character 1", available_chars, index=0,
                                format_func=lambda x: CHARACTER_PROFILES[x]['name'],
                                key='qe_char1')
            emotion1 = st.selectbox("Emotion 1", list(EMOTION_PRESETS.keys()),
                                   index=0, key='qe_emo1')
        
        with qe_col2:
            char2 = st.selectbox("Character 2", available_chars, index=1,
                                format_func=lambda x: CHARACTER_PROFILES[x]['name'],
                                key='qe_char2')
            emotion2 = st.selectbox("Emotion 2", list(EMOTION_PRESETS.keys()),
                                   index=5, key='qe_emo2')
        
        if st.button("Generate Quick Exchange", use_container_width=True):
            stereo = generate_quick_exchange(char1, char2, emotion1, emotion2, sr=sr)
            st.session_state.current_audio = stereo
            st.session_state.current_audio_stereo = True
            st.session_state.conversation_metadata = [
                {'character': char1, 'emotion': emotion1, 'duration': 0, 'gap_after': 0},
                {'character': char2, 'emotion': emotion2, 'duration': 0, 'gap_after': 0},
            ]
            st.rerun()


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
    BlingSpeak — Formant synthesis, pitch contours, and procedural conversations. No samples, just math.
    </div>
    """,
    unsafe_allow_html=True
)