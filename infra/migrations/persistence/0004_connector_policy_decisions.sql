CREATE TABLE IF NOT EXISTS connector_policy_decisions (
  decision_id TEXT PRIMARY KEY,
  connector_id TEXT NOT NULL,
  direction TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  final_outcome TEXT NOT NULL,
  status TEXT NOT NULL,
  provider TEXT,
  source TEXT,
  approval_id TEXT,
  policy_report_json TEXT NOT NULL,
  execution_result_json TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_connector_policy_decisions_lookup
ON connector_policy_decisions(connector_id, direction, created_at);
