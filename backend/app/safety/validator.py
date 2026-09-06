import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class SafetyValidator:
    """
    Post-generation guardrail ensuring LLM responses are safe, factual, and legally defensible.
    Blocks hallucinated numbers, clinical diagnoses, false promises, and victim blaming.
    """

    # Approved official helplines (never blocked or sanitized)
    APPROVED_NUMBERS = {"14566", "112", "108", "14416", "1098", "1930", "181", "100", "101", "102"}

    # Whitelisted statutory years and legal act dates
    WHITELISTED_YEARS = {str(y) for y in range(1947, 2035)}

    # Map Indic native digits (Odia and Devanagari) to ASCII 0-9
    INDIC_DIGIT_MAP = str.maketrans("୦୧୨୩୪୫୬୭୮୯०१२३४५६७८९", "01234567890123456789")

    PROHIBITED_DIAGNOSES = [
        "you have ptsd", "diagnose you with", "clinical depression",
        "psychiatric illness", "you have trauma disorder", "you are suffering from mental illness"
    ]

    VICTIM_BLAMING = [
        "your fault", "why did you go there", "why didn't you avoid",
        "you should have obeyed", "you caused this"
    ]

    FALSE_PROMISES = [
        "i guarantee the police will arrest", "i promise you will get compensation",
        "i promise everything will be fixed today"
    ]

    SAFE_FALLBACKS = {
        "or": "Namaskar. Apan ebe surakshita achhanti ki? Apananka surakhya amara prathama kartavya. Daya kari kuhan tu ame kemiti sahajya kariparibu.",
        "hi": "Namaskar. Kya aap abhi surakshit hain? Aapki suraksha hamari pehli prathmikta hai. Kripya batayein hum aapki kya sahayata kar sakte hain.",
        "en": "Hello. Are you currently in a safe place? Your immediate safety is our priority. Please let us know how we can support you."
    }

    @classmethod
    def validate(cls, text: str, language_code: str = "or") -> Tuple[str, bool]:
        """
        Validate generated text.
        Returns: (safe_text, is_clean)
        """
        lower = text.lower()
        validated_text = text

        # 1. Check for prohibited medical/clinical diagnosis
        for diag in cls.PROHIBITED_DIAGNOSES:
            if diag in lower:
                logger.warning(f"[SafetyValidator] Inappropriate clinical diagnosis blocked: {diag}")
                fallback = cls.SAFE_FALLBACKS.get(language_code, cls.SAFE_FALLBACKS["en"])
                return fallback, False

        # 2. Check for victim blaming phrases
        for blame in cls.VICTIM_BLAMING:
            if blame in lower:
                logger.warning(f"[SafetyValidator] Victim blaming language blocked: {blame}")
                fallback = cls.SAFE_FALLBACKS.get(language_code, cls.SAFE_FALLBACKS["en"])
                return fallback, False

        # 3. Check for false guarantees/promises
        for promise in cls.FALSE_PROMISES:
            if promise in lower:
                logger.warning(f"[SafetyValidator] False legal/police promise blocked: {promise}")
                fallback = cls.SAFE_FALLBACKS.get(language_code, cls.SAFE_FALLBACKS["en"])
                return fallback, False

        has_sanitized_number = False
        potential_phones = re.findall(r'(?:\+91[\-\s]?)?[6-9]\d{9}\b|\b0\d{2,4}[-\s]?\d{6,8}\b|\b\d{3,6}\b|[୦-୯]{3,6}|[०-९]{3,6}', validated_text)
        for token in potential_phones:
            normalized_token = token.translate(cls.INDIC_DIGIT_MAP)
            clean_digits = re.sub(r'\D', '', normalized_token)
            # Check if this token is an approved helpline
            if clean_digits in cls.APPROVED_NUMBERS:
                continue
            # Check if this is a statutory act year (e.g. 1989, 1995, 2015)
            if clean_digits in cls.WHITELISTED_YEARS:
                continue
            # Check if small number (< 3 digits) or valid legal section reference
            if len(clean_digits) < 3 or len(clean_digits) > 12:
                continue

            # If it's a 10-digit mobile or unknown 3-6 digit shortcode not in approved helplines:
            logger.warning(f"[SafetyValidator] Unauthorized number sanitized in-place: {token} -> 14566")
            validated_text = re.sub(r'\b' + re.escape(token) + r'\b', '14566', validated_text)
            has_sanitized_number = True

        if has_sanitized_number:
            return validated_text, False

        return validated_text, True
