from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, Optional
from ..domain.models import LinguisticSignals


class LLMProvider(ABC):
    """Abstract interface for LLM conversational and reasoning engines (Gemini, OpenAI)."""

    @abstractmethod
    async def generate_response(
        self,
        conversation_history: List[Dict[str, str]],
        system_instructions: str,
        retrieved_context: Optional[str] = None
    ) -> str:
        """Generate a complete conversational response text."""
        pass

    @abstractmethod
    async def stream_response(
        self,
        conversation_history: List[Dict[str, str]],
        system_instructions: str,
        retrieved_context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream conversational response text tokens for low latency."""
        pass

    @abstractmethod
    async def extract_linguistic_signals(self, text: str) -> LinguisticSignals:
        """Extract structured distress and danger indicators from transcript."""
        pass
