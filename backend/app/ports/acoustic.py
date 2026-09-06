from abc import ABC, abstractmethod
from ..domain.models import AcousticSignals


class AcousticFeatureExtractor(ABC):
    """Abstract interface for acoustic prosody and feature extraction (openSMILE, librosa)."""

    @abstractmethod
    async def extract(self, audio_bytes: bytes, sample_rate: int = 16000) -> AcousticSignals:
        """Extract pitch, jitter, shimmer, pause ratio, and speech rate from audio."""
        pass
