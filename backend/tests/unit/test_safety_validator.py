import pytest
from app.safety.validator import SafetyValidator


def test_approved_helpline_numbers_allowed():
    text = "Please call our helpline 14566 or emergency 112 for immediate assistance."
    safe_text, is_clean = SafetyValidator.validate(text, "en")
    assert is_clean is True
    assert safe_text == text


def test_hallucinated_number_blocked():
    text = "Call officer Sharma directly at 9876543210 for immediate help."
    safe_text, is_clean = SafetyValidator.validate(text, "en")
    assert is_clean is False
    assert "9876543210" not in safe_text


def test_clinical_diagnosis_blocked():
    text = "Based on your voice, I diagnose you with clinical depression and PTSD."
    safe_text, is_clean = SafetyValidator.validate(text, "en")
    assert is_clean is False
    assert "diagnose" not in safe_text.lower()
    assert "ptsd" not in safe_text.lower()


def test_victim_blaming_blocked():
    text = "This happened because it was your fault for going outside alone."
    safe_text, is_clean = SafetyValidator.validate(text, "en")
    assert is_clean is False
    assert "your fault" not in safe_text.lower()
