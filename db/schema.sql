CREATE TABLE IF NOT EXISTS summaries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT NOT NULL,
  repos TEXT[] NOT NULL,
  days INTEGER NOT NULL,
  display TEXT NOT NULL,
  summary TEXT NOT NULL,
  generated_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_summaries_username ON summaries(username);
CREATE INDEX IF NOT EXISTS idx_summaries_generated_at ON summaries(generated_at DESC);
