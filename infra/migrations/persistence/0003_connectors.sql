CREATE TABLE IF NOT EXISTS connector_idempotency (
  key TEXT PRIMARY KEY,
  direction TEXT NOT NULL,
  connector_id TEXT NOT NULL,
  result_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS connector_dead_letters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dead_letter_id TEXT NOT NULL UNIQUE,
  connector_id TEXT NOT NULL,
  direction TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  reason TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  attempts INTEGER NOT NULL,
  last_error TEXT NOT NULL,
  created_at TEXT NOT NULL,
  replay_status TEXT,
  replayed_at TEXT,
  replay_result_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_connector_dead_letters_lookup
ON connector_dead_letters(connector_id, direction, created_at);
