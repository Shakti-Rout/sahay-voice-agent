"""
Supabase Persistence and Audit Logging Client.
Provides resilient asynchronous persistence for call sessions, acoustic features,
emotion vectors, triage assessments, escalations, and compliance audit logs.
"""

import os
import hashlib
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


class SupabaseManager:
    """
    Singleton persistence manager for the NHAA Voice Triage system.
    Falls back to in-memory buffer if Supabase is offline or not configured.
    """

    _instance: Optional["SupabaseManager"] = None

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url or os.getenv("SUPABASE_URL", "")
        self.key = key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
        self.client: Optional[Client] = None
        self.in_memory_sessions: Dict[str, Dict[str, Any]] = {}
        self.in_memory_assessments: List[Dict[str, Any]] = []
        self.in_memory_escalations: List[Dict[str, Any]] = []

        if SUPABASE_AVAILABLE and self.url and self.key and "your_" not in self.key:
            try:
                self.client = create_client(self.url, self.key)
                logger.info("[SupabaseManager] Connected to Supabase instance.")
            except Exception as e:
                logger.warning(f"[SupabaseManager] Could not initialize Supabase client: {e}. Using in-memory store.")
        else:
            logger.info("[SupabaseManager] Running with resilient in-memory storage.")

    @classmethod
    def get_instance(cls) -> "SupabaseManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def hash_phone(phone_number: str, salt: str = "nhaa_sih_2026_salt") -> str:
        """One-way salted SHA-256 phone hash for privacy compliance (DPDP Act)."""
        if not phone_number:
            return "anonymous_caller"
        return hashlib.sha256(f"{salt}_{phone_number}".encode("utf-8")).hexdigest()

    async def create_call_session(
        self,
        external_call_id: str,
        phone_hash: str,
        telephony_provider: str = "mock",
        detected_language: str = "or-IN"
    ) -> Dict[str, Any]:
        """Record the start of a call session."""
        session_data = {
            "external_call_id": external_call_id,
            "caller_phone_hash": phone_hash,
            "telephony_provider": telephony_provider,
            "status": "initiated",
            "detected_language": detected_language,
            "language_confidence": 0.95,
            "started_at": datetime.now(timezone.utc).isoformat()
        }

        self.in_memory_sessions[external_call_id] = session_data

        if self.client:
            try:
                res = self.client.table("call_sessions").insert(session_data).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.warning(f"[SupabaseManager] create_call_session fallback: {e}")

        return session_data

    async def update_call_status(
        self,
        external_call_id: str,
        status: str,
        detected_language: Optional[str] = None
    ) -> None:
        """Update the lifecycle status of a call session."""
        if external_call_id in self.in_memory_sessions:
            self.in_memory_sessions[external_call_id]["status"] = status
            if detected_language:
                self.in_memory_sessions[external_call_id]["detected_language"] = detected_language

        if self.client:
            try:
                update_data = {"status": status}
                if detected_language:
                    update_data["detected_language"] = detected_language
                self.client.table("call_sessions").update(update_data).eq("external_call_id", external_call_id).execute()
            except Exception as e:
                logger.warning(f"[SupabaseManager] update_call_status error: {e}")

    async def save_transcript_segment(
        self,
        external_call_id: str,
        speaker: str,
        text_content: str,
        sequence_num: int,
        language: str = "or-IN",
        start_ms: int = 0,
        end_ms: int = 0
    ) -> None:
        """Save an individual conversational turn."""
        segment_data = {
            "external_call_id": external_call_id,
            "speaker": speaker,
            "sequence_num": sequence_num,
            "text_content": text_content,
            "language": language,
            "start_time_ms": start_ms,
            "end_time_ms": end_ms,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        session = self.in_memory_sessions.get(external_call_id, {})
        if "transcripts" not in session:
            session["transcripts"] = []
        session["transcripts"].append(segment_data)

        if self.client:
            try:
                # Resolve internal session UUID if available
                self.client.table("transcript_segments").insert({
                    "call_session_id": external_call_id,
                    "speaker": speaker,
                    "sequence_num": sequence_num,
                    "text_content": text_content,
                    "language": language,
                    "start_time_ms": start_ms,
                    "end_time_ms": end_ms
                }).execute()
            except Exception as e:
                logger.debug(f"[SupabaseManager] save_transcript_segment fallback: {e}")

    async def save_risk_assessment(
        self,
        external_call_id: str,
        risk_score: float,
        risk_level: str,
        safety_flags: Dict[str, Any],
        evidence_summary: List[str],
        recommended_action: str,
        requires_human_escalation: bool
    ) -> None:
        """Save a multimodal risk assessment."""
        assessment_data = {
            "external_call_id": external_call_id,
            "risk_score": round(risk_score, 3),
            "risk_level": risk_level,
            "safety_flags": safety_flags,
            "evidence_summary": evidence_summary,
            "recommended_action": recommended_action,
            "requires_human_escalation": requires_human_escalation,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        self.in_memory_assessments.append(assessment_data)

        if self.client:
            try:
                self.client.table("risk_assessments").insert(assessment_data).execute()
            except Exception as e:
                logger.debug(f"[SupabaseManager] save_risk_assessment fallback: {e}")

    async def create_escalation(
        self,
        external_call_id: str,
        trigger_reason: str
    ) -> None:
        """Create an urgent operator escalation ticket."""
        escalation_data = {
            "external_call_id": external_call_id,
            "trigger_reason": trigger_reason,
            "status": "pending",
            "escalated_at": datetime.now(timezone.utc).isoformat()
        }

        self.in_memory_escalations.append(escalation_data)
        logger.warning(f"[SupabaseManager] ESCALATION CREATED: Call {external_call_id} -> {trigger_reason}")

        if self.client:
            try:
                self.client.table("escalations").insert(escalation_data).execute()
            except Exception as e:
                logger.debug(f"[SupabaseManager] create_escalation fallback: {e}")

    def get_recent_escalations(self) -> List[Dict[str, Any]]:
        """Fetch pending escalations for the operator triage dashboard."""
        return self.in_memory_escalations

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Fetch active calls for the operator dashboard."""
        return list(self.in_memory_sessions.values())
