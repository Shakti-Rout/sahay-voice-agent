"""
Multilingual Language Router and Dialect Normalization Bridge.
Handles Odia, Hindi, English, code-mixed varieties, and tribal/regional dialects (Sambalpuri, Santali).
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
    SAMBALPURI = "sp-IN"
    SANTALI = "sat-IN"
    UNKNOWN = "und"


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
        r"\bhanta\b": "seti",
        r"\benta\b": "eithi",
        r"\bkahe\b": "kahuchhi",
        r"\bdeuchhe\b": "deuchhi",
        r"\bkarchhe\b": "karuchhi",
        r"\bmarba\b": "marideba",
        r"\bkhaye\b": "khauchi",
        r"\bpile\b": "pila",
        r"\bdada\b": "bhai",
        r"\bhuchhe\b": "heuchhi"
    }

    @classmethod
    def normalize_dialect(cls, text: str, source_dialect: str) -> str:
        """Normalize regional dialect terms into standard form for semantic processing."""
        if not text:
            return ""
        normalized = text
        if source_dialect == SupportedLanguage.SAMBALPURI:
            for pattern, replacement in cls.SAMBALPURI_TO_ODIA.items():
                normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        return normalized


class LanguageRouter:
    """
    Dynamic Language Identification, Routing, and Session Continuity Manager.
    """

    ODIA_SCRIPT_RANGE = re.compile(r"[\u0b00-\u0b7f]")
    DEVANAGARI_SCRIPT_RANGE = re.compile(r"[\u0900-\u097f]")
    BENGALI_SCRIPT_RANGE = re.compile(r"[\u0980-\u09ff]")
    TELUGU_SCRIPT_RANGE = re.compile(r"[\u0c00-\u0c7f]")

    # Phonetic transliterated keywords for romanized input
    ODIA_PHONETIC_MARKERS = {
        "mu", "mate", "mora", "mor", "tume", "apan", "apananka", "achhi", "achhanti",
        "nahi", "katha", "darichhi", "dhamaka", "sahajya", "marideba", "bhanguchhanti",
        "ghara", "lathi", "police", "thana", "gali", "atiyachara", "marpit"
    }

    HINDI_PHONETIC_MARKERS = {
        "main", "mujhe", "mera", "meri", "aap", "hum", "hai", "hain", "nahi",
        "darr", "lag", "raha", "marne", "dhamki", "madad", "chahiye", "police",
        "bachao", "pitai", "gaali", "shikayat", "ghar"
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

        total_indic = odia_chars + devanagari_chars + bengali_chars + telugu_chars
        if total_indic > 0:
            if odia_chars >= max(devanagari_chars, bengali_chars, telugu_chars):
                return SupportedLanguage.ODIA, 0.98
            elif devanagari_chars >= max(odia_chars, bengali_chars, telugu_chars):
                return SupportedLanguage.HINDI, 0.98
            elif bengali_chars >= max(odia_chars, devanagari_chars, telugu_chars):
                return SupportedLanguage.BENGALI, 0.98
            elif telugu_chars >= max(odia_chars, devanagari_chars, bengali_chars):
                return SupportedLanguage.TELUGU, 0.98

        # 2. Phonetic romanized lexical detection (Code-mixed / Romanized transcripts)
        words = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
        if not words:
            return self.default_language, 0.50

        odia_matches = len(words.intersection(self.ODIA_PHONETIC_MARKERS))
        hindi_matches = len(words.intersection(self.HINDI_PHONETIC_MARKERS))

        if odia_matches > hindi_matches and odia_matches > 0:
            conf = min(0.60 + (odia_matches * 0.10), 0.95)
            return SupportedLanguage.ODIA, conf
        elif hindi_matches > odia_matches and hindi_matches > 0:
            conf = min(0.60 + (hindi_matches * 0.10), 0.95)
            return SupportedLanguage.HINDI, conf

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

        # Only switch language if confidence is convincingly high
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
        if "or" in c or "odi" in c:
            return SupportedLanguage.ODIA
        if "hi" in c or "hin" in c:
            return SupportedLanguage.HINDI
        if "en" in c or "eng" in c:
            return SupportedLanguage.ENGLISH
        if "bn" in c or "ben" in c:
            return SupportedLanguage.BENGALI
        if "te" in c or "tel" in c:
            return SupportedLanguage.TELUGU
        if "sp" in c or "sambalpur" in c:
            return SupportedLanguage.SAMBALPURI
        if "sat" in c or "santali" in c:
            return SupportedLanguage.SANTALI
        return SupportedLanguage.ODIA
