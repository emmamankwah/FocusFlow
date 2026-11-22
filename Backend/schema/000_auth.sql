-- Core authentication tables used by the API. These are created before the
-- follow-up schema files when PostgreSQL initializes the database.
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    user_type VARCHAR(32) NOT NULL DEFAULT 'other'
        CHECK (user_type IN ('student', 'working_professional', 'both', 'other'))
);

CREATE TABLE IF NOT EXISTS pending_users (
    email VARCHAR(255) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    user_type VARCHAR(32) NOT NULL DEFAULT 'other'
        CHECK (user_type IN ('student', 'working_professional', 'both', 'other'))
);

CREATE TABLE IF NOT EXISTS otp_table (
    email VARCHAR(255) PRIMARY KEY,
    hash_otp TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    expired_at TIMESTAMPTZ NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    total_attempts INTEGER NOT NULL DEFAULT 3
);
