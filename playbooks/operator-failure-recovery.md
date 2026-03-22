# Playbook: Operator Failure Recovery

## Goal

Evaluate a recovery path after an operational disruption.

## Command

```bash
make workflow-failure
```

## Procedure

1. Create an isolated simulation branch.
2. Apply hypothetical recovery event(s).
3. Run simulation and inspect changed state paths.
4. Use returned recommendation for proposal review.
