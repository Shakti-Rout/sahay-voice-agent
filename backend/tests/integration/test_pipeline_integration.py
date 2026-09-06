import pytest
import asyncio
import numpy as np
from app.audio.resampler import AudioResampler
from app.audio.vad import VoiceActivityDetector
from app.acoustic.extractor import StandardAcousticExtractor
from app.emotion.classifier import Wav2VecEmotionClassifier
from app.distress.fusion_engine import DistressFusionEngine
from app.trauma.controller import TraumaController
from app.trauma.state_machine import ConversationStateManager, ConversationState
from app.trauma.handoff import StructuredHandoffGenerator
from app.rag.retriever import VerifiedRAGRetriever
from app.safety.validator import SafetyValidator
from app.language.router import LanguageRouter, SupportedLanguage
from app.domain.models import DistressState, LinguisticSignals, RiskLevel


def generate_synthetic_pcm(duration_sec: float = 1.0, freq: float = 220.0, sample_rate: int = 16000) -> bytes:
    """Generates synthetic 16kHz 16-bit linear PCM audio."""
    num_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    wave_data = 0.5 * np.sin(2 * np.pi * freq * t)
    pcm = (wave_data * 32767).astype(np.int16).tobytes()
    return pcm


def test_full_triage_pipeline_integration():
    async def run_pipeline():
        # 1. Setup all components
        call_id = "integration_call_001"
        vad = VoiceActivityDetector()
        resampler = AudioResampler()
        acoustic_ext = StandardAcousticExtractor()
        emotion_cls = Wav2VecEmotionClassifier()
        fusion_eng = DistressFusionEngine()
        controller = TraumaController()
        state_machine = ConversationStateManager()
        rag = VerifiedRAGRetriever()
        lang_router = LanguageRouter()

        # 2. Ingest audio chunk (simulate caller speaking)
        pcm_audio = generate_synthetic_pcm(duration_sec=1.2, freq=280.0)
        is_speech = vad.process_frame(pcm_audio[:640])  # 20ms frame
        assert is_speech in [True, False]

        # 3. Acoustic prosody & emotion extraction
        acoustic = await acoustic_ext.extract(pcm_audio, 16000)
        assert acoustic.mean_pitch_f0 is not None

        emotion = await emotion_cls.predict_emotion(pcm_audio, 16000)
        assert "fear" in emotion.probabilities

        # 4. Transcript & Language Routing
        spoken_text = "Mu bahut darichhi se mate marideba boli dhamaka deichhi"
        lang, conf = lang_router.detect_language_from_text(spoken_text)
        assert lang == SupportedLanguage.ODIA

        # 5. Linguistic threat extraction
        linguistic = LinguisticSignals(
            detected_keywords=["threat", "fear"],
            risk_indicators=["threat", "fear"],
            threat_severity=0.85
        )

        # 6. Distress Fusion
        initial_state = DistressState(call_id=call_id)
        fused_state = fusion_eng.fuse(initial_state, acoustic, emotion, linguistic)
        assert fused_state.rolling_distress_score >= 0.40

        # 7. Deterministic Trauma Controller
        assessment = controller.assess_and_control(call_id, fused_state, spoken_text)
        assert assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert assessment.requires_human_escalation is True

        # 8. Conversational State Transition
        next_state = state_machine.transition(call_id, assessment.risk_level.value, turn_count=1, requires_escalation=True)
        assert next_state == ConversationState.PROBLEM_ASSESSMENT

        # Follow-up turns probe scenario, and later turns escalate
        escalated_state = state_machine.transition(call_id, assessment.risk_level.value, turn_count=4, requires_escalation=True)
        assert escalated_state == ConversationState.ESCALATION_HANDOFF

        # 9. Verified RAG Retrieval
        verified_context = rag.retrieve_context(spoken_text, assessment.risk_level.value, lang.value)
        assert verified_context != ""
        assert ("14566" in verified_context or "112" in verified_context or "POA" in verified_context)

        # 10. SBAR Structured Handoff
        transcript = [
            {"role": "caller", "content": spoken_text},
            {"role": "agent", "content": "Apan surakshita achhanti ki?"}
        ]
        sbar = StructuredHandoffGenerator.generate_sbar_report(
            call_id=call_id,
            phone_hash="phone_hash_xyz",
            detected_language=lang.value,
            assessment=assessment,
            distress_state=fused_state,
            full_transcript=transcript,
            acoustic_features=acoustic,
            emotion_prediction=emotion
        )
        assert sbar["triage"]["risk_level"] in ["HIGH", "CRITICAL"]
        assert sbar["triage"]["requires_human_escalation"] is True

        # 11. Safety Validation
        safe_text, is_valid = SafetyValidator.validate(
            "Apan nishchinta rahantu, 14566 amara helpline apananka sahajya pain achhi.", lang.value
        )
        assert is_valid is True
        assert "14566" in safe_text

    asyncio.run(run_pipeline())
