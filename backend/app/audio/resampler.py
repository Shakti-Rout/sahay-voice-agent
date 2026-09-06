import numpy as np
from scipy import signal

# Precomputed G.711 mu-law expansion table (256 entries for int16)
# Standard ITU-T G.711 implementation (Python 3.13 compatible, zero dependencies)
def _create_ulaw_to_linear_table() -> np.ndarray:
    table = np.zeros(256, dtype=np.int16)
    for i in range(256):
        val = ~i & 0xFF
        sign = val & 0x80
        exponent = (val >> 4) & 0x07
        mantissa = val & 0x0F
        sample = ((mantissa << 3) + 0x84) << exponent
        sample -= 0x84
        table[i] = -sample if sign else sample
    return table

_ULAW_DECODE_TABLE = _create_ulaw_to_linear_table()


class AudioResampler:
    """
    Handles 8kHz <-> 16kHz conversion, G.711 u-law decoding/encoding, and normalization.
    Fully compatible with Python 3.10 through Python 3.13+.
    """

    @staticmethod
    def ulaw_to_linear_pcm(ulaw_bytes: bytes) -> bytes:
        """Decode 8-bit G.711 u-law bytes to 16-bit linear PCM."""
        if not ulaw_bytes:
            return b""
        raw_u8 = np.frombuffer(ulaw_bytes, dtype=np.uint8)
        decoded = _ULAW_DECODE_TABLE[raw_u8]
        return decoded.tobytes()

    @staticmethod
    def linear_pcm_to_ulaw(pcm_bytes: bytes) -> bytes:
        """Encode 16-bit linear PCM bytes to 8-bit G.711 u-law."""
        if not pcm_bytes:
            return b""
        samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.int32)
        # Vectorized G.711 mu-law compression
        sign = (samples < 0)
        samples = np.abs(samples)
        samples = np.clip(samples + 132, 0, 32767)

        # Exponent determination
        exponent = np.zeros_like(samples, dtype=np.uint8)
        for exp in range(7, 0, -1):
            mask = (samples >= (132 << exp))
            exponent[mask & (exponent == 0)] = exp

        mantissa = (samples >> (exponent + 3)) & 0x0F
        ulaw = ~( (exponent << 4) | mantissa | (sign.astype(np.uint8) << 7) ) & 0xFF
        return ulaw.astype(np.uint8).tobytes()

    @staticmethod
    def resample_8k_to_16k(pcm_8k: bytes) -> bytes:
        """
        Resample 16-bit mono PCM from 8,000 Hz to 16,000 Hz
        using band-limited polyphase filter (up=2, down=1).
        """
        if not pcm_8k:
            return b""

        audio_data = np.frombuffer(pcm_8k, dtype=np.int16)
        if len(audio_data) == 0:
            return b""

        resampled_data = signal.resample_poly(audio_data, up=2, down=1)
        resampled_int16 = np.clip(resampled_data, -32768, 32767).astype(np.int16)

        return resampled_int16.tobytes()

    @staticmethod
    def resample_16k_to_8k(pcm_16k: bytes) -> bytes:
        """
        Resample 16-bit mono PCM from 16,000 Hz to 8,000 Hz
        using band-limited polyphase filter (up=1, down=2).
        """
        if not pcm_16k:
            return b""

        audio_data = np.frombuffer(pcm_16k, dtype=np.int16)
        if len(audio_data) == 0:
            return b""

        resampled_data = signal.resample_poly(audio_data, up=1, down=2)
        resampled_int16 = np.clip(resampled_data, -32768, 32767).astype(np.int16)

        return resampled_int16.tobytes()

    @staticmethod
    def normalize_volume(pcm_bytes: bytes, target_rms: float = 3000.0) -> bytes:
        """Normalize PCM audio energy to a stable RMS level."""
        if not pcm_bytes:
            return b""

        audio_data = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
        rms = np.sqrt(np.mean(audio_data**2))
        if rms < 50.0:
            return pcm_bytes

        gain = target_rms / (rms + 1e-6)
        gain = min(gain, 4.0)
        normalized = np.clip(audio_data * gain, -32768, 32767).astype(np.int16)

        return normalized.tobytes()
