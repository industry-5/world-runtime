# Playbook: Operator Observability Diagnostics

## Goal

Generate structured telemetry summaries and a dashboard artifact for runtime diagnostics.

## Command

```bash
make observability
make provenance-audit
```

## Procedure

1. Run a representative workflow (default: quickstart) through the diagnostics script.
2. Review generated summary and dashboard files in `tmp/diagnostics/`.
3. Inspect dashboard cards (`events`, `traces`, `errors`, `avg_trace_ms`) and severity/component breakdowns.
4. Use `slow_traces` output to identify runtime hotspots for follow-up.
5. For provenance-grade review, inspect `tmp/diagnostics/audit_export.latest.json` for redacted decision evidence, stage linkage, and deterministic fingerprinting.
