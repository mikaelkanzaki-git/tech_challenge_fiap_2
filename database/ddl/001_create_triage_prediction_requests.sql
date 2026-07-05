-- Run this script connected to the tech_challenge_fiap_2 database.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS triage_prediction_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    age NUMERIC(5, 2) NOT NULL CHECK (age >= 0 AND age <= 120),
    heart_rate NUMERIC(5, 2) NOT NULL CHECK (heart_rate >= 0 AND heart_rate <= 250),
    systolic_blood_pressure NUMERIC(5, 2) NOT NULL CHECK (
        systolic_blood_pressure >= 0 AND systolic_blood_pressure <= 300
    ),
    oxygen_saturation NUMERIC(5, 2) NOT NULL CHECK (
        oxygen_saturation >= 0 AND oxygen_saturation <= 100
    ),
    body_temperature NUMERIC(4, 2) NOT NULL CHECK (
        body_temperature >= 30 AND body_temperature <= 45
    ),
    pain_level SMALLINT NOT NULL CHECK (pain_level >= 0 AND pain_level <= 10),
    chronic_disease_count SMALLINT NOT NULL CHECK (chronic_disease_count >= 0),
    previous_er_visits SMALLINT NOT NULL CHECK (previous_er_visits >= 0),
    arrival_mode VARCHAR(20) NOT NULL CHECK (
        arrival_mode IN ('walk_in', 'wheelchair', 'ambulance')
    ),
    triage_level SMALLINT NOT NULL CHECK (triage_level BETWEEN 0 AND 3),
    triage_label VARCHAR(20) NOT NULL,
    probabilities JSONB NOT NULL,
    model_version VARCHAR(80) NOT NULL DEFAULT 'local',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_triage_prediction_requests_created_at
    ON triage_prediction_requests (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_triage_prediction_requests_triage_level
    ON triage_prediction_requests (triage_level);
