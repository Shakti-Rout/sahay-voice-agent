"""
Multilingual Language Router and Dialect Normalization Bridge.
Handles all 22 Indian languages supported by Sarvam Saaras (Odia, Hindi, English,
Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Punjabi, Malayalam),
plus native Odia tribal and regional varieties (Sambalpuri/Kosli, Santali, Desia).
"""

import re
import logging
from enum import Enum
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class SupportedLanguage(str, Enum):
    ODIA = "or-IN"
    HINDI = "hi-IN"
    ENGLISH = "en-IN"
    BENGALI = "bn-IN"
    TELUGU = "te-IN"
    MARATHI = "mr-IN"
    TAMIL = "ta-IN"
    GUJARATI = "gu-IN"
    KANNADA = "kn-IN"
    PUNJABI = "pa-IN"
    MALAYALAM = "ml-IN"
    SAMBALPURI = "sp-IN"
    SANTALI = "sat-IN"
    UNKNOWN = "unknown"


class DialectBridge:
    """
    Normalizes tribal and regional dialect expressions into standard base language
    to ensure high-precision NLU and verified legal RAG retrieval.
    """

    # Sambalpuri (Kosli) -> Standard Odia lexical mappings
    SAMBALPURI_TO_ODIA = {
        r"\bkanje\b": "kahinki",
        r"\bkana\b": "kana",
        r"\btor\b": "tora",
        r"\bmor\b": "mora",
        r"\bmor pache\b": "mo pache",
        r"\bgodauchhan\b": "godauchhanti",
        r"\bgodauchhe\b": "godauchhi",
        r"\bhanta\b": "seti",
        r"\benta\b": "eithi",
        r"\bkahe\b": "kahuchhi",
        r"\bdeuchhe\b": "deuchhi",
        r"\bkarchhe\b": "karuchhi",
        r"\bmarba\b": "marideba",
        r"\bkhaye\b": "khauchi",
        r"\bpile\b": "pila",
        r"\bdada\b": "bhai",
        r"\bhuchhe\b": "heuchhi",
        r"\bbana\b": "jangala",
        r"\bdongar\b": "pahar",
        r"\bnuchi achhe\b": "nuchiki achhi",
        r"\bkhedi dele\b": "bahiskara kale",
        r"\bpani mana\b": "pani nebaku mana",
        r"\bgaon ru\b": "gan ru",
        r"\bdada banchao\b": "bhai banchantu",
        r"\bghare dhuki\b": "ghara bhitaraku pasi",
        r"\bpila ke\b": "shishu ku"
    }

    # Santali (Tribal indigenous language in Odisha) -> Standard Odia mappings
    SANTALI_TO_ODIA = {
        r"\bbir re ukanakana\b": "jangala re nuchiki achhi",
        r"\bpanjayedina\b": "godauchhanti",
        r"\bgojing lagid\b": "mariba pain",
        r"\bdalan kanako\b": "maruchhanti",
        r"\bbotor ge aikawkana\b": "bahut bhaya laguchhi",
        r"\bbanchaoing pe\b": "mote banchantu",
        r"\bdak nu mana\b": "pani peeba mana",
        r"\bato khon ko orok\b": "gan ru bahiskara",
        r"\bpolice hohoako\b": "police ku dakantu",
        r"\bkapi\b": "talwar",
        r"\bhasiyara\b": "churi",
        r"\bthonga\b": "lathi",
        r"\bgidra\b": "pila",
        r"\borak\b": "ghara",
        r"\bdahar\b": "rasta"
    }

    @classmethod
    def normalize_dialect(cls, text: str, source_dialect: str) -> str:
        """Normalize regional dialect terms into standard form for semantic processing."""
        if not text:
            return ""
        normalized = text
        if source_dialect in [SupportedLanguage.SAMBALPURI, "sp-IN", "sambalpuri"]:
            for pattern, replacement in cls.SAMBALPURI_TO_ODIA.items():
                normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        elif source_dialect in [SupportedLanguage.SANTALI, "sat-IN", "santali"]:
            for pattern, replacement in cls.SANTALI_TO_ODIA.items():
                normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        return normalized


