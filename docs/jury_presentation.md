# SIH 2026 PS 26093: Jury Presentation & Pitch Guide
## AI-Based Real-Time Stress & Trauma Assessment Module for NHAA (14566)

> **Helpline Context**: National Helpline Against Atrocities (NHAA - 14566)  
> **Target Audience**: SIH Evaluation Jury, Ministry Evaluators, and Technical Assessors  
> **Demo URL**: `http://localhost:8000/dashboard` (Live Dispatcher Dashboard) & `http://localhost:8000/test` (Live Mic Console)  

---

## 1. The 2-Minute Elevator Pitch (Say This Verbatim)

> *"Respected Jury members, every day hundreds of citizens facing caste violence, intimidation, and acute distress dial the National Helpline Against Atrocities (14566). But human operators are often overwhelmed, leading to call queue delays, missed danger signals, and inconsistent triage.*
> 
> *Our team presents an **AI-orchestrated, multimodal real-time voice triage agent** built specifically for the 14566 telecom exchange.*
> 
> *Unlike ordinary chatbots, our system is decoupled into a **clinical-safety triad***:
> 1. * **What they said**: Multilingual ASR (Odia, Hindi, English, and tribal dialects like Sambalpuri) with zero-hallucination statutory legal RAG (PoA Act Section 15A).*
> 2. * **How they said it**: openSMILE acoustic prosody (F0 pitch tremors, speech rate, pause ratio) combined with Wav2Vec2 speech emotion recognition measuring vocal fear and shock.*
> 3. * **What needs to happen**: A **100% deterministic Trauma Controller**—the LLM is never allowed to guess safety. Critical threats instantly trigger automated 112 police dispatch and human operator takeover.*
> 
> *Today, we demonstrate our live working system over both telephone audio and our real-time operator dispatch dashboard."*

---

## 2. Live Demo Sequence (Step-by-Step Flow)

### Screen Setup:
- **Left/Main Screen**: Operator Triage Dashboard at `http://localhost:8000/dashboard`.
- **Right Screen/Handset**: Dev Test Console at `http://localhost:8000/test` (or mobile phone on virtual demo line).

### The 4 Rehearsed Scenarios:

| Scenario | Spoken Input (Odia / Hindi) | System Actions | Triage Category | Operator Result |
| :--- | :--- | :--- | :---: | :--- |
| **1. Calm Inquiry** | *"Mu scholarship scheme bisayare kichhi information chahunchhi."* | Low pitch variance, neutral emotion, welfare retrieval. | **LOW** (Score: 0.12) | Automated response, 0 escalation. |
| **2. Emotional Distress** | *"Mu bahut darichhi, mo katha kehi sununahanti."* | Pitch tremor detected, fear 68%, hesitation pause. | **MODERATE** (Score: 0.54) | Calming tone, Tele-MANAS (14416) offered. |
| **3. Direct Threat** | *"Se mate marideba boli dhamaka deichhi."* | Threat keyword (`dhamaka`), vocal fear 74%. | **HIGH** (Score: 0.78) | Alert pushed to operator, PoA Section 15A rights. |
| **4. Imminent Danger** | *"Ghara bahare lathi dhari thia hoichhanti, kapata bhanguchhanti!"* | Weapon (`lathi`), violent entry override trigger. | **CRITICAL** (Score: 0.95) | **Flashing Red Alert**, 112 CAD Emergency Bridge. |

---

## 3. Defense Against Tough Jury Questions

### Q1: *"What if the LLM hallucinates fake legal advice or a made-up phone number?"*
**Answer**:
> *"We strictly isolate the LLM from safety-critical authority. The LLM only drafts natural conversation. 
> All phone numbers are filtered through a hardcoded regex whitelist (`14566`, `112`, `108`, `14416`, `15100`). Any unapproved number is instantly redacted by our post-generation `SafetyValidator`. Furthermore, legal provisions come exclusively from our verified PoA Act Section 15A vector store."*

### Q2: *"Can this system diagnose trauma or PTSD?"*
**Answer**:
> *"No, and by design it never will. Our system is strictly a **decision-support and triage tool**, not a medical diagnostic engine. We output probabilistic distress indicators (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`) to prioritize human operator attention. Our system prompts and safety validator explicitly forbid medical diagnoses."*

### Q3: *"How does this perform on noisy, low-bandwidth 8kHz rural telephone lines?"*
**Answer**:
> *"Standard telecom audio is 8kHz G.711 μ-law. We built an ITU-T lookup table and polyphase band-limited sinc resampler that converts 8kHz telephony audio to 16kHz with spectral pre-emphasis before acoustic feature extraction. Our VAD detects speech boundaries in under 150ms and supports instantaneous barge-in interruption."*

### Q4: *"How do you comply with the DPDP Act 2023 and protect victim confidentiality?"*
**Answer**:
> *"1. **Zero Raw Audio Retention**: Voice audio remains strictly in ephemeral RAM circular buffers during the call and is discarded immediately post-inference.  
> 2. **Salted SHA-256 Phone Hashing**: We never store raw phone numbers; all sessions use one-way salted cryptographic hashes.  
> 3. **Row-Level Security (RLS)**: The database restricts transcript access exclusively to authenticated helpline supervisors."*

### Q5: *"How do you handle tribal dialects and code-switching in Odisha/Jharkhand/Chhattisgarh?"*
**Answer**:
> *"Our `LanguageRouter` features a native script detector, phonetic transliteration mapper, and a dedicated `DialectBridge`. For example, in western Odisha, callers speaking Sambalpuri/Kosli use words like 'kanje' (why) or 'marba' (will beat); our bridge normalizes these to standard Odia for semantic analysis while allowing the voice agent to respond with regional empathy."*
