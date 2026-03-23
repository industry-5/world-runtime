CREATE UNIQUE INDEX IF NOT EXISTS idx_events_stream_sequence
ON events(stream_id, sequence);

CREATE INDEX IF NOT EXISTS idx_events_stream_offset
ON events(stream_id, offset);

CREATE INDEX IF NOT EXISTS idx_snapshots_projection_offset
ON snapshots(projection_name, source_event_offset);
