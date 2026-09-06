import pytest
from app.domain.models import (
    AcousticSignals,
    EmotionSignals,
    LinguisticSignals,
    DistressState,
    RiskLevel
)
from app.distress.fusion_engine import DistressFusionEngine
from app.trauma.controller import TraumaController


def test_svi_and_mandated_indicators_detection():
    """Verify SVI calculation and detection of PS 26093 mandated trauma indicators."""
    engine = DistressFusionEngine()
    state = DistressState(call_id="test_ps26093")

    # Simulate an atrocity victim experiencing caste boycott, threats, and acute anxiety
    acoustic = AcousticSignals(
        mean_pitch_f0=280.0,
        pitch_variability=52.0,
        pause_ratio=0.48,
        jitter=0.055
    )
    emotion = EmotionSignals(
        probabilities={"fear": 0.72, "sadness": 0.20, "neutral": 0.08},
        dominant_emotion="fear"
    )
    linguistic = LinguisticSignals(
        risk_indicators=["threat", "boycott", "fear"],
        threat_severity=0.75
    )

    updated_state = engine.fuse(state, acoustic, emotion, linguistic, silence_duration_ms=1500)

    # 1. Verify SVI is computed and categorized as HIGH or CRITICAL
    assert updated_state.svi_score >= 0.65
    assert updated_state.current_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    # 2. Verify sub-indices are properly calculated
    assert "acoustic_stress" in updated_state.sub_indices
    assert "emotional_trauma" in updated_state.sub_indices
    assert "linguistic_threat" in updated_state.sub_indices
    assert "conversational_hesitation" in updated_state.sub_indices

    # 3. Verify PS 26093 mandated trauma indicators
    flags = updated_state.safety_flags
    assert flags.intimidation_threat is True
    assert flags.social_boycott_isolation is True
    assert flags.fear_anxiety is True


def test_automated_public_service_recommendations():
    """Verify automated recommendations for police, medical, legal aid, counselling, and witness protection."""
    controller = TraumaController()
    state = DistressState(
        call_id="test_recs",
        rolling_distress_score=0.88,
        current_risk_level=RiskLevel.CRITICAL
    )
    state.safety_flags.immediate_danger = True

    assessment = controller.assess_and_control(
        call_id="test_recs",
        distress_state=state,
        latest_transcript="They have weapons outside our home and are breaking the door!"
    )

    assert assessment.risk_level == RiskLevel.CRITICAL
    assert assessment.svi_score >= 0.85
    assert assessment.svi_percentage >= 85
    assert assessment.requires_human_escalation is True

    # Verify structured multi-agency services
    recs = assessment.recommended_services
    assert any("Police Intervention" in s for s in recs)
    assert any("Medical Assistance" in s for s in recs)
    assert any("Witness Protection" in s for s in recs)
    assert any("Psychological Support" in s for s in recs)
    assert any("Legal Aid" in s for s in recs)


def test_situational_emotion_and_svi_floor_alignment():
    """Verify that calm conversational voice uttering threats or lack of safety gets calibrated fear emotion and aligned SVI."""
    engine = DistressFusionEngine()
    state = DistressState(call_id="test_situation_emotion")

    # Acoustic voice is calm/conversational (speech at normal volume)
    acoustic = AcousticSignals(mean_pitch_f0=145.0, pitch_variability=18.0, pause_ratio=0.25)
    # Raw classifier output before linguistic grounding was neutral
    raw_emotion = EmotionSignals(
        probabilities={"fear": 0.12, "sadness": 0.10, "anger": 0.08, "neutral": 0.70},
        dominant_emotion="neutral",
        confidence=0.70
    )
    # Caller states workplace intimidation and lack of safety: "ମୋତେ ଧମକ ମିଳୁଛି, ମୁଁ ସୁରକ୍ଷିତ ନାହିଁ"
    linguistic = LinguisticSignals(
        risk_indicators=["threat", "fear"],
        threat_severity=0.70
    )

    updated_state = engine.fuse(state, acoustic, raw_emotion, linguistic)

    # 1. Emotion must be calibrated to match the situation (Fear-dominant, NOT neutral)
    calibrated = updated_state.latest_emotion
    assert calibrated.dominant_emotion == "fear"
    assert calibrated.probabilities["fear"] >= 0.65
    assert calibrated.probabilities["neutral"] <= 0.10

    # 2. SVI must be aligned with the High triage level (>= 0.65, not stuck at 0.18)
    assert updated_state.svi_score >= 0.65
    assert updated_state.current_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

