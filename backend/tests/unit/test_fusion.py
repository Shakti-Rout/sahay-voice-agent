import pytest
from app.domain.models import (
    AcousticSignals,
    EmotionSignals,
    LinguisticSignals,
    DistressState,
    RiskLevel
)
from app.distress.fusion_engine import DistressFusionEngine


def test_calm_signals_yield_low_risk():
    engine = DistressFusionEngine()
    state = DistressState(call_id="test_calm")

    acoustic = AcousticSignals(mean_pitch_f0=130.0, pitch_variability=12.0, pause_ratio=0.15)
    emotion = EmotionSignals(probabilities={"neutral": 0.85, "fear": 0.05, "sadness": 0.05, "anger": 0.05})
    linguistic = LinguisticSignals(threat_severity=0.0)

    updated_state = engine.fuse(state, acoustic, emotion, linguistic)

    assert updated_state.rolling_distress_score < 0.35
    assert updated_state.current_risk_level == RiskLevel.LOW


def test_acute_distress_yields_high_risk():
    engine = DistressFusionEngine()
    state = DistressState(call_id="test_distress")

    acoustic = AcousticSignals(mean_pitch_f0=310.0, pitch_variability=55.0, pause_ratio=0.55, jitter=0.06)
    emotion = EmotionSignals(probabilities={"fear": 0.82, "sadness": 0.12, "neutral": 0.06})
    linguistic = LinguisticSignals(risk_indicators=["fear", "threat"], threat_severity=0.7)

    updated_state = engine.fuse(state, acoustic, emotion, linguistic)

    assert updated_state.rolling_distress_score >= 0.65
    assert updated_state.current_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
