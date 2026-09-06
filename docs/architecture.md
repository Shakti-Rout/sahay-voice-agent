# System Architecture & Technical Specifications
## SIH 2026 PS 26093: Real-Time Multimodal Voice Triage for NHAA (14566)

### 1. Architectural Philosophy
The National Helpline Against Atrocities (NHAA - 14566) handles sensitive situations including caste-based atrocities, acute domestic and physical intimidation, and trauma distress. In such high-stakes environments, relying purely on conversational LLM chat models is unsafe and clinically irresponsible.

Our architecture enforces a **Strict Decoupled Triad**:
1. **WHAT is spoken (Perception & NLU)**: High-accuracy streaming ASR (Sarvam Saaras v3 + Government Bhashini) and Gemini Flash for conversational reasoning.
2. **HOW it is spoken (Acoustic & Emotion Intelligence)**: Raw 8kHz/16kHz audio prosodic feature extraction (openSMILE eGeMAPS) and Speech Emotion Recognition (Wav2Vec2).
3. **WHAT must happen (Deterministic Safety Decision Engine)**: An unbypassable rule engine (`TraumaController`) with hardcoded safety override gates and verified knowledge grounding.

```
                          ┌─────────────────────┐
                          │   CALLER (PHONE)    │
                          │   PSTN / Browser    │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   TELEPHONY LAYER   │
                          │   Exotel / WebRTC   │
                          └──────────┬──────────┘
                                     │
                             WebSocket (PCM)
                                     │
                                     ▼
                       ┌───────────────────────────┐
                       │      FASTAPI SERVER       │
                       │   Voice Gateway Router    │
                       └─────────────┬─────────────┘
                                     │
                       ┌─────────────┴─────────────┐
                       ▼                           ▼
             ┌──────────────────┐        ┌──────────────────┐
             │ LANGUAGE ROUTER  │        │ RAW AUDIO STREAM │
             │ Sarvam / Bhashini│        │ 8kHz -> 16kHz    │
             └────────┬─────────┘        └────────┬─────────┘
                      │                           │
                ┌─────┴─────┐               ┌─────┴─────┐
                ▼           ▼               ▼           ▼
           ┌─────────┐ ┌─────────┐    ┌──────────┐ ┌──────────┐
           │ Sarvam  │ │Bhashini │    │ Wav2Vec2 │ │ openSMILE│
           │  STT    │ │  STT    │    │ Emotion  │ │ Acoustic │
           └────┬────┘ └────┬────┘    └────┬─────┘ └────┬─────┘
                │           │              │            │
                └─────┬─────┘              └──────┬─────┘
                      │                           │
                      ▼                           ▼
                 TRANSCRIPT                DISTRESS SIGNALS
                      │                           │
                      └─────────────┬─────────────┘
                                    ▼
                        ┌─────────────────────────┐
                        │ DISTRESS FUSION ENGINE  │
                        │ Multi-Signal Assessment │
                        └───────────┬─────────────┘
                                    │
                                    ▼
                        ┌─────────────────────────┐
                        │    TRAUMA CONTROLLER    │
                        │ Deterministic Safeguard │
                        └───────────┬─────────────┘
                                    │
                        ┌───────────┴───────────┐
                        ▼                       ▼
                ┌──────────────┐       ┌────────────────┐
                │  KNOWLEDGE   │       │     GEMINI     │
                │  / RAG       │──────▶│ Conversational │
                │  (14566/PoA) │       │ Reasoning      │
                └──────────────┘       └───────┬────────┘
                                               │
                                               ▼
                                     ┌──────────────────┐
                                     │ SAFETY VALIDATOR │
                                     └────────┬─────────┘
                                              │
                                              ▼
                                 Safe Multilingual Response
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │ Sarvam/Bhashini  │
                                     │       TTS        │
                                     └────────┬─────────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │  EXOTEL / CALLER │
                                     └──────────────────┘
```

---

### 2. Subsystem Descriptions

#### 2.1 Telephony Ingestion & Resilience
* **Real Call Telephony**: Ingests bidirectional 8kHz μ-law/PCM audio via Exotel WebSocket AgentStream.
* **Direct Web Audio**: Ingests 16kHz linear PCM via browser WebSocket directly from `http://localhost:8000/test`.
* **Zero-Drop Resilience**: Both streams map to the identical internal `AudioFrame` structure, allowing the team to demonstrate seamlessly via phone call or browser microphone.

#### 2.2 Speech & Multilingual Orchestration
* **Sarvam AI (Saaras v3)**: Primary ASR for major Indian languages (Hindi, Odia, Bengali, Tamil, Telugu, English) and code-mixed speech (e.g. Odia + English / Hinglish).
* **Bhashini Ulca**: Fallback infrastructure for scheduled and tribal languages (Kui, Desia, Santali, Sambalpuri).
* **Language Router**: Evaluates language identification confidence ($>0.75$) within the first 2.5 seconds and binds the session language.

#### 2.3 Acoustic Prosody & Speech Emotion Recognition
* **openSMILE (eGeMAPS)**: Extracts F0 mean/variance, jitter, shimmer, pause ratio, speech rate, and loudness directly from raw audio chunks.
* **Wav2Vec2 SER**: Outputs normalized probability distributions over emotional states ($p_{\text{fear}}, p_{\text{sadness}}, p_{\text{anger}}, p_{\text{neutral}}$).
* **8kHz Narrowband Resampling**: Decodes μ-law to linear PCM and uses polyphase sinc interpolation to 16kHz with pre-emphasis to eliminate spectral voids.

#### 2.4 Multimodal Distress Fusion
Fuses four discrete signal vectors into a single bounded score ($S_{\text{turn}} \in [0.0, 1.0]$):
1. $A_{\text{norm}}$: Acoustic arousal index (openSMILE).
2. $E_{\text{fear\_sad}}$: Fear and sadness probability (Wav2Vec2).
3. $L_{\text{risk}}$: Linguistic danger marker density.
4. $C_{\text{hesitation}}$: Conversational latency and silence ratio.

An Exponential Moving Average (EMA) aggregates temporal distress over conversation turns to eliminate single-segment false alarms.

#### 2.5 Deterministic Trauma & Risk Controller
* Overrides LLM output when safety rules are triggered.
* **CRITICAL**: Immediate physical violence, weapons, self-harm language $\rightarrow$ Instant silent operator alarm and emergency 112 bridge.
* **HIGH**: Severe intimidation, caste-based threat, acute crying $\rightarrow$ Calming speech rate, operator queue alert.
* **MODERATE**: General emotional distress, non-imminent complaints $\rightarrow$ Empathetic grounding.
* **LOW**: Informational or administrative inquiries $\rightarrow$ Direct guidance.

#### 2.6 Verified RAG & Safety Validator
* **Supabase pgvector**: Stores verified legal provisions (SC/ST PoA Act Section 15A), helplines (112, 108, 14416, 14566), and DLSA contacts.
* **SafetyValidator**: Pre- and post-generation regex/semantic inspection blocking hallucinated phone numbers, unauthorized medical diagnoses, or victim-blaming phrases.
