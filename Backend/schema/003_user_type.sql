-- Persist signup context for verified and pending accounts.
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS user_type VARCHAR(32) NOT NULL DEFAULT 'other';

ALTER TABLE pending_users
    ADD COLUMN IF NOT EXISTS user_type VARCHAR(32) NOT NULL DEFAULT 'other';

ALTER TABLE users
    DROP CONSTRAINT IF EXISTS users_user_type_check;
ALTER TABLE users
    ADD CONSTRAINT users_user_type_check
    CHECK (user_type IN ('student', 'working_professional', 'both', 'other'));

ALTER TABLE pending_users
    DROP CONSTRAINT IF EXISTS pending_users_user_type_check;
ALTER TABLE pending_users
    ADD CONSTRAINT pending_users_user_type_check
    CHECK (user_type IN ('student', 'working_professional', 'both', 'other'));
