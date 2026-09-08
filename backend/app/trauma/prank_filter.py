"""
Prank & Spam Precaution Filter for NHAA 14566 Helpline.
Protects emergency PCR 112 dispatchers and legal officers by filtering:
- Empty audio / premature hangups (< 2 seconds)
- Repetitive laughter, gibberish, or test chatter
- Explicit prank keywords ("timepass", "masti", "prank", "fake call", "mazak")
- Pure background noise with zero distress/grievance words

Validates legitimate citizen complaints:
- Recognizes authentic grievances across Odia, Sambalpuri, Santali, Kui, Desia, Hindi, and English
- Automatically provisions verified Complaint Tickets (TKT-YYYY-XXXX) for valid cases.
"""

import re
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PrankEvaluationResult(BaseModel):
    is_legitimate: bool
    is_prank: bool
    confidence: float
    reason: str
    ticket_id: Optional[str] = None
    category: str = "Unclassified"


class PrankFilter:
    """Precautionary gate evaluating call legitimacy before registering official complaints."""

    EXPLICIT_PRANK_KEYWORDS = {
        "prank", "mazak", "masti", "timepass", "time pass", "joke", "fake call",
        "lol", "haha", "testing", "test call", "kuch nahi", "kichi nahi", "maja laguchi",
        "pagala", "prank karuchi", "camera kaha hai", "who are you bro", "bye bye"
    }

    GENUINE_GRIEVANCE_INDICATORS = {
        "bipad", "khatra", "danger", "police", "maruchi", "maruchhanti", "pita", "godauchanti",
        "godauchhan", "nuchi", "jangala", "dongar", "bana", "darr", "bhaya", "help", "bachao",
        "sahajya", "banchao", "dhamki", "threat", "gali", "atiyachara", "bahiskara", "khedi",
        "pani mana", "dak nu mana", "tube-well", "hospital", "rakta", "bleeding", "ambulance",
        "112", "14566", "fir", "thana", "poa", "sc st", "dalit", "adivasi", "havba", "saaha",
        "pidisenji", "koruche", "marbar"
    }

    @classmethod
    def evaluate(
        cls,
        call_id: str,
        transcripts: List[str],
        risk_score: float,
        duration_seconds: float = 0.0,
        safety_flags: Optional[Dict[str, Any]] = None
    ) -> PrankEvaluationResult:
        """
        Evaluates whether a call is a genuine citizen complaint or a prank/spam call.
        """
        combined_text = " ".join(transcripts or []).lower().strip()
        words = set(re.findall(r"\w+", combined_text))

        # 1. Immediate Safety Flag override: If any critical safety flag is present, ALWAYS legitimate
        if safety_flags:
            for flag, active in safety_flags.items():
                if active and flag in ["active_assault", "death_threat", "forest_pursuit", "suicidal_ideation"]:
                    ticket_id = f"TKT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                    return PrankEvaluationResult(
                        is_legitimate=True,
                        is_prank=False,
                        confidence=0.99,
                        reason="CRITICAL_SAFETY_OVERRIDE_VALIDATED",
                        ticket_id=ticket_id,
                        category="Immediate_Emergency"
                    )

        # 2. Check for explicit prank/trolling keywords
        prank_matches = words.intersection(cls.EXPLICIT_PRANK_KEYWORDS)
        if len(prank_matches) > 0 and risk_score < 0.30:
            logger.info(f"[PrankFilter] Call {call_id} flagged as PRANK: matched keywords {prank_matches}")
            return PrankEvaluationResult(
                is_legitimate=False,
                is_prank=True,
                confidence=0.92,
                reason=f"EXPLICIT_PRANK_KEYWORD_MATCH: {', '.join(prank_matches)}",
                ticket_id=None,
                category="Prank_Spam"
            )

        # 3. Check for ultra-short, empty, or silent audio
        total_words = len(words)
        if total_words < 2 and duration_seconds < 3.0:
            logger.info(f"[PrankFilter] Call {call_id} rejected: empty audio / silent hangup ({total_words} words, {duration_seconds}s)")
            return PrankEvaluationResult(
                is_legitimate=False,
                is_prank=True,
                confidence=0.88,
                reason="EMPTY_AUDIO_OR_PREMATURE_HANGUP",
                ticket_id=None,
                category="Incomplete_Call"
            )

        # 4. Check for genuine grievance or distress content
        grievance_matches = words.intersection(cls.GENUINE_GRIEVANCE_INDICATORS)
        has_distress = risk_score >= 0.25 or len(grievance_matches) >= 1

        if has_distress or total_words >= 6:
            ticket_id = f"TKT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            category = "Caste_Atrocity_or_Distress" if len(grievance_matches) >= 1 else "Citizen_Grievance"
            return PrankEvaluationResult(
                is_legitimate=True,
                is_prank=False,
                confidence=0.95,
                reason=f"AUTHENTIC_GRIEVANCE_CONFIRMED: {len(grievance_matches)} indicators, risk score {risk_score:.2f}",
                ticket_id=ticket_id,
                category=category
            )

        # 5. Low information / noise default filter
        return PrankEvaluationResult(
            is_legitimate=False,
            is_prank=True,
            confidence=0.75,
            reason="INSUFFICIENT_INFORMATION_NO_DISTRESS_OR_GRIEVANCE_DETECTED",
            ticket_id=None,
            category="Non_Actionable"
        )
