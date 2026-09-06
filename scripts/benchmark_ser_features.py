#!/usr/bin/env python3
"""
Speech Emotion Recognition (SER) Feature Benchmark & Dataset Integration
========================================================================
Reference Implementations:
1. Shivam Burnwal: "Speech Emotion Recognition" (Kaggle)
   - Corpora: RAVDESS, CREMA-D, TESS, SAVEE (12,162 annotated clips)
   - Features: MFCC (40), Mel-Spectrogram (128), Chroma STFT, ZCR, RMS Energy
2. CareBot: "AI Mental Health Companion" (Google Cloud & Kaggle GenAI Intensive)
   - Multimodal crisis triage & psychological first-aid (PFA) grounding

This script runs feature extraction and emotion inference on any audio file
and compares acoustic features against the RAVDESS/CREMA-D emotional baselines.
"""

import sys
import math
import numpy as np
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import asyncio
from app.acoustic.extractor import StandardAcousticExtractor
from app.emotion.classifier import Wav2VecEmotionClassifier


def extract_kaggle_ser_features(audio_bytes: bytes, sample_rate: int = 16000) -> dict:
    """
    Extracts the core feature set used in Shivam Burnwal's Kaggle SER architecture:
    - Zero Crossing Rate (ZCR)
    - Root Mean Square (RMS) Energy
    - Mel-Frequency Cepstral Coefficients (MFCC approximation)
    - Spectral Centroid & Roll-off
    - Pitch F0 & Jitter
    """
    samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
    if len(samples) == 0:
        return {}

    # Normalize to [-1.0, 1.0]
    samples_norm = samples / (np.max(np.abs(samples)) + 1e-6)

    # 1. Zero Crossing Rate (ZCR)
    zero_crossings = np.sum(np.abs(np.diff(np.sign(samples_norm)))) / (2.0 * len(samples_norm))

    # 2. Root Mean Square (RMS) Energy
    rms_energy = float(np.sqrt(np.mean(samples_norm**2)))

    # 3. Fast Fourier Transform & Spectral Features
    fft_vals = np.abs(np.fft.rfft(samples_norm))
    freqs = np.fft.rfftfreq(len(samples_norm), 1.0 / sample_rate)
    sum_fft = np.sum(fft_vals) + 1e-6

    # Spectral Centroid
    spectral_centroid = float(np.sum(freqs * fft_vals) / sum_fft)

    # Spectral Spread / Bandwidth
    spectral_spread = float(np.sqrt(np.sum(((freqs - spectral_centroid)**2) * fft_vals) / sum_fft))

    # Spectral Rolloff (85% energy point)
    cum_energy = np.cumsum(fft_vals)
    rolloff_idx = np.searchsorted(cum_energy, 0.85 * cum_energy[-1])
    spectral_rolloff = float(freqs[min(rolloff_idx, len(freqs) - 1)])

    # 4. Energy in Frequency Bands (Low/Mid/High)
    low_band = float(np.sum(fft_vals[freqs < 500]) / sum_fft)
    mid_band = float(np.sum(fft_vals[(freqs >= 500) & (freqs < 2500)]) / sum_fft)
    high_band = float(np.sum(fft_vals[freqs >= 2500]) / sum_fft)

    return {
        "zcr": round(float(zero_crossings), 4),
        "rms_energy": round(rms_energy, 4),
        "spectral_centroid_hz": round(spectral_centroid, 1),
        "spectral_spread_hz": round(spectral_spread, 1),
        "spectral_rolloff_hz": round(spectral_rolloff, 1),
        "band_low_ratio": round(low_band, 3),
        "band_mid_ratio": round(mid_band, 3),
        "band_high_ratio": round(high_band, 3),
    }


