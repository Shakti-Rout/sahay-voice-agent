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


def test_desia_dialect_normalization():
    desia_text = "mor pache padila godauche dada banchao bhay laguche khedi delu"
    normalized = DialectBridge.normalize_dialect(desia_text, SupportedLanguage.DESIA)

    assert "mo pache padichhi" in normalized
    assert "godauchhi" in normalized
    assert "bhai banchantu" in normalized
    assert "bhaya laguchhi" in normalized
    assert "bahiskara kale" in normalized


def test_kui_dialect_normalization():
    kui_text = "aanu gahi vespa naju re iddu haji re daha"
    normalized = DialectBridge.normalize_dialect(kui_text, SupportedLanguage.KUI)

    assert "mu" in normalized
    assert "bhaya" in normalized
    assert "kahiba" in normalized
    assert "gan" in normalized
    assert "ghara" in normalized
    assert "rasta" in normalized
    assert "pani" in normalized


def test_broken_odia_colloquial_normalization():
    broken_text = "mate dar laguchi chua mari bachao dada pani nai grama bahara"
    normalized = DialectBridge.normalize_dialect(broken_text, SupportedLanguage.ODIA)

    assert "mate bhaya laguchi" in normalized
    assert "pila ku maruchanti" in normalized
    assert "bhai banchantu" in normalized
    assert "pani miluni" in normalized
    assert "gan ru bahiskara" in normalized


def test_desia_and_kui_phonetic_detection():
    router = LanguageRouter()

    # Desia romanized input
    desia_roman = "mor pache padila godauche khedi delu banchao dada"
    lang, conf = router.detect_language_from_text(desia_roman)
    assert lang == SupportedLanguage.DESIA

    # Kui romanized input
    kui_roman = "aanu aane gida mera haji gahi vespa naju iddu daha"
    lang_kui, conf_kui = router.detect_language_from_text(kui_roman)
    assert lang_kui == SupportedLanguage.KUI


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

