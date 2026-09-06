-- ==============================================================================
-- NHAA (14566) Voice Triage Schema (Supabase / PostgreSQL)
-- Migration: 20260904_initial_schema.sql
-- ==============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. Operator Profiles (Authorized Helpline Staff)
CREATE TABLE IF NOT EXISTS operator_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    badge_number TEXT UNIQUE NOT NULL,
    role TEXT CHECK (role IN ('operator', 'supervisor', 'admin')) DEFAULT 'operator',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Call Sessions (High-level lifecycle metadata)
CREATE TABLE IF NOT EXISTS call_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_call_id TEXT UNIQUE NOT NULL,
    caller_phone_hash TEXT NOT NULL, -- Salted SHA-256 hash (never raw phone number)
    telephony_provider TEXT NOT NULL DEFAULT 'mock',
    status TEXT CHECK (status IN ('initiated', 'in_progress', 'escalated', 'completed', 'abandoned')) DEFAULT 'initiated',
    detected_language TEXT DEFAULT 'und',
    language_confidence NUMERIC(4,3) DEFAULT 0.000,
    consent_given BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMPTZ,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Transcript Segments (Segmented conversation logs with PII scrubbing)
CREATE TABLE IF NOT EXISTS transcript_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_session_id UUID NOT NULL REFERENCES call_sessions(id) ON DELETE CASCADE,
    speaker TEXT CHECK (speaker IN ('caller', 'agent', 'operator')) NOT NULL,
    sequence_num INT NOT NULL,
    text_content TEXT NOT NULL,
    language TEXT,
    start_time_ms INT NOT NULL,
    end_time_ms INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Acoustic Features (openSMILE eGeMAPS prosody parameters)
CREATE TABLE IF NOT EXISTS acoustic_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_session_id UUID NOT NULL REFERENCES call_sessions(id) ON DELETE CASCADE,
    segment_id UUID REFERENCES transcript_segments(id) ON DELETE SET NULL,
    mean_pitch_f0 NUMERIC(6,2),
    pitch_variability NUMERIC(6,2),
    jitter NUMERIC(6,4),
    shimmer NUMERIC(6,4),
    pause_ratio NUMERIC(4,3),
    speech_rate NUMERIC(5,2),
    voice_activity_ratio NUMERIC(4,3),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Emotion Predictions (Wav2Vec2 softmax probability distribution)
CREATE TABLE IF NOT EXISTS emotion_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_session_id UUID NOT NULL REFERENCES call_sessions(id) ON DELETE CASCADE,
    segment_id UUID REFERENCES transcript_segments(id) ON DELETE SET NULL,
    prob_fear NUMERIC(4,3) NOT NULL,
    prob_sadness NUMERIC(4,3) NOT NULL,
    prob_anger NUMERIC(4,3) NOT NULL,
    prob_neutral NUMERIC(4,3) NOT NULL,
    dominant_emotion TEXT NOT NULL,
    confidence NUMERIC(4,3) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Risk Assessments (Multimodal distress fusion outputs)
CREATE TABLE IF NOT EXISTS risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_session_id UUID NOT NULL REFERENCES call_sessions(id) ON DELETE CASCADE,
    risk_score NUMERIC(4,3) NOT NULL,
    risk_level TEXT CHECK (risk_level IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')) NOT NULL,
    confidence NUMERIC(4,3) NOT NULL,
    safety_flags JSONB DEFAULT '{}'::jsonb,
    evidence_summary JSONB DEFAULT '[]'::jsonb,
    recommended_action TEXT NOT NULL,
    requires_human_escalation BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Escalations (Real-time operator queue records)
CREATE TABLE IF NOT EXISTS escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_session_id UUID NOT NULL REFERENCES call_sessions(id) ON DELETE CASCADE,
    assigned_operator_id UUID REFERENCES operator_profiles(id) ON DELETE SET NULL,
    trigger_reason TEXT NOT NULL,
    status TEXT CHECK (status IN ('pending', 'acknowledged', 'resolved')) DEFAULT 'pending',
    escalated_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- 8. Verified Knowledge Documents (RAG store for legal aid and helplines)
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    category TEXT CHECK (category IN ('emergency', 'legal', 'medical', 'counselling', 'scheme')) NOT NULL,
    source TEXT NOT NULL,
    jurisdiction TEXT DEFAULT 'National',
    content TEXT NOT NULL,
    embedding VECTOR(768),
    last_verified TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Audit Logs (Compliance and tamper-evident audit trail)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_session_id UUID REFERENCES call_sessions(id) ON DELETE SET NULL,
    actor_type TEXT CHECK (actor_type IN ('system', 'operator', 'api')) NOT NULL,
    action TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    ip_address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create helpful indices for performance
CREATE INDEX IF NOT EXISTS idx_call_sessions_status ON call_sessions(status);
CREATE INDEX IF NOT EXISTS idx_transcript_segments_call ON transcript_segments(call_session_id);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_call ON risk_assessments(call_session_id);
CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalations(status);

-- Enable Row Level Security (RLS) on sensitive tables
ALTER TABLE call_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcript_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE escalations ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
