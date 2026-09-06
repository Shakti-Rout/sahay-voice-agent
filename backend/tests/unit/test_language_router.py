import pytest
from app.language.router import LanguageRouter, DialectBridge, SupportedLanguage


def test_native_script_detection():
    router = LanguageRouter()

    # Odia script
    odia_text = "ମୁଁ ବହୁତ ଡରିଯାଇଛି। ସେ ମତେ ଧମକ ଦେଇଛି।"
    lang, conf = router.detect_language_from_text(odia_text)
    assert lang == SupportedLanguage.ODIA
    assert conf >= 0.90

    # Devanagari script (Hindi)
    hindi_text = "मुझे बहुत डर लग रहा है। उसने मुझे धमकी दी है।"
    lang, conf = router.detect_language_from_text(hindi_text)
    assert lang == SupportedLanguage.HINDI
    assert conf >= 0.90


def test_phonetic_romanized_detection():
    router = LanguageRouter()

    # Romanized Odia
    odia_roman = "Mu bahut darichhi se mate marideba boli dhamaka deichhi"
    lang, conf = router.detect_language_from_text(odia_roman)
    assert lang == SupportedLanguage.ODIA

    # Romanized Hindi
    hindi_roman = "Mujhe bahut darr lag raha hai police ki madad chahiye"
    lang, conf = router.detect_language_from_text(hindi_roman)
    assert lang == SupportedLanguage.HINDI


def test_sambalpuri_dialect_normalization():
    sambalpuri_text = "se mate gali deuchhe mor ghare marba boli kahe"
    normalized = DialectBridge.normalize_dialect(sambalpuri_text, SupportedLanguage.SAMBALPURI)

    # "deuchhe" -> "deuchhi", "mor" -> "mora", "marba" -> "marideba", "kahe" -> "kahuchhi"
    assert "deuchhi" in normalized
    assert "mora" in normalized
    assert "marideba" in normalized
    assert "kahuchhi" in normalized


def test_session_language_update():
    router = LanguageRouter()
    call_id = "test_call_lang_1"

    # Initially defaults
    assert router.get_session_language(call_id) == SupportedLanguage.ODIA

    # High confidence Hindi updates session
    active = router.update_session_language(call_id, "hi-IN", 0.95)
    assert active == SupportedLanguage.HINDI
    assert router.get_session_language(call_id) == SupportedLanguage.HINDI
