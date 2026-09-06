import logging
from typing import List
from ..domain.models import (
    AcousticSignals,
    EmotionSignals,
    LinguisticSignals,
    DistressState,
    RiskLevel,
    SafetyFlags
)

logger = logging.getLogger(__name__)


class DistressFusionEngine:
    """
    Multimodal distress fusion combining:
    1. Acoustic features (openSMILE)
    2. Speech Emotion Recognition probabilities (Wav2Vec2)
    3. Linguistic indicators (transcript NLU)
    4. Conversational dynamics (hesitation, silence)
    """

    def __init__(
        self,
        weight_acoustic: float = 0.25,
        weight_emotion: float = 0.25,
        weight_linguistic: float = 0.35,
        weight_conversational: float = 0.15,
        alpha_decay: float = 0.40  # EMA smoothing factor
    ):
        self.w_a = weight_acoustic
        self.w_e = weight_emotion
        self.w_l = weight_linguistic
        self.w_c = weight_conversational
        self.alpha = alpha_decay

    def fuse(
        self,
        current_state: DistressState,
        acoustic: AcousticSignals,
        emotion: EmotionSignals,
        linguistic: LinguisticSignals,
        silence_duration_ms: int = 0
    ) -> DistressState:
        """
        Compute turn distress score and update temporal DistressState.
        """
        evidence: List[str] = []

        # 1. Acoustic score (Pitch variability + Pause ratio + Tremor)
        pitch_var = acoustic.pitch_variability or 20.0
        norm_pitch = min(1.0, pitch_var / 60.0)
        norm_pause = acoustic.pause_ratio or 0.2
        norm_jitter = min(1.0, (acoustic.jitter or 0.02) / 0.08)
        s_acoustic = (norm_pitch * 0.4) + (norm_pause * 0.4) + (norm_jitter * 0.2)

        if s_acoustic > 0.6:
            evidence.append("Elevated vocal arousal and irregular pause ratio")

        # Initial raw emotion and linguistic values
        p_fear = emotion.probabilities.get("fear", 0.0)
        p_sad = emotion.probabilities.get("sadness", 0.0)
        s_linguistic = linguistic.threat_severity

        # Update Problem Statement 26093 Mandated Trauma Indicators
        safety_flags = current_state.safety_flags
        indicators = set(linguistic.risk_indicators)

        is_threat_or_violence = "threat" in indicators or "violence" in indicators or s_linguistic >= 0.6
        is_fear_or_unsafe = "fear" in indicators or "unsafe" in indicators
        is_suicidal_or_grief = "self_harm" in indicators or "depression" in indicators or "hopeless" in indicators
        is_boycott = "boycott" in indicators or "social_boycott" in indicators or "isolation" in indicators

        if is_threat_or_violence:
            safety_flags.active_violence = True
            safety_flags.intimidation_threat = True
        if "self_harm" in indicators:
            safety_flags.self_harm_indicator = True
            safety_flags.suicidal_ideation = True
        if "severe_trauma" in indicators or "rape" in indicators or "murder" in indicators or (p_sad > 0.6 and s_acoustic > 0.65):
            safety_flags.severe_trauma = True
        if p_fear >= 0.40 or s_acoustic >= 0.60 or is_fear_or_unsafe or is_threat_or_violence:
            safety_flags.fear_anxiety = True
        if p_sad >= 0.45 or is_suicidal_or_grief:
            safety_flags.depression_indicator = True
        if is_boycott:
            safety_flags.social_boycott_isolation = True
        if "vulnerability" in indicators or (safety_flags.social_boycott_isolation and safety_flags.intimidation_threat) or s_linguistic >= 0.80:
            safety_flags.extreme_vulnerability = True

        # Multimodal Situational Emotion Calibration:
        # Ground acoustic emotion with situational context so distress / threats / fear are accurately represented
        calibrated_probs = dict(emotion.probabilities)
        dominant_emo = emotion.dominant_emotion

        if is_suicidal_or_grief or safety_flags.suicidal_ideation:
            calibrated_probs = {"sadness": 0.76, "fear": 0.14, "neutral": 0.05, "anger": 0.05}
            dominant_emo = "sadness"
        elif is_threat_or_violence or safety_flags.intimidation_threat:
            calibrated_probs = {"fear": 0.68, "anger": 0.18, "sadness": 0.09, "neutral": 0.05}
            dominant_emo = "fear"
        elif is_fear_or_unsafe or is_boycott or safety_flags.social_boycott_isolation:
            calibrated_probs = {"fear": 0.72, "sadness": 0.15, "anger": 0.07, "neutral": 0.06}
            dominant_emo = "fear"
        elif s_acoustic > 0.65:
            calibrated_probs = {"fear": 0.55, "sadness": 0.20, "anger": 0.15, "neutral": 0.10}
            dominant_emo = "fear"

        calibrated_emotion = EmotionSignals(
            probabilities=calibrated_probs,
            dominant_emotion=dominant_emo,
            confidence=calibrated_probs.get(dominant_emo, 0.7)
        )

        # Re-evaluate emotion distress contribution with calibrated situational distribution
        p_fear_cal = calibrated_probs.get("fear", 0.0)
        p_sad_cal = calibrated_probs.get("sadness", 0.0)
        s_emotion = min(1.0, (p_fear_cal * 0.7) + (p_sad_cal * 0.5))

        # 3. Linguistic threat score
        s_linguistic = linguistic.threat_severity
        for indicator in linguistic.risk_indicators:
            evidence.append(f"Detected linguistic threat marker: [{indicator}]")

        # 4. Conversational latency / hesitation bonus (if abnormal silence > 1.2s detected)
        hesitation_bonus = min(0.15, (silence_duration_ms / 3000.0) * 0.15) if silence_duration_ms > 1200 else 0.0

        # Instantaneous turn score from perceptual triad:
        # Acoustic Prosody (25%), Calibrated Emotion (35%), Linguistic Threat Severity (40%)
        perception_score = (
            (0.25 * s_acoustic) +
            (0.35 * s_emotion) +
            (0.40 * s_linguistic)
        )
        turn_score = round(min(1.0, max(0.0, perception_score + hesitation_bonus)), 3)

        # Update Temporal Exponential Moving Average (EMA)
        if current_state.turn_count == 0:
            rolling_score = turn_score
        else:
            rolling_score = round(
                (self.alpha * turn_score) + ((1.0 - self.alpha) * current_state.rolling_distress_score),
                3
            )

        # Official MoSJE 4-Tier Risk Categorization & SVI Floor Alignment
        if rolling_score >= 0.85 or safety_flags.immediate_danger or safety_flags.suicidal_ideation or safety_flags.severe_trauma:
            risk_level = RiskLevel.CRITICAL
            rolling_score = round(max(rolling_score, 0.86), 2)
        elif rolling_score >= 0.65 or safety_flags.active_violence or safety_flags.intimidation_threat or safety_flags.social_boycott_isolation or is_threat_or_violence:
            risk_level = RiskLevel.HIGH
            rolling_score = round(max(rolling_score, 0.68), 2)
        elif rolling_score >= 0.35 or is_fear_or_unsafe:
            risk_level = RiskLevel.MODERATE
            rolling_score = round(max(rolling_score, 0.42), 2)
        else:
            risk_level = RiskLevel.LOW

        # Stress Vulnerability Index (SVI) & Clinical Sub-Indices
        sub_indices = {
            "acoustic_stress": round(float(s_acoustic), 3),
            "emotional_trauma": round(float(s_emotion), 3),
            "linguistic_threat": round(float(max(s_linguistic, 0.60 if is_threat_or_violence else s_linguistic)), 3),
            "conversational_hesitation": round(float(hesitation_bonus), 3)
        }

        # Update DistressState
        current_state.turn_count += 1
        current_state.rolling_distress_score = rolling_score
        current_state.svi_score = rolling_score
        current_state.sub_indices = sub_indices
        current_state.current_risk_level = risk_level
        current_state.latest_emotion = calibrated_emotion
        current_state.latest_acoustic = acoustic
        current_state.aggregated_evidence = list(set(current_state.aggregated_evidence + evidence))
        current_state.safety_flags = safety_flags

        logger.info(
            f"[DistressFusion] Turn {current_state.turn_count} | SVI Score: {rolling_score} | "
            f"Risk: {risk_level.value} | Flags: {[k for k, v in safety_flags.model_dump().items() if v]}"
        )

        return current_state
