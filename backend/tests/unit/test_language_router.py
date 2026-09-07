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

    # Bengali script
    bengali_text = "আমি খুব ভয়ে আছি। আমাকে বাঁচান।"
    lang, conf = router.detect_language_from_text(bengali_text)
    assert lang == SupportedLanguage.BENGALI
    assert conf >= 0.90

    # Telugu script
    telugu_text = "నాకు చాలా భయంగా ఉంది. నన్ను రక్షించండి."
    lang, conf = router.detect_language_from_text(telugu_text)
    assert lang == SupportedLanguage.TELUGU
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

    # Romanized Sambalpuri
    sp_roman = "kanje godauchhan mor pache bana dongar re nuchi achhe"
    lang, conf = router.detect_language_from_text(sp_roman)
    assert lang == SupportedLanguage.SAMBALPURI

    # Romanized Santali
    sat_roman = "bir re ukanakana gojing lagid ko panjayedina banchaoing pe"
    lang, conf = router.detect_language_from_text(sat_roman)
    assert lang == SupportedLanguage.SANTALI


def test_sambalpuri_dialect_normalization():
    sambalpuri_text = "se mate gali deuchhe mor ghare marba boli kahe"
    normalized = DialectBridge.normalize_dialect(sambalpuri_text, SupportedLanguage.SAMBALPURI)

    # "deuchhe" -> "deuchhi", "mor" -> "mora", "marba" -> "marideba", "kahe" -> "kahuchhi"
    assert "deuchhi" in normalized
    assert "mora" in normalized
    assert "marideba" in normalized
    assert "kahuchhi" in normalized


def test_santali_dialect_normalization():
    santali_text = "bir re ukanakana gojing lagid ko panjayedina dalan kanako"
    normalized = DialectBridge.normalize_dialect(santali_text, SupportedLanguage.SANTALI)

    assert "jangala re nuchiki achhi" in normalized
    assert "mariba pain" in normalized
    assert "godauchhanti" in normalized
    assert "maruchhanti" in normalized


def test_session_language_update():
    router = LanguageRouter()
    call_id = "test_call_lang_1"

    # Initially defaults
    assert router.get_session_language(call_id) == SupportedLanguage.ODIA

    # High confidence Hindi updates session
    active = router.update_session_language(call_id, "hi-IN", 0.95)
    assert active == SupportedLanguage.HINDI
    assert router.get_session_language(call_id) == SupportedLanguage.HINDI

    # Update to Telugu
    active_te = router.update_session_language(call_id, "te-IN", 0.95)
    assert active_te == SupportedLanguage.TELUGU
    assert router.get_session_language(call_id) == SupportedLanguage.TELUGU
