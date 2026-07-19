-- SANTINEL v2.0 COMPLETE SCHEMA

-- =====================================================
-- CORE USERS & AUTHENTICATION
-- =====================================================

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    profile_personality JSONB,
    anchored_states JSONB
);

-- =====================================================
-- THIRD PARTIES (People user negotiates with)
-- =====================================================

CREATE TABLE third_parties (
    third_party_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    name VARCHAR(255) NOT NULL,
    role VARCHAR(255),
    company VARCHAR(255),
    industry VARCHAR(255),
    first_interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    communication_profile JSONB,
    emotional_baseline JSONB,
    success_patterns JSONB,
    interaction_count INTEGER DEFAULT 0,
    last_interaction_date TIMESTAMP
);

-- =====================================================
-- SESSIONS
-- =====================================================

CREATE TABLE sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    third_party_id INTEGER REFERENCES third_parties(third_party_id),
    session_type VARCHAR(50),
    objective TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    context_data JSONB,
    outcomes JSONB,
    analysis_data JSONB
);

-- =====================================================
-- COACHING INTERACTIONS
-- =====================================================

CREATE TABLE coaching_interactions (
    interaction_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id),
    third_party_id INTEGER REFERENCES third_parties(third_party_id),
    sequence_number INTEGER,
    coaching_data JSONB,
    user_response JSONB,
    effectiveness JSONB,
    third_party_reaction JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- FEEDBACK & OUTCOMES
-- =====================================================

CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(session_id),
    coaching_id VARCHAR(255),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    quality_score REAL,
    useful_aspects TEXT,
    comments TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE outcomes (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(session_id),
    contact_name VARCHAR(255),
    company_name VARCHAR(255),
    negotiation_type VARCHAR(255),
    success INTEGER,
    target_value REAL,
    actual_value REAL,
    target_achieved REAL,
    actual_achieved REAL,
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PSYCHOLOGY FRAMEWORKS & TECHNIQUES
-- =====================================================

CREATE TABLE psychology_frameworks (
    framework_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(100),
    techniques_count INTEGER,
    effectiveness_score REAL,
    description TEXT
);

CREATE TABLE psychology_techniques (
    technique_id SERIAL PRIMARY KEY,
    framework_id INTEGER NOT NULL REFERENCES psychology_frameworks(framework_id),
    technique_name VARCHAR(255) NOT NULL,
    description TEXT,
    step_by_step_process TEXT,
    when_to_use TEXT,
    when_not_to_use TEXT,
    effectiveness_score REAL,
    source VARCHAR(255)
);

-- =====================================================
-- PATTERN LEARNING & OPTIMIZATION
-- =====================================================

CREATE TABLE pattern_learnings (
    learning_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    third_party_id INTEGER REFERENCES third_parties(third_party_id),
    what_worked JSONB,
    what_didnt_work JSONB,
    reframe_preferences JSONB,
    anchor_effectiveness JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_level REAL
);

CREATE TABLE technique_effectiveness (
    effectiveness_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    third_party_id INTEGER REFERENCES third_parties(third_party_id),
    technique_used VARCHAR(255),
    framework_used VARCHAR(100),
    did_it_work BOOLEAN,
    effectiveness_score REAL,
    context TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- VECTOR PATTERNS (Pinecone storage tracking)
-- =====================================================

CREATE TABLE vector_patterns (
    id SERIAL PRIMARY KEY,
    pattern_id VARCHAR(255) UNIQUE,
    coaching_text TEXT,
    situation_type VARCHAR(100),
    frameworks_used TEXT,
    rating INTEGER,
    quality_score REAL,
    session_id VARCHAR(255) REFERENCES sessions(session_id),
    success_outcome INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- FINE-TUNING & MODEL MANAGEMENT
-- =====================================================

CREATE TABLE finetuning_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE,
    provider VARCHAR(100),
    model_name VARCHAR(255),
    status VARCHAR(50),
    examples_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE model_versions (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255),
    version VARCHAR(50),
    provider VARCHAR(100),
    status VARCHAR(50),
    performance_rating REAL,
    deployed_at TIMESTAMP
);

CREATE TABLE coaching_performance (
    id SERIAL PRIMARY KEY,
    coaching_id VARCHAR(255),
    framework_used VARCHAR(100),
    user_satisfaction REAL,
    outcome_success_rate REAL,
    improvement_trend REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(255),
    metric_value REAL,
    period VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- VOICE RECOGNITION & EMOTION DETECTION
-- =====================================================

CREATE TABLE voice_fingerprints (
    fingerprint_id SERIAL PRIMARY KEY,
    third_party_id INTEGER NOT NULL REFERENCES third_parties(third_party_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    voice_embedding BYTEA,
    baseline_features JSONB,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    samples_count INTEGER DEFAULT 0,
    confidence_score REAL
);

CREATE TABLE voice_samples_archive (
    sample_id SERIAL PRIMARY KEY,
    fingerprint_id INTEGER NOT NULL REFERENCES voice_fingerprints(fingerprint_id),
    session_id VARCHAR(255) REFERENCES sessions(session_id),
    audio_file_path VARCHAR(500),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    emotion_at_time VARCHAR(100),
    transcription TEXT
);

CREATE TABLE emotional_voice_patterns (
    pattern_id SERIAL PRIMARY KEY,
    third_party_id INTEGER NOT NULL REFERENCES third_parties(third_party_id),
    emotion VARCHAR(50),
    voice_characteristics JSONB,
    accuracy_score REAL,
    sample_count INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES (For performance)
-- =====================================================

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_third_parties_user_id ON third_parties(user_id);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_third_party_id ON sessions(third_party_id);
CREATE INDEX idx_coaching_interactions_session_id ON coaching_interactions(session_id);
CREATE INDEX idx_pattern_learnings_user_id ON pattern_learnings(user_id);
CREATE INDEX idx_pattern_learnings_third_party_id ON pattern_learnings(third_party_id);
CREATE INDEX idx_voice_fingerprints_third_party_id ON voice_fingerprints(third_party_id);
CREATE INDEX idx_voice_samples_fingerprint_id ON voice_samples_archive(fingerprint_id);