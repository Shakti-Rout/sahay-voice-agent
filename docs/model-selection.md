# Model Selection & Inference Strategy
## SIH 2026 PS 26093: AI Model Benchmarking and Selection

### 1. Overview of AI Models Used

| Component | Selected Model / Provider | License / Access | Inference Mode | Latency Target |
| :--- | :--- | :--- | :--- | :--- |
| **Speech-to-Text (STT)** | **Sarvam Saaras v3** (with Bhashini ASR fallback) | Commercial API (Free trial credits) | Streaming Cloud API | < 300 ms |
| **Speech Emotion Recognition (SER)**| **Wav2Vec2-XLSR fine-tuned SER** | Open Source (Apache 2.0) | Local CPU-INT8 / CUDA | < 120 ms |
| **Acoustic Prosody Extraction** | **openSMILE (eGeMAPS 88-feature set)** | Open Source (LGPL / Research) | Local C++ / Python binary | < 50 ms |
| **Conversational Reasoning & NLU** | **Google Gemini 2.0 Flash** | Cloud API (Free tier) | Streaming SSE API | < 350 ms (TTFT)|
| **Text-to-Speech (TTS)** | **Sarvam Bulbul** (with Bhashini TTS fallback) | Commercial API (Free trial credits) | Streaming Audio Chunk API| < 250 ms |

---

### 2. Speech Emotion Recognition: Wav2Vec2 vs Custom Models

#### Why NOT train from scratch?
1. **Data Scarcity**: Real-world emergency helpline trauma audio is strictly confidential and unavailable for training public models. Training on small acted datasets from scratch yields severe overfitting.
2. **Transfer Learning**: Pretrained cross-lingual models (like Wav2Vec2-XLSR-53) have learned foundational acoustic and phonetic representations across 50+ languages, including Indian languages.

#### Selected Checkpoint:
* Model: `ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition` or `superb/wav2vec2-base-superb-er`
* Calibration: The model outputs softmax logits over four baseline states:
  $$\mathbf{P} = [p_{\text{fear}}, p_{\text{sadness}}, p_{\text{anger}}, p_{\text{neutral}}]$$
* **Scientific Constraint**: Softmax probabilities are treated as **acoustic proxy features**, never as a psychiatric diagnosis.

---

### 3. openSMILE Acoustic Feature Set: eGeMAPS

The **extended Geneva Minimalistic Acoustic Parameter Set (eGeMAPS)** is the internationally recognized gold standard for acoustic distress measurement.

#### Key Features Monitored:
1. **F0 Fundamental Frequency (Pitch)**:
   - `F0semitoneFrom27.5Hz_sma3nz_amean`: Mean vocal pitch.
   - `F0semitoneFrom27.5Hz_sma3nz_stddevNorm`: Pitch variability. Elevated in panic and acute fear.
2. **Acoustic Perturbation (Tremor)**:
   - `jitterLocal_sma3nz_amean`: Frequency perturbation. Correlates with vocal tremor during crying or shock.
   - `shimmerLocaldB_sma3nz_amean`: Amplitude perturbation.
3. **Temporal Dynamics**:
   - `pause_ratio`: Percentage of unvoiced pause duration relative to speech duration.
   - `speech_rate`: Syllables/words per second.

---

### 4. 8kHz Telephony Narrowband Audio Optimization

Telephone audio arrives sampled at 8,000 Hz. If fed directly into models expecting 16,000 Hz, zero-padding or naive interpolation creates artificial harmonics that confuse the emotion classifier.

#### Audio Normalization Pipeline:
1. **μ-law to Float32 Conversion**:
   $$x[n] = \text{sign}(y) \frac{(1 + \mu)^{|y|} - 1}{\mu}, \quad \mu = 255$$
2. **Band-Limited Sinc Resampling**: Polyphase resampler (`torchaudio.transforms.Resample(8000, 16000)`).
3. **Pre-emphasis Filter**:
   $$y[n] = x[n] - 0.97 x[n-1]$$
4. **RMS Volume Normalization**: Normalizes target chunk energy to $-20\text{ dBFS}$ before feature extraction.
