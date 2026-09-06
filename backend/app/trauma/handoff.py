"""
Structured Operator Handoff Generator.
Produces standardized SBAR (Situation, Background, Assessment, Recommendation) reports
for seamless transfer to human helpline supervisors and 112 emergency dispatchers.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from ..domain.models import RiskAssessment, DistressState, AcousticSignals, EmotionSignals


class StructuredHandoffGenerator:
    """
    Generates standardized handoff dossiers for human operators and emergency dispatchers.
    """

    @staticmethod
    def generate_sbar_report(
        call_id: str,
        phone_hash: str,
        detected_language: str,
        assessment: RiskAssessment,
        distress_state: DistressState,
        full_transcript: List[Dict[str, str]],
        acoustic_features: Optional[AcousticSignals] = None,
        emotion_prediction: Optional[EmotionSignals] = None
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive SBAR handoff dictionary.
        """
        # Situation
        situation = (
            f"Call ID: {call_id} | Triage Level: {assessment.risk_level.value} | "
            f"Score: {assessment.risk_score:.2f} | Language: {detected_language}"
        )

        # Background
        caller_turns = [msg["content"] for msg in full_transcript if msg.get("role") in ["caller", "user"]]
        latest_utterance = caller_turns[-1] if caller_turns else "No transcript recorded"
        background = (
            f"Total conversational turns: {len(full_transcript)}. "
            f"Latest caller statement: \"{latest_utterance}\""
        )

        # Assessment
        evidence_str = "; ".join(assessment.evidence) if assessment.evidence else "No specific hazard markers flagged"
        
        f0_val = f"{acoustic_features.mean_pitch_f0:.1f} Hz" if acoustic_features and acoustic_features.mean_pitch_f0 else "N/A"
        jitter_val = f"{acoustic_features.jitter:.4f}" if acoustic_features and acoustic_features.jitter else "N/A"
        pause_val = f"{acoustic_features.pause_ratio:.2f}" if acoustic_features and acoustic_features.pause_ratio else "N/A"
        acoustic_summary = f"Mean F0: {f0_val}, Jitter: {jitter_val}, Pause Ratio: {pause_val}"

        if emotion_prediction and emotion_prediction.probabilities:
            probs = emotion_prediction.probabilities
            fear = probs.get("fear", 0.0)
            sad = probs.get("sadness", 0.0)
            anger = probs.get("anger", 0.0)
            emotion_summary = f"Dominant Emotion: {emotion_prediction.dominant_emotion.upper()} (Fear: {fear:.0%}, Sadness: {sad:.0%}, Anger: {anger:.0%})"
        else:
            emotion_summary = "Emotion baseline normal"

        assessment_text = (
            f"Detected Evidence: {evidence_str}. "
            f"Prosodic Signals: {acoustic_summary}. "
            f"Vocal Emotion: {emotion_summary}."
        )

        # Recommendation
        recommendation = assessment.recommended_action

        return {
            "call_id": call_id,
            "caller_phone_hash": phone_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "detected_language": detected_language,
            "triage": {
                "risk_level": assessment.risk_level.value,
                "risk_score": round(assessment.risk_score, 3),
                "requires_human_escalation": assessment.requires_human_escalation
            },
            "sbar": {
                "situation": situation,
                "background": background,
                "assessment": assessment_text,
                "recommendation": recommendation
            },
            "evidence": assessment.evidence,
            "safety_flags": {
                "immediate_danger": assessment.safety_flags.immediate_danger,
                "self_harm_indicator": assessment.safety_flags.self_harm_indicator,
                "medical_emergency": assessment.safety_flags.medical_emergency,
                "active_violence": assessment.safety_flags.active_violence,
                "weapon_present": assessment.safety_flags.weapon_present
            },
            "transcript_summary": full_transcript[-4:] if len(full_transcript) >= 4 else full_transcript
        }
