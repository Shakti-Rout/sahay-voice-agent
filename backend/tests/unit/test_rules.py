import pytest
from app.domain.models import RiskLevel, SafetyFlags
from app.trauma.rules import SafetyRulesEngine


def test_suicide_trigger_forces_critical():
    flags = SafetyFlags()
    transcript = "Mo jeeban re kichi nahi, mu suicide karidebi."
    level, is_override, evidence = SafetyRulesEngine.evaluate_overrides(transcript, flags)

    assert is_override is True
    assert level == RiskLevel.CRITICAL
    assert flags.immediate_danger is True
    assert flags.self_harm_indicator is True
    assert any("suicide" in ev for ev in evidence)


def test_weapon_trigger_forces_critical():
    flags = SafetyFlags()
    transcript = "Unke paas talwar aur banduk hai, darwaza tod rahe hain!"
    level, is_override, evidence = SafetyRulesEngine.evaluate_overrides(transcript, flags)

    assert is_override is True
    assert level == RiskLevel.CRITICAL
    assert flags.weapon_present is True


def test_high_threat_trigger():
    flags = SafetyFlags()
    transcript = "Se mane mo ghara bahare thia hoichhanti o marideba boli dhamaki deichhanti."
    level, is_override, evidence = SafetyRulesEngine.evaluate_overrides(transcript, flags)

    assert is_override is True
    assert level == RiskLevel.HIGH


def test_benign_transcript_no_override():
    flags = SafetyFlags()
    transcript = "I would like information regarding the SC scholarship scheme."
    level, is_override, evidence = SafetyRulesEngine.evaluate_overrides(transcript, flags)

    assert is_override is False
    assert level == RiskLevel.LOW
    assert len(evidence) == 0
