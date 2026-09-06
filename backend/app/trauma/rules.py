import csv
import logging
from pathlib import Path
from typing import List, Tuple, Set
from ..domain.models import RiskLevel, SafetyFlags

logger = logging.getLogger(__name__)

# Dynamically load keywords from Indian Linguistic Risk Corpus (ILRC 500)
_ILRC_CRITICAL_EXTRA: Set[str] = set()
_ILRC_HIGH_EXTRA: Set[str] = set()

def _load_ilrc_corpus():
    paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "processed" / "indian_linguistic_risk_corpus.csv",
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "indian_linguistic_risk_corpus.csv",
        Path.cwd() / "data" / "processed" / "indian_linguistic_risk_corpus.csv",
        Path.cwd() / "data" / "indian_linguistic_risk_corpus.csv",
        Path("/app/data/processed/indian_linguistic_risk_corpus.csv"),
        Path("/app/data/indian_linguistic_risk_corpus.csv")
    ]
    for p in paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        sev = (row.get("severity") or "").upper()
                        # Keywords from English, Hindi, and Odia columns
                        for col in ("english_keywords", "hindi_keywords", "odia_keywords"):
                            raw_val = row.get(col, "")
                            for part in raw_val.split(","):
                                clean = part.strip().lower()
                                if clean and len(clean) >= 2:
                                    if sev == "CRITICAL":
                                        _ILRC_CRITICAL_EXTRA.add(clean)
                                    elif sev == "HIGH":
                                        _ILRC_HIGH_EXTRA.add(clean)
                logger.info(f"[SafetyRulesEngine] Loaded {len(_ILRC_CRITICAL_EXTRA)} critical and {len(_ILRC_HIGH_EXTRA)} high ILRC triggers from {p.name}")
                break
            except Exception as e:
                logger.warning(f"[SafetyRulesEngine] Error loading ILRC CSV: {e}")

_load_ilrc_corpus()


class SafetyRulesEngine:
    """
    Deterministic safety rules and override gates.
    The LLM has zero authority over these rules.
    """

    CRITICAL_TRIGGERS = list(set([
        # English & Romanized
        "suicide", "mariba", "end my life", "jeeban haridebi", "khatam kar dunga",
        "talwar", "banduk", "gun", "knife", "chaku", "bomb", "lathi",
        "ebe maruchhanti", "beating now", "darwaza tod rahe", "ghara bhanguchhanti",
        "raktapata", "bleeding", "unconscious", "behosh", "bachao", "kapata bhang",
        "rape", "gang rape", "murder", "hatya", "balatkar", "killed",
        # Native Odia Script
        "ଲାଠି", "ବନ୍ଧୁକ", "ଛୁରୀ", "ଖଣ୍ଡା", "ଭାଙ୍ଗୁଛନ୍ତି", "ଭାଙ୍ଗି", "ମାରୁଛନ୍ତି",
        "ଆତ୍ମହତ୍ୟା", "ଜୀବନ ହାରି", "ରକ୍ତ", "ବଚାଅ", "କପାଟ ଭାଙ୍ଗ", "ହତ୍ୟା", "ବଳାତ୍କାର",
        # Native Devanagari Script
        "लाठी", "बंदूक", "चाकू", "तलवार", "दरवाजा तोड़", "घर तोड़", "मार रहे हैं",
        "आत्महत्या", "खून", "बचाओ", "हत्या", "बलात्कार"
    ] + list(_ILRC_CRITICAL_EXTRA)))

    HIGH_TRIGGERS = list(set([
        # English & Romanized
        "dhamaka", "dhamki", "threat", "marideba", "kill you",
        "caste abuse", "atiyachara", "boycott", "pani nebaku mana", "samaja ru bahiskara",
        "kidnap", "police complaint mana", "land dispute attack", "bata banda",
        # Native Odia Script
        "ଧମକ", "ଧମକା", "ମାରିଦେବା", "ଅତ୍ୟାଚାର", "ଜାତିଆଣ", "ଅପହରଣ", "ବାସନ୍ଦ", "ପାଣି ମନା", "ସମାଜରୁ ବହିଷ୍କାର",
        # Native Devanagari Script
        "धमकी", "जान से मार", "मार दूंगा", "अत्याचार", "अपहरण", "सामाजिक बहिष्कार", "पानी बंद"
    ] + list(_ILRC_HIGH_EXTRA)))

    @classmethod
    def evaluate_overrides(
        cls, transcript_text: str, current_flags: SafetyFlags
    ) -> Tuple[RiskLevel, bool, List[str]]:
        """
        Evaluate if hardcoded safety triggers force an override to CRITICAL or HIGH.
        Returns: (overridden_level, is_override_applied, evidence_tags)
        """
        text_lower = transcript_text.lower()
        evidence: List[str] = []

        # 1. Check for immediate critical triggers
        for trigger in cls.CRITICAL_TRIGGERS:
            if trigger in text_lower:
                evidence.append(f"Immediate Critical Safety Trigger: '{trigger}'")
                current_flags.immediate_danger = True
                if trigger in ["suicide", "mariba", "end my life", "jeeban haridebi", "ଆତ୍ମହତ୍ୟା", "ଜୀବନ ହାରି", "आत्महत्या"]:
                    current_flags.self_harm_indicator = True
                    current_flags.suicidal_ideation = True
                if trigger in ["talwar", "banduk", "gun", "knife", "chaku", "ଲାଠି", "ବନ୍ଧୁକ", "ଛୁରୀ", "ଖଣ୍ଡା", "बंदूक", "चाकू", "तलवार"]:
                    current_flags.weapon_present = True
                if trigger in ["rape", "gang rape", "murder", "hatya", "balatkar", "killed", "ହତ୍ୟା", "ବଳାତ୍କାର", "हत्या", "बलात्कार"]:
                    current_flags.severe_trauma = True

                return RiskLevel.CRITICAL, True, evidence

        # 2. Check for high-level threats
        for trigger in cls.HIGH_TRIGGERS:
            if trigger in text_lower:
                evidence.append(f"High-Level Threat Trigger: '{trigger}'")
                if trigger in ["boycott", "pani nebaku mana", "samaja ru bahiskara", "ବାସନ୍ଦ", "ପାଣି ମନା", "ସମାଜରୁ ବହିଷ୍କାର", "सामाजिक बहिष्कार", "पानी बंद"]:
                    current_flags.social_boycott_isolation = True
                if trigger in ["dhamaka", "dhamki", "threat", "marideba", "kill you", "ଧମକ", "ଧମକା", "ମାରିଦେବା", "धमकी", "जान से मार", "मार दूंगा"]:
                    current_flags.intimidation_threat = True

                return RiskLevel.HIGH, True, evidence

        return RiskLevel.LOW, False, evidence
