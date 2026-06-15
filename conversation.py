"""Conversation generation for AlienChatter."""

import numpy as np
from synth.generator import generate_bling_sound, generate_blip_sequence
from effects.effects import apply_effects_chain
from presets import EMOTION_PRESETS
from utils import normalize


# Character voice profiles (modify base synthesis parameters)
CHARACTER_PROFILES = {
    'null': {
        'name': 'Null',
        'description': 'Deep, authoritative, slightly unsettling',
        'base_freq_mult': 0.7,
        'formant_shift': 0.85,
        'breathiness': 0.05,
        'brightness': 0.5,
        'default_emotion': 'thinking',
        'pan': -0.3,  # Slightly left
    },
    'smol': {
        'name': 'Smol',
        'description': 'Tiny, nervous, curious',
        'base_freq_mult': 1.4,
        'formant_shift': 1.4,
        'breathiness': 0.15,
        'brightness': 0.7,
        'default_emotion': 'curious',
        'pan': 0.5,  # Right
    },
    'mimo': {
        'name': 'Mimo',
        'description': 'Quick, observational, slightly mischievous',
        'base_freq_mult': 1.15,
        'formant_shift': 1.2,
        'breathiness': 0.1,
        'brightness': 0.65,
        'default_emotion': 'happy',
        'pan': 0.3,  # Slightly right
    },
    'yun': {
        'name': 'Yun',
        'description': 'Soft, warm, encouraging',
        'base_freq_mult': 1.1,
        'formant_shift': 1.1,
        'breathiness': 0.12,
        'brightness': 0.6,
        'default_emotion': 'agreeing',
        'pan': -0.5,  # Left
    },
    'bling': {
        'name': 'Bling',
        'description': 'Abstract, tonal, expressive non-words',
        'base_freq_mult': 1.3,
        'formant_shift': 1.5,
        'breathiness': 0.08,
        'brightness': 0.9,
        'default_emotion': 'delighted',
        'pan': 0.0,  # Center
    },
}


# Conversation templates with emotional arcs
CONVERSATION_TEMPLATES = {
    'casual_chat': {
        'name': 'Casual Chat',
        'description': 'Friendly back-and-forth',
        'turns': [
            {'emotion_curve': 'neutral_to_happy'},
            {'min_turns': 4, 'max_turns': 8},
        ],
        'emotion_sequence': ['curious', 'agreeing', 'happy', 'curious', 'agreeing'],
        'energy': 'medium',
        'interruption_chance': 0.1,
    },
    'excited_discovery': {
        'name': 'Excited Discovery',
        'description': 'Someone found something interesting',
        'emotion_sequence': ['curious', 'excited', 'excited', 'delighted', 'agreeing'],
        'energy': 'high',
        'interruption_chance': 0.3,
    },
    'confusion': {
        'name': 'Confusion',
        'description': 'Nobody understands what is happening',
        'emotion_sequence': ['confused', 'curious', 'confused', 'thinking', 'confused'],
        'energy': 'medium',
        'interruption_chance': 0.2,
    },
    'startled_reaction': {
        'name': 'Startled Reaction',
        'description': 'Something unexpected happened',
        'emotion_sequence': ['startled', 'nervous', 'curious', 'confused', 'agreeing'],
        'energy': 'high',
        'interruption_chance': 0.4,
    },
    'explanation': {
        'name': 'Explanation',
        'description': 'One character explains something to others',
        'emotion_sequence': ['thinking', 'curious', 'agreeing', 'confused', 'agreeing', 'happy'],
        'energy': 'low',
        'interruption_chance': 0.05,
    },
    'argument': {
        'name': 'Disagreement',
        'description': 'Characters have different opinions',
        'emotion_sequence': ['confused', 'nervous', 'startled', 'thinking', 'agreeing'],
        'energy': 'high',
        'interruption_chance': 0.5,
    },
}


