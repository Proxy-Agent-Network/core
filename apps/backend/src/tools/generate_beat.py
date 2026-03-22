import wave
import math
import struct
import random
import os

# CONFIGURATION
FILENAME = "static/audio/disco.wav"
SAMPLE_RATE = 44100
BPM = 104
BEAT_DURATION = 60 / BPM  # ~0.577 seconds
BAR_DURATION = BEAT_DURATION * 4
LOOP_DURATION = BAR_DURATION * 2  # 2 Bar Loop
TOTAL_SAMPLES = int(SAMPLE_RATE * LOOP_DURATION)

# ENSURE DIRECTORY EXISTS
os.makedirs(os.path.dirname(FILENAME), exist_ok=True)

def generate_sine(freq, duration, volume=1.0):
    """Generate a pure sine wave."""
    samples = []
    num_samples = int(SAMPLE_RATE * duration)
    for i in range(num_samples):
        value = math.sin(2 * math.pi * freq * (i / SAMPLE_RATE))
        samples.append(value * volume)
    return samples

def generate_kick(duration=0.4):
    """Synthesize a punchy 808-style kick (Sine Sweep)."""
    samples = []
    num_samples = int(SAMPLE_RATE * duration)
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Frequency Sweep: Starts at 150Hz, drops to 50Hz quickly
        freq = 150 * math.exp(-15 * t) + 50
        # Amplitude Envelope: Fast attack, decay
        amp = math.exp(-5 * t)
        value = math.sin(2 * math.pi * freq * t) * amp
        samples.append(value)
    return samples

def generate_snare(duration=0.2):
    """Synthesize a retro noise snare."""
    samples = []
    num_samples = int(SAMPLE_RATE * duration)
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # White Noise + Low Sine for body
        noise = (random.random() * 2 - 1) * math.exp(-15 * t)
        tone = math.sin(2 * math.pi * 200 * t) * math.exp(-10 * t) * 0.5
        samples.append((noise + tone) * 0.8)
    return samples

def generate_hihat(duration=0.1):
    """Synthesize a high-frequency noise hat."""
    samples = []
    num_samples = int(SAMPLE_RATE * duration)
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # High frequency noise
        noise = (random.random() * 2 - 1)
        # Bandpass filter simulation (crude)
        if i > 0: noise = noise - 0.5 * samples[i-1] 
        amp = math.exp(-40 * t)
        samples.append(noise * amp * 0.3)
    return samples

def generate_bass(freq, duration):
    """Synthesize a funky FM-style bass."""
    samples = []
    num_samples = int(SAMPLE_RATE * duration)
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # FM Synthesis: Carrier + Modulator
        mod = math.sin(2 * math.pi * freq * 2 * t) * 5  # Modulator
        val = math.sin(2 * math.pi * freq * t + mod)     # Carrier
        amp = 1.0
        if t < 0.05: amp = t / 0.05
        else: amp = math.exp(-2 * (t - 0.05))
        samples.append(val * amp * 0.6)
    return samples

def generate_strings(chord_freqs, duration):
    """Synthesize a string pad (Chorus effect)."""
    samples = []
    num_samples = int(SAMPLE_RATE * duration)
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val = 0
        for f in chord_freqs:
            # Add slight detuning for "Chorus" effect
            v1 = math.sin(2 * math.pi * f * t)
            v2 = math.sin(2 * math.pi * (f * 1.002) * t + 1)
            val += (v1 + v2) * 0.1
        # Slow attack
        amp = 1.0
        if t < 0.2: amp = t / 0.2
        samples.append(val * amp * 0.4)
    return samples

# --- SEQUENCER ---
print(f"🎵 Synthesizing {LOOP_DURATION:.2f}s Disco Loop at {BPM} BPM...")
final_mix = [0.0] * TOTAL_SAMPLES

# 1. DRUMS (Standard 4-on-the-floor)
for beat in range(8): # 2 bars * 4 beats
    pos = int(beat * BEAT_DURATION * SAMPLE_RATE)
    
    # KICK (Every beat)
    kick = generate_kick()
    for i, s in enumerate(kick):
        if pos+i < TOTAL_SAMPLES: final_mix[pos+i] += s * 0.8

    # SNARE (Beats 2 and 4)
    if beat % 4 in [1, 3]: # 0-indexed: 1 is beat 2
        snare = generate_snare()
        for i, s in enumerate(snare):
            if pos+i < TOTAL_SAMPLES: final_mix[pos+i] += s * 0.7

    # HI-HAT (Every 8th note)
    for sub in [0, 0.5]:
        hat_pos = int((beat + sub) * BEAT_DURATION * SAMPLE_RATE)
        hat = generate_hihat()
        for i, s in enumerate(hat):
             if hat_pos+i < TOTAL_SAMPLES: final_mix[hat_pos+i] += s * 0.5

# 2. BASS (F Minor Groovy Syncopation)
# F2 = 87.31 Hz, Eb2 = 77.78 Hz, Ab2 = 103.83 Hz
bass_seq = [
    (0, 87.31, 0.5),   # Beat 1: F
    (0.75, 77.78, 0.25), # Beat 1.75: Eb
    (1.5, 87.31, 0.5), # Beat 2.5: F
    (2.5, 103.83, 0.5), # Beat 3.5: Ab
    (3.5, 87.31, 0.5), # Beat 4.5: F
    # Bar 2
    (4, 87.31, 0.5),
    (4.75, 77.78, 0.25),
    (5.5, 87.31, 0.5),
    (6.5, 116.54, 0.5), # Bb2
    (7.5, 87.31, 0.5)
]

for b, freq, dur in bass_seq:
    pos = int(b * BEAT_DURATION * SAMPLE_RATE)
    sound = generate_bass(freq, dur * BEAT_DURATION)
    for i, s in enumerate(sound):
        if pos+i < TOTAL_SAMPLES: final_mix[pos+i] += s * 0.6

# 3. STRINGS (High Pad F Minor 7)
# F4, Ab4, C5, Eb5
chord = [349.23, 415.30, 523.25, 622.25]
strings = generate_strings(chord, LOOP_DURATION)
for i, s in enumerate(strings):
    if i < TOTAL_SAMPLES: final_mix[i] += s * 0.3

# --- WRITE WAVE FILE ---
with wave.open(FILENAME, 'w') as wav_file:
    wav_file.setnchannels(1) # Mono
    wav_file.setsampwidth(2) # 16-bit
    wav_file.setframerate(SAMPLE_RATE)
    
    # Normalize and Convert to 16-bit PCM
    max_val = max(abs(x) for x in final_mix)
    print(f"🎚️ Normalizing (Peak: {max_val:.2f})...")
    
    packed_data = bytearray()
    for sample in final_mix:
        # Clip and Scale
        s = max(min(sample / max_val, 1.0), -1.0)
        packed_data.extend(struct.pack('<h', int(s * 32767)))
        
    wav_file.writeframes(packed_data)

print(f"✅ DONE! Saved to {FILENAME}")