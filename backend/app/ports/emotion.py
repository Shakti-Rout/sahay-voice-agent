from abc import ABC, abstractmethod
from ..domain.models import EmotionSignals


class EmotionClassifier(ABC):
    """Abstract interface for Speech Emotion Recognition models (Wav2Vec2, SpeechBrain)."""

    @abstractmethod
    async def predict_emotion(self, audio_bytes: bytes, sample_rate: int = 16000) -> EmotionSignals:
        """Predict calibrated softmax probabilities across basic emotional states."""
        pass
