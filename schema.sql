CREATE TABLE IF NOT EXISTS meta_posts (
    id BIGSERIAL PRIMARY KEY,
    facebook_id TEXT NOT NULL UNIQUE,
    message TEXT,
    created_time TIMESTAMPTZ,
    permalink_url TEXT,
    image_url TEXT,
    raw_json JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_meta_posts_created_time ON meta_posts(created_time DESC);