def apply_stereo_pan(mono_audio, pan):
    """
    Convert mono to stereo with panning.
    
    pan: -1 (full left) to +1 (full right), 0 = center
    """
    left_gain = np.sqrt(0.5 * (1 - pan))
    right_gain = np.sqrt(0.5 * (1 + pan))
    
    stereo = np.zeros((len(mono_audio), 2))
    stereo[:, 0] = mono_audio * left_gain
    stereo[:, 1] = mono_audio * right_gain
    
    return stereo


def generate_character_utterance(
    character_key,
    emotion='curious',
    duration=0.4,
    n_blips=None,
    intensity=0.7,
    sr=44100
):
    """
    Generate a single utterance for a character.
    
    Returns: mono audio array
    """
    profile = CHARACTER_PROFILES.get(character_key, CHARACTER_PROFILES['bling'])
    preset = EMOTION_PRESETS.get(emotion, EMOTION_PRESETS['curious'])
    
    # Merge profile with emotion preset
    params = preset['params'].copy()
    
    # Apply character modifications
    if 'base_freq' in params:
        params['base_freq'] *= profile['base_freq_mult']
    else:
        params['base_freq'] = 500 * profile['base_freq_mult']
    
    params['formant_shift'] = params.get('formant_shift', 1.0) * profile['formant_shift']
    params['breathiness'] = profile['breathiness']
    params['brightness'] = profile['brightness']
    
    # Scale by intensity
    if 'contour_amount' in params:
        params['contour_amount'] *= intensity
    if 'tremolo_depth' in params:
        params['tremolo_depth'] *= intensity
    if 'vibrato_depth' in params:
        params['vibrato_depth'] *= intensity
    
    # Decide if single blip or sequence
    if n_blips is None:
        # Randomize based on character and emotion
        if emotion in ['excited', 'startled', 'nervous']:
            n_blips = np.random.randint(2, 5)
        elif emotion in ['thinking', 'sad']:
            n_blips = 1
        else:
            n_blips = np.random.randint(1, 4)
    
    if n_blips == 1:
        params['duration'] = duration
        params['sr'] = sr
        audio = generate_bling_sound(**params)
    else:
        # Generate sequence
        audio = generate_blip_sequence(
            n_blips=n_blips,
            base_freq=params['base_freq'],
            freq_variation=0.15,
            duration_range=(duration * 0.5, duration * 1.2),
            gap_range=(0.03, 0.1),
            formant_shift=params['formant_shift'],
            breathiness=params['breathiness'],
            brightness=params['brightness'],
            sr=sr
        )
    
    # Apply character-specific effects
    effects = preset.get('effects', [])
    if effects:
        audio = apply_effects_chain(audio, effects, sr=sr)
    
    return normalize(audio)


def generate_turn(
    character_key,
    emotion,
    base_duration=0.4,
    energy='medium',
    sr=44100
):
    """
    Generate a complete turn (one character speaking).
    
    Returns: dict with audio, character, duration info
    """
    profile = CHARACTER_PROFILES[character_key]
    
    # Adjust duration based on energy
    energy_mult = {'low': 1.3, 'medium': 1.0, 'high': 0.7}
    duration = base_duration * energy_mult.get(energy, 1.0)
    
    # Randomize number of blips based on energy
    if energy == 'high':
        n_blips = np.random.randint(2, 6)
    elif energy == 'low':
        n_blips = np.random.randint(1, 3)
    else:
        n_blips = np.random.randint(1, 4)
    
    audio = generate_character_utterance(
        character_key,
        emotion=emotion,
        duration=duration,
        n_blips=n_blips,
        sr=sr
    )
    
    return {
        'audio': audio,
        'character': character_key,
        'emotion': emotion,
        'pan': profile['pan'],
        'duration': len(audio) / sr
    }


