-- =====================================================
-- 001_auth.sql — JWT auth support
-- Idempotent. Apply to santinel_prod:
--   ./pg.bat -d santinel_prod -f migrations/001_auth.sql
-- The `users` table already exists (see schema.sql); this only adds the
-- rotating-refresh-token store. Access tokens are stateless and never stored.
-- =====================================================

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id           BIGSERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    jti_hash     CHAR(64) NOT NULL UNIQUE,          -- sha256 hex of the refresh-token jti
    issued_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at   TIMESTAMPTZ NOT NULL,
    revoked_at   TIMESTAMPTZ,                       -- set on rotation, logout, or reuse detection
    user_agent   VARCHAR(255),
    ip           VARCHAR(64)
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_exp  ON refresh_tokens(expires_at);

-- Housekeeping (run from cron, not automatic):
--   DELETE FROM refresh_tokens WHERE expires_at < now() - INTERVAL '7 days';
