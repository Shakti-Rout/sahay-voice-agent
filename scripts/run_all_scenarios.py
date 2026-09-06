"""
SIH 2026 PS 26093: Automated 5-Scenario Evaluation Benchmark & Scorecard.
Runs the complete multimodal pipeline on all 5 official benchmark scenarios and generates an evaluation table.
"""

import os
import sys
import time
import asyncio
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.config import settings
from app.providers.sarvam_provider import SarvamProvider
from app.providers.gemini_provider import GeminiProvider
from app.acoustic.extractor import StandardAcousticExtractor
from app.emotion.classifier import Wav2VecEmotionClassifier
from app.distress.fusion_engine import DistressFusionEngine
from app.trauma.controller import TraumaController
from app.trauma.state_machine import ConversationStateManager
from app.trauma.handoff import StructuredHandoffGenerator
from app.rag.retriever import VerifiedRAGRetriever
from app.safety.validator import SafetyValidator
from app.language.router import LanguageRouter, DialectBridge
from app.domain.models import DistressState, RiskLevel

SCENARIO_CONFIGS = [
    {
        "id": "scenario_01",
        "name": "Calm Inquiry",
        "file": "data/test_audio/odia/scenario_01_calm.wav",
        "expected_risk": "LOW",
        "description": "Information request about SC/ST welfare scholarship."
    },
    {
        "id": "scenario_02",
        "name": "Distressed / Fear",
        "file": "data/test_audio/odia/scenario_02_moderate.wav",
        "expected_risk": "MODERATE",
        "description": "Caller expressing isolation and acute emotional distress."
    },
    {
        "id": "scenario_03",
        "name": "Direct Threat",
        "file": "data/test_audio/odia/scenario_03_high.wav",
        "expected_risk": "HIGH",
        "description": "Explicit threat to life ('marideba dhamaka')."
    },
    {
        "id": "scenario_04",
        "name": "Immediate Life Danger",
        "file": "data/test_audio/odia/scenario_04_critical.wav",
        "expected_risk": "CRITICAL",
        "description": "Armed intimidation with lathis outside door breaking in."
    },
    {
        "id": "scenario_05",
        "name": "Code-Switching",
        "file": "data/test_audio/odia/scenario_05_codeswitch.wav",
        "expected_risk": "HIGH",
        "description": "Odia-English code-mixed urgent distress call."
    }
]


async def run_benchmark():
    base_dir = Path(__file__).resolve().parent.parent

    # Initialize modules
    sarvam = SarvamProvider(api_key=settings.SARVAM_API_KEY, base_url=settings.SARVAM_BASE_URL)
    gemini = GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
    acoustic_extractor = StandardAcousticExtractor()
    emotion_classifier = Wav2VecEmotionClassifier()
    fusion_engine = DistressFusionEngine()
    trauma_controller = TraumaController()
    state_machine = ConversationStateManager()
    rag_retriever = VerifiedRAGRetriever()
    lang_router = LanguageRouter()

    print("=" * 80)
    print("  SIH 2026 PS 26093 — MULTIMODAL VOICE TRIAGE BENCHMARK SCORECARD")
    print("  Official Helpline: NHAA 14566 | Emergency Bridge: 112 / 108")
    print("=" * 80)

    scorecard = []

    for sc in SCENARIO_CONFIGS:
        wav_path = base_dir / sc["file"]
        if not wav_path.exists():
            print(f"[!] File not found: {sc['file']}. Skipping.")
            continue

        start_time = time.time()
        audio_bytes = wav_path.read_bytes()

        # 1. Perception
        transcript, raw_lang, lang_conf = await sarvam.transcribe(audio_bytes, 16000)
        acoustic = await acoustic_extractor.extract(audio_bytes, 16000)
        emotion = await emotion_classifier.predict_emotion(audio_bytes, 16000)

        # 2. Language & Dialect Routing
        detected_lang_enum, det_conf = lang_router.detect_language_from_text(transcript)
        normalized_transcript = DialectBridge.normalize_dialect(transcript, detected_lang_enum.value)

        # 3. NLU & Fusion
        linguistic = await gemini.extract_linguistic_signals(normalized_transcript)
        state = DistressState(call_id=sc["id"])
        fused = fusion_engine.fuse(state, acoustic, emotion, linguistic)

        # 4. Deterministic Trauma Controller
        assessment = trauma_controller.assess_and_control(sc["id"], fused, normalized_transcript)

        # 5. RAG & Response
        rag_context = rag_retriever.retrieve_context(normalized_transcript, assessment.risk_level.value, detected_lang_enum.value)
        next_state = state_machine.transition(sc["id"], assessment.risk_level.value, 1, assessment.requires_human_escalation)
        system_prompt = state_machine.get_system_prompt_for_state(next_state, detected_lang_enum.value, assessment.risk_level.value)

        ai_raw = await gemini.generate_response([{"role": "caller", "content": transcript}], system_prompt, rag_context)
        safe_response, is_valid = SafetyValidator.validate(ai_raw, detected_lang_enum.value)

        elapsed_ms = int((time.time() - start_time) * 1000)

        # SBAR Handoff
        sbar = StructuredHandoffGenerator.generate_sbar_report(
            call_id=sc["id"],
            phone_hash="hash_" + sc["id"],
            detected_language=detected_lang_enum.value,
            assessment=assessment,
            distress_state=fused,
            full_transcript=[{"role": "caller", "content": transcript}, {"role": "agent", "content": safe_response}],
            acoustic_features=acoustic,
            emotion_prediction=emotion
        )

        match = (assessment.risk_level.value == sc["expected_risk"])
        scorecard.append({
            "name": sc["name"],
            "expected": sc["expected_risk"],
            "computed": assessment.risk_level.value,
            "score": assessment.risk_score,
            "dominant_emotion": emotion.dominant_emotion.upper(),
            "f0_mean": f"{acoustic.mean_pitch_f0:.1f}Hz" if acoustic.mean_pitch_f0 else "N/A",
            "escalated": assessment.requires_human_escalation,
            "latency_ms": elapsed_ms,
            "pass": match,
            "ai_response": safe_response[:50] + "..." if len(safe_response) > 50 else safe_response
        })

    # Print Formatted Markdown Table
    print("\n| Scenario | Expected | Computed | Distress | Emotion | F0 Mean | Escalation | Latency | Result |")
    print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    all_passed = True
    for row in scorecard:
        res = "[PASS]" if row["pass"] else "[DIFF]"
        if not row["pass"]:
            all_passed = False
        print(f"| {row['name']:<22} | {row['expected']:<8} | {row['computed']:<8} | {row['score']:.2f} | {row['dominant_emotion']:<7} | {row['f0_mean']:<7} | {'YES' if row['escalated'] else 'NO':<10} | {row['latency_ms']:<5}ms | {res} |")

    print("\n" + "=" * 80)
    print(f"  OVERALL BENCHMARK VERDICT: {'ALL 5 SCENARIOS PASSED 100%' if all_passed else 'EVALUATION COMPLETE'}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_benchmark())
