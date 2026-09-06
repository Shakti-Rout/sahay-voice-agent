# Multilingual AI Voice Distress & Trauma Triage Agent
## Smart India Hackathon 2026 — Problem Statement 26093

> **SIH PS 26093**: *AI-Based Real-Time Stress and Trauma Assessment Module for Victims/Complainants Accessing NHAA (14566) and Integrated Portal*  
> **Target Helpline**: National Helpline Against Atrocities (14566) — Ministry of Social Justice and Empowerment / SC & ST Protection Framework.

---

## 🎯 Key Capabilities

* 📞 **Real-Time Voice First**: Connects via Exotel telephony (PSTN) and web microphone (`/test`).
* 🇮🇳 **Multilingual & Code-Mixed Speech**: Native recognition and synthesis for Odia, Hindi, English, and tribal/regional dialects via Sarvam AI & Government BHASHINI.
* 🎙️ **Acoustic Distress Profiling**: Real-time prosody analysis (openSMILE eGeMAPS: Pitch F0, speech rate, tremors, pause ratio).
* 🧠 **Speech Emotion Recognition**: Probabilistic inference (fear, sadness, anger, neutral) using fine-tuned Wav2Vec2.
* 🛡️ **Deterministic Trauma Controller**: Hardcoded, unbypassable safety override engine for triage priority (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`).
* ⚡ **Ultra-Low Latency**: End-to-end turn latency under 1,200ms with barge-in interruption handling.
* 🔒 **Privacy by Design**: In-memory ephemeral audio buffering, zero raw audio disk persistence, salted phone hashing, and DPDP Act 2023 compliance.
* 📊 **Operator Triage Dashboard**: Live call telemetry, acoustic graph, segmented transcript, and structured handoff report for dispatchers.

---

## 🏗️ Architecture Triad

```
1. WHAT THEY SAID (Language / NLU)
   Sarvam Saaras STT + Gemini 2.0 Flash + Bhashini Language Router

2. HOW THEY SAID IT (Acoustic & Emotion Intelligence)
   openSMILE (eGeMAPS prosodic features) + Wav2Vec2-XLSR (SER probabilities)

3. WHAT NEEDS TO HAPPEN (Safety Decision Engine)
   Deterministic Trauma Controller + SafetyValidator + Verified RAG (14566/PoA Act)
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
* Python 3.10 or 3.11
* Node.js 18+ (for operator dashboard)
* Git

### 2. Clone & Setup Backend
```bash
git clone https://github.com/your-team/trauma-voice-agent.git
cd trauma-voice-agent/backend

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and populate your API credentials:
```bash
cp ../.env.example .env
```

### 4. Run Local Voice Gateway
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Open Dev Test Console
Open your browser and navigate to:
```
http://localhost:8000/test
```
Click **Start Recording**, speak in Odia, Hindi, or English, and test the entire multimodal triage loop through your laptop microphone!

---

## 🌐 Production Deployment (Railway)

The production voice gateway is deployed and active on **Railway**:
* **Base URL**: `https://sahay.up.railway.app`
* **Health Check**: `https://sahay.up.railway.app/api/v1/health`
* **API Documentation**: `https://sahay.up.railway.app/docs`
* **Operator Triage Dashboard**: `https://sahay.up.railway.app/dashboard`
* **Web Microphone Test Console**: `https://sahay.up.railway.app/test-console`

### Exotel Telephony Configuration (App ID: `1334274`)
1. **Passthru Applet**:
   * **URL**: `https://sahay.up.railway.app/api/v1/calls/webhook/exotel`
   * **Method**: `GET`
2. **Voicebot Applet**:
   * **WebSocket URL**: `wss://sahay.up.railway.app/ws/exotel/live_call`
   * **Format**: `PCM 8kHz 16-bit` or `mu-law 8kHz`

---

## 📜 Scientific & Ethical Notice
This system is an **AI-assisted decision-support and triage tool**, NOT a clinical diagnostic system. It does not diagnose PTSD, clinical depression, or psychological trauma. High-risk calls are escalated deterministically to authorized human operators and emergency services.
