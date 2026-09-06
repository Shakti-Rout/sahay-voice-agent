import pytest
import numpy as np
from app.audio.resampler import AudioResampler


def test_resample_8k_to_16k():
    # 8000 samples at 8kHz = 1 second of audio
    sample_rate_8k = 8000
    t = np.linspace(0, 1.0, sample_rate_8k, endpoint=False)
    # 440 Hz pure tone
    samples = (np.sin(2 * np.pi * 440 * t) * 10000).astype(np.int16)
    raw_8k = samples.tobytes()

    raw_16k = AudioResampler.resample_8k_to_16k(raw_8k)
    resampled_samples = np.frombuffer(raw_16k, dtype=np.int16)

    # 1 second of audio at 16kHz should have 16000 samples
    assert len(resampled_samples) == 16000


def test_resample_16k_to_8k():
    sample_rate_16k = 16000
    t = np.linspace(0, 1.0, sample_rate_16k, endpoint=False)
    samples = (np.sin(2 * np.pi * 440 * t) * 10000).astype(np.int16)
    raw_16k = samples.tobytes()

    raw_8k = AudioResampler.resample_16k_to_8k(raw_16k)
    resampled_samples = np.frombuffer(raw_8k, dtype=np.int16)

    assert len(resampled_samples) == 8000
