from abc import ABC, abstractmethod
from typing import Callable, Awaitable, Any


class TelephonyProvider(ABC):
    """Abstract interface for telephony audio ingestion and playback."""

    @abstractmethod
    async def start_call(self, call_id: str, caller_info: dict) -> None:
        """Initialize a new telephony call session."""
        pass

    @abstractmethod
    async def send_audio(self, call_id: str, audio_bytes: bytes) -> None:
        """Send synthesized audio chunk back to the caller."""
        pass

    @abstractmethod
    async def clear_buffer(self, call_id: str, reason: str = "barge_in") -> None:
        """Clear caller audio buffer immediately upon barge-in."""
        pass

    @abstractmethod
    async def end_call(self, call_id: str, reason: str = "normal") -> None:
        """Terminate the telephony connection."""
        pass
