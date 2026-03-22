# Playbook: Local Reference Deployment

## Goal

Start a reproducible local deployment profile without changing code.

## Command

```bash
make deploy-local
```

## Procedure

1. Load `infra/profiles/local.profile.json`.
2. Validate persistence and LLM config paths.
3. Bootstrap adapters and scenario events into runtime.
4. Run session/task smoke query and eval suite.
5. Confirm `task_status=completed` and `eval_status=passed`.
