# Playbook: Operator Quickstart

## Goal

Run a first operator workflow without editing runtime internals.

## Fast Path

```bash
make workflow-quickstart
```

If you want the supported HTTP + SDK surface after that:

```bash
python -m world_runtime serve --profile local
make sdk-example
```

## Procedure

1. Start with the default adapter (`adapter-supply-network`).
2. Run quickstart command.
3. Review returned reasoning summary and generated draft proposal.
4. Inspect emitted task events for auditability.
5. For high-constraint workflows, run `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-air-traffic`.
6. For external integration smoke checks, run API + SDK commands and verify a session plus proposal policy result are returned.
