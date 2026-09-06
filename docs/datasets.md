# Dataset Strategy & Ethical Provenance
## SIH 2026 PS 26093: Data Architecture for NHAA Voice Triage

### 1. The Ethical & Scientific Boundary
We explicitly do **NOT** claim to possess or utilize a "dataset of real trauma calls."
Authentic distress calls made by victims of caste atrocities, domestic violence, or assault contain deeply sensitive, non-shareable personal identifying information (PII) protected under:
* The Digital Personal Data Protection (DPDP) Act 2023
* The SC/ST Prevention of Atrocities Act (Section 15A: Rights of Victims and Witnesses)
* Medical ethics guidelines regarding trauma victims

Our dataset architecture cleanly decouples the evaluation requirements across four legitimate categories:

```
data/
├── raw/                 # Scripts and manifest files for public dataset download
├── processed/           # Feature scalers and normalized acoustic baselines
├── synthetic/           # Scripted, consenting roleplay audio recorded for SIH testing
└── test_audio/          # 5 Core benchmark scenarios in Odia, Hindi, and English
    ├── odia/
    ├── hindi/
    └── english/
```

---

### 2. Dataset Segregation Matrix

| Category | Primary Sources | Purpose | Licensing & Usage Rules |
| :--- | :--- | :--- | :--- |
| **1. Indian Language Speech** | **Project VAANI** (IISc / ARTPARK / Google)<br>**Kathbath** (AI4Bharat / IIT Madras) | Indic ASR benchmarking, accent resilience, dialect diversity (Odia/Hindi) | Open Data Commons / CC-BY 4.0. Permitted for research & hackathon evaluation. |
| **2. Speech Emotion Recognition** | **RAVDESS**<br>**CREMA-D**<br>**TESS**<br>**SAVEE** (Kaggle Benchmark) | Multi-corpus SER acoustic baseline & stress feature extraction | Open academic datasets with consenting actors. Labeled explicitly as "acted emotion". |
| **3. Synthetic Roleplay Scenarios** | Internal Team Synthetic Recordings (30 clips) | End-to-end system testing of multi-turn dialogue | Recorded by consenting team members using simulated emergency scripts. |
| **4. Linguistic Risk Corpus (ILRC)** | **Indian Linguistic Risk Corpus** (500 phrases across 10 trauma domains) | Deterministic NLU keyword & safety override matcher in Odia, Hindi, English | Hand-crafted and verified domain rules stored in `data/processed/indian_linguistic_risk_corpus.csv`. |

---

### 3. Indic Speech Corpora & Acoustic Foundations

