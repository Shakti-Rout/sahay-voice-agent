# API Specification (REST & WebSockets)
## SIH 2026 PS 26093: NHAA Voice Agent Endpoints

### 1. Base URL
* Local Development: `http://localhost:8000/api/v1`
* WebSocket Base: `ws://localhost:8000/ws`

---

### 2. REST Endpoints (`/api/v1`)

#### 2.1 Health & Diagnostic Check
* **Method**: `GET /api/v1/health`
* **Summary**: Returns overall server health, model readiness, and provider latencies.
* **Response (200 OK)**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "providers": {
    "telephony": "mock",
    "stt": "sarvam",
    "tts": "sarvam",
    "llm": "gemini",
    "database": "supabase"
  },
  "models_loaded": {
    "openSMILE": true,
    "wav2vec2_ser": true
  },
  "timestamp": "2026-09-05T10:30:00Z"
}
```

#### 2.2 Exotel Telephony Inbound Webhook
* **Method**: `POST /api/v1/calls/webhook/exotel`
* **Summary**: Ingestion endpoint called by Exotel when a citizen dials the virtual helpline number.
* **Request Body (from Exotel)**:
```json
{
  "CallSid": "ex_call_98741",
  "From": "+919876543210",
  "To": "+918069290000",
  "Direction": "inbound",
  "CallType": "tranship"
}
```
* **Response (200 OK)**: Exotel JSON/XML instructing Exotel to open the AgentStream WebSocket connection to `/ws/exotel/{call_id}`.

#### 2.3 Get Call Session Details
* **Method**: `GET /api/v1/calls/{call_id}`
* **Response (200 OK)**:
```json
{
  "call_id": "call_98741",
  "status": "in_progress",
  "detected_language": "or",
  "language_confidence": 0.94,
  "consent_given": true,
  "started_at": "2026-09-05T10:30:00Z",
  "latest_risk_level": "HIGH",
  "latest_risk_score": 0.78
}
```

#### 2.4 Offline Audio Diagnostic Test Endpoint
* **Method**: `POST /api/v1/test/audio`
* **Content-Type**: `multipart/form-data`
* **Parameters**: `file`: WAV audio file (8kHz or 16kHz)
* **Response (200 OK)**:
```json
{
  "language": {
    "detected": "or",
    "confidence": 0.94
  },
  "transcript": "Mu bahut darichhi. Se mate dhamaka deichhi.",
  "emotion": {
    "probabilities": {
      "fear": 0.72,
      "sadness": 0.18,
      "anger": 0.07,
      "neutral": 0.03
    },
    "dominant": "fear",
    "confidence": 0.72
  },
  "acoustic": {
    "mean_pitch_f0": 248.5,
    "pause_ratio": 0.38,
    "jitter": 0.042,
    "speech_rate": 3.2
  },
  "linguistic": {
    "risk_indicators": ["fear", "threat"]
  },
  "risk": {
    "level": "HIGH",
    "score": 0.78,
    "requires_human_escalation": true
  },
  "ai_response": {
    "text": "Mu apananka katha bujhiparuchhi. Apan bartaman safe achhanti ki?",
    "audio_latency_ms": 840
  }
}
```

---

### 3. WebSocket Endpoints (`/ws`)

#### 3.1 Browser Direct Audio Stream (`/ws/client/{call_id}`)
Used by the **Dev Test Console (`/test`)** for zero-cost microphone streaming.
* **Inbound Message (Microphone to Server)**:
```json
{
  "event": "media",
  "call_id": "local_test_01",
  "format": "audio/pcm",
  "sample_rate": 16000,
  "payload": "<base64_encoded_pcm_chunk>"
}
```
* **Outbound Message (Server to Browser)**:
```json
{
  "event": "media",
  "call_id": "local_test_01",
  "payload": "<base64_encoded_tts_chunk>"
}
```
* **Interruption / Barge-in Command**:
```json
{
  "event": "clear_buffer",
  "call_id": "local_test_01",
  "reason": "caller_speech_detected"
}
```

#### 3.2 Exotel Telephony Stream (`/ws/exotel/{call_id}`)
Bidirectional 8kHz audio bridge mapped directly to Exotel AgentStream specification.
