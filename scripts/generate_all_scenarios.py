"""
Generate Complete SIH 2026 Benchmark Scenario Audio Files.
Uses Sarvam Bulbul v3 TTS to synthesize authentic spoken Indian speech for all 5 jury scenarios.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.providers.sarvam_provider import SarvamProvider
from app.config import settings

SCENARIOS = [
    {
        "id": "scenario_01_calm",
        "name": "Scenario 1: Calm Inquiry (LOW RISK)",
        "path": "data/test_audio/odia/scenario_01_calm.wav",
        "text": "Namaskar, mu SC ST welfare scholarship scheme bisayare kichhi information chahunchhi.",
        "lang": "od-IN",
        "speaker": "ritu"
    },
    {
        "id": "scenario_02_moderate",
        "name": "Scenario 2: Distressed / Fear (MODERATE RISK)",
        "path": "data/test_audio/odia/scenario_02_moderate.wav",
        "text": "Mu bahut darichhi, amaku bahut asanti laguchhi, mo katha kehi sununahanti.",
        "lang": "od-IN",
        "speaker": "ritu"
    },
    {
        "id": "scenario_03_high_threat",
        "name": "Scenario 3: Direct Threat (HIGH RISK)",
        "path": "data/test_audio/odia/scenario_03_high.wav",
        "text": "Se mate marideba boli dhamaka deichhi. Mate bahut bhaya laguchhi.",
        "lang": "od-IN",
        "speaker": "ritu"
    },
    {
        "id": "scenario_04_critical_danger",
        "name": "Scenario 4: Immediate Life Danger / Weapon (CRITICAL RISK)",
        "path": "data/test_audio/odia/scenario_04_critical.wav",
        "text": "Se ebe mo ghara bahare lathi dhari thia hoichhanti, kapata bhanguchhanti, bachao!",
        "lang": "od-IN",
        "speaker": "ritu"
    },
    {
        "id": "scenario_05_code_switch",
        "name": "Scenario 5: Code-Switching (Odia + English)",
        "path": "data/test_audio/odia/scenario_05_codeswitch.wav",
        "text": "Se mate continuously threaten karuchhi, mu bahut scared achhi please urgent help karantu.",
        "lang": "od-IN",
        "speaker": "ritu"
    }
]


async def generate_all():
    base_dir = Path(__file__).resolve().parent.parent
    sarvam = SarvamProvider(api_key=settings.SARVAM_API_KEY, base_url=settings.SARVAM_BASE_URL)

    print("=" * 70)
    print("  SYNTHESIZING SIH 2026 JURY DEMONSTRATION SCENARIOS (Sarvam Bulbul v3)")
    print("=" * 70)

    for sc in SCENARIOS:
        out_file = base_dir / sc["path"]
        out_file.parent.mkdir(parents=True, exist_ok=True)
        print(f"\n[*] Synthesizing {sc['name']}...")
        print(f"    Text: \"{sc['text']}\"")

        audio_bytes = await sarvam.synthesize(
            text=sc["text"],
            language_code=sc["lang"],
            speaker_gender="female"
        )

        if audio_bytes:
            out_file.write_bytes(audio_bytes)
            print(f"    [OK] Saved {len(audio_bytes)} bytes -> {sc['path']}")
        else:
            print("    [!] Failed to synthesize audio.")

    print("\n" + "=" * 70)
    print("  ALL 5 SIH BENCHMARK AUDIO SCENARIOS READY")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(generate_all())
