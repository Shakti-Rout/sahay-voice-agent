# SIH 2026 PS 26093: Quick Demo & Testing Guide
## National Helpline Against Atrocities (14566) Voice Triage Module

This guide details how to launch, operate, and demonstrate the prototype in 3 simple steps.

---

### Step 1: Start the Local Voice Server
Open a terminal in the project root:
```powershell
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Verify the server is healthy:
- Open browser: `http://localhost:8000/api/v1/health`
- Expect status: `"status": "healthy"`, `"production_helpline": "14566"`

---

### Step 2: Open the Two Visual Interfaces

1. **Operator Triage Dashboard** (Dispatcher Screen):
   - Open: **`http://localhost:8000/dashboard`**
   - Features: Real-time 8kHz audio waveform, live bilingual transcript stream, emotion probability bars (Fear, Sadness, Anger, Neutral), openSMILE acoustic meters (F0 Pitch, Tremor, Pause Ratio), SBAR handoff dossier, and emergency dispatch action buttons (`🚨 Bridge to 112 CAD Emergency`).

2. **Interactive Microphone Console** (Caller Simulation):
   - Open: **`http://localhost:8000/test`**
   - Click **`🎙️ START RECORDING`**, speak in Odia, Hindi, or English, and click **`⏹️ STOP & ANALYZE`**.
   - Watch the audio waveform stream live, transcribe via Sarvam Saaras v3, compute distress via Wav2Vec2 + openSMILE, evaluate safety via deterministic rules, and listen to the synthesized soothing voice response via Sarvam Bulbul v3.

---

### Step 3: Run the Automated 5-Scenario Benchmark
To evaluate the complete pipeline on all 5 official SIH benchmark scenarios offline:
```powershell
python scripts/run_all_scenarios.py
```
This runs each pre-synthesized audio scenario through the full triad and outputs a complete terminal scorecard table displaying expected vs. computed risk levels, acoustic features, and latency metrics.

---

### Step 4: Run the Complete Automated Test Suite
To verify all 28 unit and integration tests:
```powershell
$env:PYTHONPATH="backend"
pytest backend/tests -v
```
All 28 tests will execute in under 2 seconds with a 100% pass rate.
