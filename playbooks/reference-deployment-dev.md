# Playbook: Dev Reference Deployment

## Goal

Run shared development deployment profile with reference backend/provider settings.

## Command

```bash
make deploy-dev
```

## Procedure

1. Load `infra/profiles/dev.profile.json`.
2. Validate reference persistence/LLM configs.
3. Bootstrap runtime and run smoke query.
4. Run eval suite and confirm pass threshold.
5. Use resulting profile as baseline for reproducible dev environments.
