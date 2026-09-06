import os
import sys
import asyncio
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.config import settings
from app.domain.models import DistressState, RiskAssessment
from app.providers.sarvam_provider import SarvamProvider
from app.providers.gemini_provider import GeminiProvider
from app.acoustic.extractor import StandardAcousticExtractor
from app.emotion.classifier import Wav2VecEmotionClassifier
from app.distress.fusion_engine import DistressFusionEngine
from app.trauma.controller import TraumaController
from app.safety.validator import SafetyValidator


async def evaluate_audio(file_path: str):
    path = Path(file_path)
    if not path.exists():
        print(f"\n[ERROR] File not found: {file_path}")
        return

    print("=" * 70)
    print(f"  TRAUMA AI — OFFLINE AUDIO DIAGNOSTIC HARNESS (SIH PS 26093)")
    print(f"  Target File: {path.name}")
    print("=" * 70)

    audio_bytes = path.read_bytes()

    sarvam = SarvamProvider(api_key=settings.SARVAM_API_KEY, base_url=settings.SARVAM_BASE_URL)
    gemini = GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
    acoustic_extractor = StandardAcousticExtractor()
    emotion_classifier = Wav2VecEmotionClassifier()
    fusion_engine = DistressFusionEngine()
    trauma_controller = TraumaController()

    print("\n[1/5] Transcribing Speech (Sarvam Saaras)...")
    transcript, lang, conf = await sarvam.transcribe(audio_bytes, 16000)
    print(f"      Language: {lang.upper()} (Confidence: {int(conf * 100)}%)")
    print(f"      Transcript: \"{transcript}\"")

    print("\n[2/5] Extracting Acoustic Prosody (openSMILE eGeMAPS)...")
    acoustic = await acoustic_extractor.extract(audio_bytes, 16000)
    print(f"      Pitch Mean: {acoustic.mean_pitch_f0} Hz | Variability: {acoustic.pitch_variability}")
    print(f"      Pause Ratio: {acoustic.pause_ratio} | Speech Rate: {acoustic.speech_rate} syl/sec")
    print(f"      Vocal Tremor (Jitter): {acoustic.jitter}")

    print("\n[3/5] Inferring Emotion Probabilities (Wav2Vec2 SER)...")
    emotion = await emotion_classifier.predict_emotion(audio_bytes, 16000)
    for emo, prob in emotion.probabilities.items():
        bar = "#" * int(prob * 20) + "-" * (20 - int(prob * 20))
        print(f"      {emo.capitalize():<8}: [{bar}] {int(prob * 100)}%")

    print("\n[4/5] Extracting Linguistic Threat & Fusing Distress...")
    linguistic = await gemini.extract_linguistic_signals(transcript)
    state = DistressState(call_id="cli_eval")
    fused_state = fusion_engine.fuse(state, acoustic, emotion, linguistic)

    assessment: RiskAssessment = trauma_controller.assess_and_control(
        call_id="cli_eval",
        distress_state=fused_state,
        latest_transcript=transcript
    )

    print("-" * 70)
    badge = f"[{assessment.risk_level.value}]"
    print(f"  TRIAGE ASSESSMENT: {badge}")
    print(f"  Fused Distress Score: {assessment.risk_score} (Confidence: {int(assessment.confidence * 100)}%)")
    print(f"  Human Escalation: {'REQUIRED [!]' if assessment.requires_human_escalation else 'Not Required'}")
    print(f"  Protocol Action: {assessment.recommended_action}")
    if assessment.evidence:
        print("  Detected Evidence:")
        for ev in assessment.evidence:
            print(f"    * {ev}")
    print("-" * 70)

    print("\n[5/5] Generating Calibrated AI Response...")
    ai_raw = await gemini.generate_response(
        conversation_history=[{"role": "user", "content": transcript}],
        system_instructions=f"Helpline 14566. Risk: {assessment.risk_level.value}. Action: {assessment.recommended_action}. Lang: {lang}"
    )
    safe_response, is_valid = SafetyValidator.validate(ai_raw, lang)
    print(f"      AI Response: \"{safe_response}\"")
    print(f"      Safety Validation: {'PASSED [OK]' if is_valid else 'FALLBACK ENFORCED [!]'}")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python scripts/test_audio.py <path_to_audio.wav>")
        print("Example: python scripts/test_audio.py data/test_audio/odia/threat_01.wav\n")
        sys.exit(1)

    asyncio.run(evaluate_audio(sys.argv[1]))