#### A. Project VAANI (IISc / ARTPARK / Google)
* **Official Portal**: [Project VAANI Version 1](https://vaani.iisc.ac.in/dataset/Version1)
* **Hugging Face Repository**: [ARTPARK-IISc/Vaani](https://huggingface.co/datasets/ARTPARK-IISc/Vaani)
* **Specifications**:
  - Over **16,000+ hours** of open-source spontaneous conversational speech collected across 80+ districts of India.
  - Covers rural and semi-urban speakers across diverse socio-economic backgrounds, including key Odia dialect clusters (Mayurbhanj, Ganjam, Sambalpur, Cuttack, Balasore) and Hindi heartland regions.
  - Captures realistic, non-studio acoustic environments (traffic, wind, room noise floor, household reverberation), essential for calibrating our noise-robust VAD and multi-frame acoustic horn/siren scanner.

#### B. Kathbath (AI4Bharat / IIT Madras)
* **Hugging Face Repository**: [ai4bharat/Kathbath](https://huggingface.co/datasets/ai4bharat/Kathbath)
* **Specifications**:
  - **1,684 hours** of curated, crowd-sourced speech across 12 Indian languages spoken by 84,000+ distinct speakers.
  - Used as our primary ASR benchmark for regional accent invariance, dialect normalization, and phonetic transcription evaluation in Odia (`or-IN`) and Hindi (`hi-IN`).

#### C. Indian Linguistic Risk Corpus (ILRC - 500 Phrases)
* **Dataset File**: [`data/processed/indian_linguistic_risk_corpus.csv`](file:///c:/Users/SAMBIT/OneDrive/Documents/My%20Projects/trauma-voice-agent/data/processed/indian_linguistic_risk_corpus.csv)
* **Specification Provenance**: Generated and structured via [ChatGPT Emergency Prompt Alignment](https://chatgpt.com/share/6a9d86e2-5178-83ee-a3a4-ea19594855ad).
* **Corpus Breakdown (50 Phrases per Category × 10 Domains)**:
  1. **Immediate Danger** (`ILRC_001` - `ILRC_050`): Imminent physical peril, acute fear, flight response. Severity: `CRITICAL`.
  2. **Physical Assault** (`ILRC_051` - `ILRC_100`): Active beating, bodily harm, physical battery. Severity: `CRITICAL`.
  3. **Death Threat** (`ILRC_101` - `ILRC_150`): Direct homicidal intimidation, life peril, lynching threats. Severity: `CRITICAL`.
  4. **Sexual Violence** (`ILRC_151` - `ILRC_200`): Sexual assault, non-consensual restraint, acute violation. Severity: `CRITICAL`.
  5. **Domestic Violence** (`ILRC_201` - `ILRC_250`): Intimate partner violence, household physical battery. Severity: `HIGH`.
  6. **Child Endangerment** (`ILRC_251` - `ILRC_300`): Minors under physical threat or abuse. Severity: `CRITICAL`.
  7. **Kidnapping & Restraint** (`ILRC_301` - `ILRC_350`): Forced confinement, hostage, illegal restraint. Severity: `CRITICAL`.
  8. **Medical Emergency** (`ILRC_351` - `ILRC_400`): Severe trauma, collapse, respiratory failure, bleeding. Severity: `CRITICAL`.
  9. **Self-Harm Crisis** (`ILRC_401` - `ILRC_450`): Suicidal ideation, self-injury crisis, hopelessness. Severity: `CRITICAL`.
  10. **Emergency Assistance** (`ILRC_451` - `ILRC_500`): Direct requests for police 112, ambulance 108, or rescue. Severity: `HIGH`.
* **Multilingual Schema**: Each entry includes native script (Odia & Devanagari), Romanized transliterations (e.g. Odialish / Hinglish), extracted keyword tags, urgency level, and expected deterministic protocol action (`SAFETY_ESCALATION`, `MEDICAL_ESCALATION`, `CRISIS_SUPPORT_ESCALATION`).
* **Runtime Integration**: Dynamically ingested by `SafetyRulesEngine` ([app/trauma/rules.py](file:///c:/Users/SAMBIT/OneDrive/Documents/My%20Projects/trauma-voice-agent/backend/app/trauma/rules.py)) to override LLM reasoning with deterministic safety gates.

---

### 4. Open Benchmark References & Kaggle Training Architectures

To anchor our multi-task trauma triage model against established academic and community state-of-the-art benchmarks without compromising PII, we incorporate two key reference methodologies:

#### A. Multi-Corpus Speech Emotion Recognition (SER) Pipeline
* **Kaggle Reference**: [Shivam Burnwal — Speech Emotion Recognition](https://www.kaggle.com/code/shivamburnwal/speech-emotion-recognition)
* **Underlying Datasets (12,162 Total Clips)**:
  1. **RAVDESS** (*Ryerson Audio-Visual Database of Emotional Speech and Song*): 1,440 audio-visual recordings of 24 professional actors (12M/12F) speaking lexically neutral statements in 8 emotional states (calm, happy, sad, angry, fearful, surprise, disgust).
  2. **CREMA-D** (*Crowd-sourced Emotional Multimodal Actors Dataset*): 7,442 clips from 91 actors (48M/43F) across 6 emotions at 4 intensity levels (low, medium, high, unspecified).
  3. **TESS** (*Toronto Emotional Speech Set*): 2,800 recordings from two female actors (ages 26 and 64) modeling 7 basic emotions.
  4. **SAVEE** (*Surrey Audio-Visual Expressed Emotion*): 480 British English audio files from 4 male actors across 7 emotions.
* **Feature Extraction Architecture**:
  - **Zero Crossing Rate (ZCR)**: High rate indicates fricatives, vocal tremor, or hyperventilation.
  - **Root Mean Square (RMS) Energy**: Dynamic energy tracking to detect vocal collapse vs. aggressive shouting.
  - **Mel-Frequency Cepstral Coefficients (MFCCs - 40 bands)**: Captures vocal tract shape and phoneme articulation anomalies under distress.
  - **Spectral Contrast & Mel-Spectrogram (128 bins)**: Analyzes harmonic richness and high-frequency energy spikes typical of fear and acute terror.
* **Role in NHAA Trauma Agent**:
  - Validates and calibrates our `StandardAcousticExtractor` (`app/acoustic/extractor.py`) and `Wav2VecEmotionClassifier` (`app/emotion/classifier.py`).
  - Benchmarked locally via `python scripts/benchmark_ser_features.py <path_to_audio.wav>`.

#### B. CareBot — AI Mental Health Companion (Google Cloud & Kaggle)
* **Kaggle Reference**: [CodeWithMoin — CareBot: AI Mental Health Companion](https://www.kaggle.com/code/codewithmoin/carebot-ai-mental-health-companion)
* **Program**: Google Cloud & Kaggle Generative AI Intensive (Moinuddin, Karthik, Tobi, Rotimi).
* **Core Principles & Architecture**:
  1. **Responsible-by-Default Governance**: Explicitly avoids practicing medicine or clinical psychiatry; operates as an empathetic "first-mile" listening post.
  2. **Multimodal Distress Grounding**: Fuses acoustic cues with linguistic indicators to identify acute distress, panic, and self-harm vulnerability.
  3. **RAG-Driven Psychological First Aid (PFA)**:
     - Curated evidence-based grounding protocols: 4-4-4 Box Breathing, 5-4-3-2-1 Sensory Reorientation, and calm presence validation.
     - Implemented in our verified knowledge base as `PFA-GROUNDING-CRISIS` (`app/rag/knowledge_base.py`).
  4. **Strict Escalation Boundary**: Detects when emotional reassurance is insufficient and triggers deterministic handoff to human emergency operators or Tele-MANAS (14416) / National Helpline (14566).

---

### 4. The 5 Standard Benchmark Evaluation Scenarios

These 5 scenarios are stored under `data/test_audio/` to test our offline diagnostic pipeline (`python scripts/test_audio.py`):

1. **Scenario 1 — Calm Administrative Inquiry (`calm_01.wav`)**:
   - Language: Hindi
   - Text: *"Mujhe SC welfare scholarship application ka status janna hai."*
   - Expected Risk: `LOW` (Score: 0.10 - 0.25). Zero human escalation.
2. **Scenario 2 — Distressed Emotional Reporting (`distress_01.wav`)**:
   - Language: Odia
   - Text: *"Mu bahut darichhi. Gaon re sabu loka amaku gaali karuchhanti o pani nebaku mana karuchhanti."*
   - Expected Risk: `MODERATE` (Score: 0.45 - 0.60). Grounding questions, detailed incident logging.
3. **Scenario 3 — Direct Physical Intimidation (`threat_01.wav`)**:
   - Language: Odia
   - Text: *"Se mane mo ghara bahare thia hoichhanti, marideba boli dhamaka deichhi."*
   - Expected Risk: `HIGH` (Score: 0.70 - 0.82). Silent operator queue alert.
4. **Scenario 4 — Active Imminent Danger (`critical_01.wav`)**:
   - Language: Hindi
   - Text: *"Bhaiya jaldi bachiye, unke paas talwar aur lathi hai, darwaza tod rahe hain!"*
   - Expected Risk: `CRITICAL` (Immediate safety rule trigger). One-click 112 emergency escalation.
5. **Scenario 5 — Multilingual Code-Switching (`codeswitch_01.wav`)**:
   - Language: Odia + English (Hinglish/Odialish)
   - Text: *"Sir mo pain continuous threat achi, land dispute re se mane kidnap karideba kahuchhanti, I am totally scared."*
   - Expected Behavior: Language Router recognizes mixed speech, transcribes faithfully, and triggers HIGH triage.
