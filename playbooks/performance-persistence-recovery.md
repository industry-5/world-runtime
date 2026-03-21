# Playbook: Performance, Persistence, and Recovery Hardening

## Goal

Produce reproducible M23 evidence for throughput envelopes, restart/idempotency correctness, migration volume behavior, and backup/restore viability.

## Commands

```bash
make benchmark
make recovery-check
make m23-validate
```

## Artifacts

- `tmp/diagnostics/m23_benchmarks.latest.json`
- `tmp/diagnostics/m23_recovery.latest.json`

## Procedure

1. Run `make benchmark` and confirm `benchmark_status=passed`.
2. Review profile-specific metrics under `results.local` and `results.dev`.
3. Run `make recovery-check` and confirm `check_status=passed`.
4. Verify `restart_idempotency.second_status=duplicate` in recovery output.
5. Verify backup/restore table counts match and migration second run has `applied=[]`.
6. Before merge, run `make m23-validate` plus baseline and broader regression commands.

## Notes

- Benchmark reproducibility is defined by fixed workload parameters and `workload_fingerprint`.
- Performance values are machine-dependent; compare envelopes by profile and run date.
- Recovery checks use isolated `tmp/m23/` databases to avoid mutating profile runtime state.
