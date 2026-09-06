import logging
from typing import Dict
from ..ports.telephony import TelephonyProvider

logger = logging.getLogger(__name__)


class MockTelephonyProvider(TelephonyProvider):
    """Local testing mock telephony provider simulating Exotel call events."""

    def __init__(self):
        self.active_sessions: Dict[str, dict] = {}

    async def start_call(self, call_id: str, caller_info: dict) -> None:
        self.active_sessions[call_id] = {
            "info": caller_info,
            "status": "connected",
            "audio_packets_sent": 0
        }
        logger.info(f"[MockTelephony] Call started: {call_id} | Caller: {caller_info.get('caller_number', 'unknown')}")

    async def send_audio(self, call_id: str, audio_bytes: bytes) -> None:
        if call_id in self.active_sessions:
            self.active_sessions[call_id]["audio_packets_sent"] += 1
            logger.debug(f"[MockTelephony] Sent {len(audio_bytes)} audio bytes to {call_id}")

    async def clear_buffer(self, call_id: str, reason: str = "barge_in") -> None:
        logger.info(f"[MockTelephony] Buffer cleared for {call_id} (Reason: {reason})")

    async def end_call(self, call_id: str, reason: str = "normal") -> None:
        if call_id in self.active_sessions:
            del self.active_sessions[call_id]
        logger.info(f"[MockTelephony] Call ended: {call_id} (Reason: {reason})")