def generate_conversation(
    characters,
    template_key='casual_chat',
    n_turns=6,
    base_duration=0.35,
    gap_range=(0.15, 0.4),
    sr=44100
):
    """
    Generate a full conversation between characters.
    
    characters: list of character keys, e.g., ['smol', 'mimo', 'null']
    template_key: conversation template to use
    n_turns: number of speaking turns
    
    Returns: stereo audio array, list of turn metadata
    """
    template = CONVERSATION_TEMPLATES.get(template_key, CONVERSATION_TEMPLATES['casual_chat'])
    emotion_sequence = template['emotion_sequence']
    energy = template['energy']
    interruption_chance = template['interruption_chance']
    
    turns = []
    turn_metadata = []
    
    # Track who spoke last to avoid same speaker twice
    last_speaker = None
    
    for i in range(n_turns):
        # Pick speaker (not the same as last)
        available = [c for c in characters if c != last_speaker]
        if not available:
            available = characters
        speaker = np.random.choice(available)
        last_speaker = speaker
        
        # Pick emotion from sequence (cycle if needed)
        emotion = emotion_sequence[i % len(emotion_sequence)]
        
        # Add some randomness to emotion
        if np.random.random() < 0.2:
            emotion = np.random.choice(emotion_sequence)
        
        # Generate turn
        turn = generate_turn(
            speaker,
            emotion,
            base_duration=base_duration,
            energy=energy,
            sr=sr
        )
        
        turns.append(turn)
        
        # Determine gap before next turn
        if i < n_turns - 1:
            # Check for interruption (negative gap = overlap)
            if np.random.random() < interruption_chance:
                gap = np.random.uniform(-0.1, 0.05)
            else:
                gap = np.random.uniform(*gap_range)
            
            turn['gap_after'] = gap
        else:
            turn['gap_after'] = 0
        
        turn_metadata.append({
            'character': speaker,
            'emotion': emotion,
            'duration': turn['duration'],
            'gap_after': turn['gap_after']
        })
    
    # Assemble stereo audio
    total_duration = sum(t['duration'] + max(0, t['gap_after']) for t in turns)
    total_samples = int(total_duration * sr) + sr  # Extra buffer
    
    stereo_output = np.zeros((total_samples, 2))
    current_pos = 0
    
    for turn in turns:
        audio = turn['audio']
        pan = turn['pan']
        
        # Convert to stereo with pan
        stereo_turn = apply_stereo_pan(audio, pan)
        
        # Handle negative position (from interruption)
        if current_pos < 0:
            # Trim the beginning if overlapping
            trim = int(-current_pos)
            if trim < len(stereo_turn):
                stereo_turn = stereo_turn[trim:]
                current_pos = 0
        
        # Place in output
        end_pos = current_pos + len(stereo_turn)
        if end_pos <= len(stereo_output):
            stereo_output[current_pos:end_pos] += stereo_turn
        
        # Move position
        current_pos = end_pos + int(turn['gap_after'] * sr)
    
    # Trim silence at end
    stereo_output = stereo_output[:int((total_duration + 0.1) * sr)]
    
    # Normalize
    peak = np.max(np.abs(stereo_output))
    if peak > 0:
        stereo_output = stereo_output * (0.95 / peak)
    
    return stereo_output, turn_metadata


def generate_quick_exchange(
    char1,
    char2,
    emotion1='curious',
    emotion2='agreeing',
    sr=44100
):
    """
    Generate a quick two-character exchange.
    
    Useful for simple back-and-forth.
    """
    turn1 = generate_turn(char1, emotion1, sr=sr)
    turn2 = generate_turn(char2, emotion2, sr=sr)
    
    gap = np.random.uniform(0.1, 0.25)
    gap_samples = int(gap * sr)
    
    # Assemble
    total_len = len(turn1['audio']) + gap_samples + len(turn2['audio'])
    stereo = np.zeros((total_len, 2))
    
    stereo[:len(turn1['audio'])] = apply_stereo_pan(turn1['audio'], turn1['pan'])
    
    start2 = len(turn1['audio']) + gap_samples
    stereo[start2:start2 + len(turn2['audio'])] = apply_stereo_pan(turn2['audio'], turn2['pan'])
    
    # Normalize
    peak = np.max(np.abs(stereo))
    if peak > 0:
        stereo = stereo * (0.95 / peak)
    
    return stereo