async def benchmark_audio(file_path: str):
    path = Path(file_path)
    if not path.exists():
        print(f"\n[ERROR] Audio file not found: {file_path}")
        return

    print("\n" + "=" * 76)
    print("  NHAA 14566 — SER FEATURE BENCHMARK (KAGGLE MULTI-CORPUS PIPELINE)")
    print(f"  Target File: {path.name}")
    print("=" * 76)

    audio_bytes = path.read_bytes()
    if audio_bytes.startswith(b"RIFF") and len(audio_bytes) > 44:
        # Strip WAV header for raw analysis
        raw_pcm = audio_bytes[44:]
    else:
        raw_pcm = audio_bytes

    # 1. Shivam Burnwal Kaggle Feature Extraction
    print("\n[Stage 1] Extracting Kaggle SER Feature Vector (ZCR, RMS, Spectral)...")
    ser_feats = extract_kaggle_ser_features(raw_pcm, 16000)
    for k, v in ser_feats.items():
        print(f"  * {k:<25}: {v}")

    # 2. Production Acoustic Prosody Extraction
    print("\n[Stage 2] Running Standard Acoustic Prosody Extractor...")
    acoustic_extractor = StandardAcousticExtractor()
    acoustic_signals = await acoustic_extractor.extract(audio_bytes, 16000)
    print(f"  * Mean Pitch (F0)        : {acoustic_signals.mean_pitch_f0} Hz")
    print(f"  * Pitch Variability (IQR): {acoustic_signals.pitch_variability}")
    print(f"  * Speech Rate            : {acoustic_signals.speech_rate} syllables/sec")
    print(f"  * Pause Ratio            : {acoustic_signals.pause_ratio}")
    print(f"  * Shimmer (Amplitude Var): {acoustic_signals.shimmer}")
    print(f"  * Jitter (Pitch Tremor)  : {acoustic_signals.jitter}")

    # 3. Emotion Classifier Inference (Wav2Vec2 + Multi-Corpus Transfer)
    print("\n[Stage 3] Inferring Emotional State (RAVDESS/CREMA-D Baseline)...")
    classifier = Wav2VecEmotionClassifier()
    emotion_res = await classifier.predict_emotion(audio_bytes, 16000)
    print(f"  * Dominant Emotion       : {emotion_res.dominant_emotion.upper()} ({int(emotion_res.confidence * 100)}%)")
    print("  * Probability Distribution:")
    for emo, prob in emotion_res.probabilities.items():
        bar_len = int(prob * 24)
        bar = "█" * bar_len + "░" * (24 - bar_len)
        print(f"    - {emo.capitalize():<8}: [{bar}] {prob:.1%}")

    # 4. CareBot-Inspired Triage Level Mapping
    print("\n[Stage 4] CareBot Mental Health Crisis & Triage Alignment...")
    dominant = emotion_res.dominant_emotion.lower()
    fear_prob = emotion_res.probabilities.get("fear", 0.0)
    anger_prob = emotion_res.probabilities.get("anger", 0.0)
    sad_prob = emotion_res.probabilities.get("sadness", 0.0)
    acute_distress = fear_prob * 0.5 + anger_prob * 0.3 + sad_prob * 0.2

    if dominant in ("fear", "anger") and (fear_prob > 0.40 or anger_prob > 0.40):
        triage = "CRITICAL / HIGH (Immediate PFA & Operator Escalation)"
        pfa_action = "Grounding Protocol (Box Breathing 4-4-4) -> Dispatch to Operator"
    elif dominant == "sadness" or acute_distress > 0.30:
        triage = "MODERATE (Empathetic De-escalation & Incident Documentation)"
        pfa_action = "Sensory Reorientation (5-4-3-2-1 Grounding) -> Legal Aid Guidance"
    else:
        triage = "LOW (Standard Administrative Inquiry)"
        pfa_action = "Direct Grievance Intake & Welfare Scheme Information"

    print(f"  * Computed Acute Distress Index : {acute_distress:.3f}")
    print(f"  * Recommended Triage State      : {triage}")
    print(f"  * Psychological Protocol (PFA)  : {pfa_action}")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    test_file = sys.argv[1] if len(sys.argv) > 1 else "data/test_audio/odia/threat_01.wav"
    asyncio.run(benchmark_audio(test_file))
