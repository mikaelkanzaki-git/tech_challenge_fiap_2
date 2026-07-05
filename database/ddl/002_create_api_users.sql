-- Run this script connected to the application database.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS api_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(64) NOT NULL,
    password_salt VARCHAR(255) NOT NULL,
    password_iterations INTEGER NOT NULL CHECK (password_iterations > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_users_email
    ON api_users (email);

INSERT INTO api_users (
    email,
    password_hash,
    password_salt,
    password_iterations,
    is_active
)
VALUES (
    'fiap@tech2.com',
    '139469b8f294c7212ca901e29a3dca86b68a0803c5c362e6b6baf3f0711b3e06',
    'tech_challenge_fiap_2_fiap_user',
    260000,
    TRUE
)
ON CONFLICT (email)
DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    password_salt = EXCLUDED.password_salt,
    password_iterations = EXCLUDED.password_iterations,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();