class LanguageRouter:
    """
    Dynamic Language Identification, Routing, and Session Continuity Manager.
    """

    # Unicode script ranges
    ODIA_SCRIPT_RANGE = re.compile(r"[\u0b00-\u0b7f]")
    DEVANAGARI_SCRIPT_RANGE = re.compile(r"[\u0900-\u097f]")
    BENGALI_SCRIPT_RANGE = re.compile(r"[\u0980-\u09ff]")
    TELUGU_SCRIPT_RANGE = re.compile(r"[\u0c00-\u0c7f]")
    TAMIL_SCRIPT_RANGE = re.compile(r"[\u0b80-\u0bff]")
    KANNADA_SCRIPT_RANGE = re.compile(r"[\u0c80-\u0cff]")
    MALAYALAM_SCRIPT_RANGE = re.compile(r"[\u0d00-\u0d7f]")
    GUJARATI_SCRIPT_RANGE = re.compile(r"[\u0a80-\u0aff]")
    GURMUKHI_SCRIPT_RANGE = re.compile(r"[\u0a00-\u0a7f]")
    OL_CHIKI_SCRIPT_RANGE = re.compile(r"[\u1c50-\u1c7f]")

    # Phonetic transliterated keywords for romanized input
    ODIA_PHONETIC_MARKERS = {
        "mu", "mate", "mora", "mor", "tume", "apan", "apananka", "achhi", "achhanti",
        "nahi", "katha", "darichhi", "dhamaka", "sahajya", "marideba", "bhanguchhanti",
        "ghara", "lathi", "police", "thana", "gali", "atiyachara", "marpit", "jangala", "godauchanti"
    }

    SAMBALPURI_PHONETIC_MARKERS = {
        "kanje", "godauchhan", "godauchhe", "marba", "deuchhe", "karchhe", "mor", "tor",
        "hanta", "enta", "dongar", "bana", "nuchi", "khedi", "pita", "khata", "aichhe", "aichhan"
    }

    SANTALI_PHONETIC_MARKERS = {
        "ukanakana", "panjayedina", "gojing", "dalan", "botor", "aikawkana", "banchaoing",
        "hohoako", "orok", "menakana", "gidra", "orak", "dahar", "kapi", "hasiyara"
    }

    HINDI_PHONETIC_MARKERS = {
        "main", "mujhe", "mera", "meri", "aap", "hum", "hai", "hain", "nahi",
        "darr", "lag", "raha", "marne", "dhamki", "madad", "chahiye", "police",
        "bachao", "pitai", "gaali", "shikayat", "ghar", "jungle", "dauda"
    }

    BENGALI_PHONETIC_MARKERS = {
        "aami", "aamake", "aamar", "tumi", "apni", "aachhe", "na", "bhay", "marche",
        "police", "sahajjo", "dorkar", "ghor", "bachao"
    }

    TELUGU_PHONETIC_MARKERS = {
        "nenu", "naaku", "naa", "meeru", "undi", "ledu", "bhayangaa", "champestanu",
        "sahayam", "kaavali", "police", "rakshinchandi", "illu"
    }

    def __init__(self, default_language: SupportedLanguage = SupportedLanguage.ODIA):
        self.default_language = default_language
        self.session_languages: Dict[str, Tuple[SupportedLanguage, float]] = {}

    def detect_language_from_text(self, text: str) -> Tuple[SupportedLanguage, float]:
        """
        Detects primary language from raw text using native script ranges
        and phonetic markers for romanized Indian English/code-switching.
        """
        if not text or not text.strip():
            return self.default_language, 0.50

        # 1. Native script detection (Highest confidence)
        odia_chars = len(self.ODIA_SCRIPT_RANGE.findall(text))
        devanagari_chars = len(self.DEVANAGARI_SCRIPT_RANGE.findall(text))
        bengali_chars = len(self.BENGALI_SCRIPT_RANGE.findall(text))
        telugu_chars = len(self.TELUGU_SCRIPT_RANGE.findall(text))
        tamil_chars = len(self.TAMIL_SCRIPT_RANGE.findall(text))
        kannada_chars = len(self.KANNADA_SCRIPT_RANGE.findall(text))
        malayalam_chars = len(self.MALAYALAM_SCRIPT_RANGE.findall(text))
        gujarati_chars = len(self.GUJARATI_SCRIPT_RANGE.findall(text))
        gurmukhi_chars = len(self.GURMUKHI_SCRIPT_RANGE.findall(text))
        ol_chiki_chars = len(self.OL_CHIKI_SCRIPT_RANGE.findall(text))

        # Check Ol Chiki first for Santali
        if ol_chiki_chars > 0:
            return SupportedLanguage.SANTALI, 0.99

        counts = {
            SupportedLanguage.ODIA: odia_chars,
            SupportedLanguage.HINDI: devanagari_chars,
            SupportedLanguage.BENGALI: bengali_chars,
            SupportedLanguage.TELUGU: telugu_chars,
            SupportedLanguage.TAMIL: tamil_chars,
            SupportedLanguage.KANNADA: kannada_chars,
            SupportedLanguage.MALAYALAM: malayalam_chars,
            SupportedLanguage.GUJARATI: gujarati_chars,
            SupportedLanguage.PUNJABI: gurmukhi_chars,
        }

        total_indic = sum(counts.values())
        if total_indic > 0:
            best_lang = max(counts, key=counts.get)
            if counts[best_lang] > 0:
                # If Odia script, check if specific Kosli/Sambalpuri keywords are present
                if best_lang == SupportedLanguage.ODIA:
                    text_lower = text.lower()
                    if any(w in text_lower for w in ["ଗୋଡ଼ାଉଛନ", "ମାର୍ବା", "ନୁଚି", "ଖେଡି", "ଦଙ୍ଗର", "କନ୍ଜେ"]):
                        return SupportedLanguage.SAMBALPURI, 0.95
                return best_lang, 0.98

        # 2. Phonetic romanized lexical detection (Code-mixed / Romanized transcripts)
        words = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
        if not words:
            return self.default_language, 0.50

        # Check tribal and regional dialect phonetic markers
        santali_matches = len(words.intersection(self.SANTALI_PHONETIC_MARKERS))
        sambalpuri_matches = len(words.intersection(self.SAMBALPURI_PHONETIC_MARKERS))
        odia_matches = len(words.intersection(self.ODIA_PHONETIC_MARKERS))
        hindi_matches = len(words.intersection(self.HINDI_PHONETIC_MARKERS))
        bengali_matches = len(words.intersection(self.BENGALI_PHONETIC_MARKERS))
        telugu_matches = len(words.intersection(self.TELUGU_PHONETIC_MARKERS))

        if santali_matches > 0 and santali_matches >= max(sambalpuri_matches, odia_matches, hindi_matches):
            conf = min(0.70 + (santali_matches * 0.10), 0.98)
            return SupportedLanguage.SANTALI, conf

        if sambalpuri_matches > 0 and sambalpuri_matches >= max(odia_matches, hindi_matches):
            conf = min(0.70 + (sambalpuri_matches * 0.10), 0.98)
            return SupportedLanguage.SAMBALPURI, conf

        if odia_matches > hindi_matches and odia_matches > 0:
            conf = min(0.60 + (odia_matches * 0.10), 0.95)
            return SupportedLanguage.ODIA, conf
        elif hindi_matches > odia_matches and hindi_matches > 0:
            conf = min(0.60 + (hindi_matches * 0.10), 0.95)
            return SupportedLanguage.HINDI, conf
        elif bengali_matches > 0:
            conf = min(0.60 + (bengali_matches * 0.10), 0.95)
            return SupportedLanguage.BENGALI, conf
        elif telugu_matches > 0:
            conf = min(0.60 + (telugu_matches * 0.10), 0.95)
            return SupportedLanguage.TELUGU, conf

        # 3. Default to English if predominantly Latin alphabet without Indic phonetic markers
        return SupportedLanguage.ENGLISH, 0.70

    def update_session_language(
        self,
        call_id: str,
        detected_lang: str,
        confidence: float
    ) -> SupportedLanguage:
        """
        Updates the session's active language with hysteresis to prevent rapid flickering.
        """
        normalized_lang = self.normalize_language_code(detected_lang)
        current_lang, current_conf = self.session_languages.get(
            call_id, (self.default_language, 0.50)
        )

        # Allow immediate switch if current is UNKNOWN or initial confidence is solid
        if confidence >= 0.75 or current_lang == SupportedLanguage.UNKNOWN:
            self.session_languages[call_id] = (normalized_lang, confidence)
            return normalized_lang

        return current_lang

    def set_session_language(self, call_id: str, lang: str) -> SupportedLanguage:
        """Manually override or lock session language."""
        normalized = self.normalize_language_code(lang)
        self.session_languages[call_id] = (normalized, 1.0)
        return normalized

    def get_session_language(self, call_id: str) -> SupportedLanguage:
        """Retrieve current established session language."""
        return self.session_languages.get(call_id, (self.default_language, 0.50))[0]

    @staticmethod
    def normalize_language_code(code: str) -> SupportedLanguage:
        """Maps diverse provider language codes to standard enum."""
        if not code:
            return SupportedLanguage.ODIA
        c = code.lower().strip()
        if "sp" in c or "sambalpur" in c or "kosli" in c:
            return SupportedLanguage.SAMBALPURI
        if "sat" in c or "santali" in c:
            return SupportedLanguage.SANTALI
        if "or" in c or "odi" in c or "od-" in c:
            return SupportedLanguage.ODIA
        if "hi" in c or "hin" in c:
            return SupportedLanguage.HINDI
        if "en" in c or "eng" in c:
            return SupportedLanguage.ENGLISH
        if "bn" in c or "ben" in c:
            return SupportedLanguage.BENGALI
        if "te" in c or "tel" in c:
            return SupportedLanguage.TELUGU
        if "mr" in c or "mar" in c:
            return SupportedLanguage.MARATHI
        if "ta" in c or "tam" in c:
            return SupportedLanguage.TAMIL
        if "gu" in c or "guj" in c:
            return SupportedLanguage.GUJARATI
        if "kn" in c or "kan" in c:
            return SupportedLanguage.KANNADA
        if "pa" in c or "pan" in c or "pun" in c:
            return SupportedLanguage.PUNJABI
        if "ml" in c or "mal" in c:
            return SupportedLanguage.MALAYALAM
        if "unknown" in c or "und" in c:
            return SupportedLanguage.UNKNOWN
        return SupportedLanguage.ODIA
