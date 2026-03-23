CREATE TABLE IF NOT EXISTS events (
  offset INTEGER PRIMARY KEY,
  stream_id TEXT NOT NULL,
  sequence INTEGER NOT NULL,
  event_json TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  projection_name TEXT NOT NULL,
  source_event_offset INTEGER NOT NULL,
  state_json TEXT NOT NULL,
  metadata_json TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
