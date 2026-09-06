import pytest
from app.domain.models import RiskAssessment, RiskLevel, DistressState, SafetyFlags, AcousticSignals, EmotionSignals
from app.trauma.handoff import StructuredHandoffGenerator


def test_sbar_report_generation():
    call_id = "test_call_sbar_01"
    phone_hash = "hash_12345"
    detected_lang = "or-IN"

    safety_flags = SafetyFlags(immediate_danger=True, weapon_present=True)
    assessment = RiskAssessment(
        call_id=call_id,
        risk_level=RiskLevel.CRITICAL,
        risk_score=0.92,
        confidence=0.90,
        safety_flags=safety_flags,
        evidence=["Threat to life", "Armed intimidation"],
        recommended_action="112 Emergency Dispatch",
        requires_human_escalation=True
    )
    distress_state = DistressState(call_id=call_id, current_risk_level=RiskLevel.CRITICAL)
    full_transcript = [
        {"role": "caller", "content": "Se mate marideba boli kahuchhanti"},
        {"role": "agent", "content": "Apan surakshita achhanti ki?"}
    ]
    acoustic = AcousticSignals(mean_pitch_f0=260.5, jitter=0.045, pause_ratio=0.35)
    emotion = EmotionSignals(
        probabilities={"fear": 0.82, "sadness": 0.10, "anger": 0.05, "neutral": 0.03},
        dominant_emotion="fear",
        confidence=0.85
    )

    report = StructuredHandoffGenerator.generate_sbar_report(
        call_id=call_id,
        phone_hash=phone_hash,
        detected_language=detected_lang,
        assessment=assessment,
        distress_state=distress_state,
        full_transcript=full_transcript,
        acoustic_features=acoustic,
        emotion_prediction=emotion
    )

    assert report["call_id"] == call_id
    assert report["triage"]["risk_level"] == "CRITICAL"
    assert report["triage"]["requires_human_escalation"] is True
    assert "situation" in report["sbar"]
    assert "background" in report["sbar"]
    assert "assessment" in report["sbar"]
    assert "recommendation" in report["sbar"]
    assert "260.5" in report["sbar"]["assessment"]
    assert report["safety_flags"]["immediate_danger"] is True
