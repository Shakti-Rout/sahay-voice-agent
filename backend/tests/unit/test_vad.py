import numpy as np
import pytest
from app.audio.vad import VoiceActivityDetector


def test_vad_rejects_steady_fan_noise():
    """Verify HVAD rejects stationary non-living background noise (fans, cooling, AC)."""
    vad = VoiceActivityDetector(min_energy_threshold=500.0)
    # Simulate 2 seconds of stationary fan hum (low-frequency drone with tiny variance)
    sample_rate = 16000
    duration_s = 2.0
    t = np.linspace(0, duration_s, int(sample_rate * duration_s))
    
    # 60Hz hum + steady white hiss at RMS ~ 600
    fan_samples = (500.0 * np.sin(2 * np.pi * 60 * t) + np.random.normal(0, 150.0, len(t))).astype(np.int16)
    
    # Feed 128ms chunks
    chunk_size = 2048
    speech_detected_count = 0
    for i in range(0, len(fan_samples), chunk_size):
        chunk = fan_samples[i:i + chunk_size].tobytes()
        if len(chunk) == chunk_size * 2:
            is_speech = vad.process_frame(chunk)
            if is_speech:
                speech_detected_count += 1

    # Steady fan noise should NOT trigger continuous human speech
    assert speech_detected_count <= 1, "VAD must ignore steady stationary fan/appliance noise"


def test_vad_detects_modulated_human_speech():
    """Verify HVAD triggers for dynamic, modulated human speech-like energy."""
    vad = VoiceActivityDetector(min_energy_threshold=500.0)
    sample_rate = 16000
    duration_s = 2.0
    t = np.linspace(0, duration_s, int(sample_rate * duration_s))
    
    # Syllabic amplitude modulated speech wave (4Hz envelope, 250Hz voice pitch)
    envelope = np.maximum(0, np.sin(2 * np.pi * 4 * t))
    speech_samples = (4000.0 * envelope * np.sin(2 * np.pi * 250 * t)).astype(np.int16)
    
    chunk_size = 2048
    speech_detected_count = 0
    for i in range(0, len(speech_samples), chunk_size):
        chunk = speech_samples[i:i + chunk_size].tobytes()
        if len(chunk) == chunk_size * 2:
            is_speech = vad.process_frame(chunk)
            if is_speech:
                speech_detected_count += 1

    assert speech_detected_count > 0, "VAD must detect modulated human speech"


def test_vad_rejects_vehicle_horn_sound():
    """Verify HVAD rejects tonal vehicle horn / siren noise even at high amplitude."""
    vad = VoiceActivityDetector(min_energy_threshold=500.0)
    sample_rate = 16000
    duration_s = 2.0
    t = np.linspace(0, duration_s, int(sample_rate * duration_s))

    # High-intensity vehicle horn blast (2400Hz pure tone at high amplitude)
    horn_samples = (12000.0 * np.sin(2 * np.pi * 2400 * t)).astype(np.int16)

    chunk_size = 2048
    speech_detected_count = 0
    for i in range(0, len(horn_samples), chunk_size):
        chunk = horn_samples[i:i + chunk_size].tobytes()
        if len(chunk) == chunk_size * 2:
            is_speech = vad.process_frame(chunk)
            if is_speech:
                speech_detected_count += 1

    assert speech_detected_count == 0, "VAD must completely reject pure tonal vehicle horn blasts"


def test_vad_rejects_low_mid_car_horn():
    """Verify HVAD rejects low-mid dual-tone car horns (420Hz + 520Hz)."""
    vad = VoiceActivityDetector(min_energy_threshold=500.0)
    sample_rate = 16000
    duration_s = 2.0
    t = np.linspace(0, duration_s, int(sample_rate * duration_s))

    # Dual-tone car horn (420Hz + 520Hz)
    horn_samples = (6000.0 * np.sin(2 * np.pi * 420 * t) + 6000.0 * np.sin(2 * np.pi * 520 * t)).astype(np.int16)

    chunk_size = 2048
    speech_detected_count = 0
    for i in range(0, len(horn_samples), chunk_size):
        chunk = horn_samples[i:i + chunk_size].tobytes()
        if len(chunk) == chunk_size * 2:
            is_speech = vad.process_frame(chunk)
            if is_speech:
                speech_detected_count += 1

    assert speech_detected_count == 0, "VAD must completely reject dual-tone car horns"


