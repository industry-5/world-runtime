# Playbook: Integration Reference Stacks

## Goal

Validate end-to-end adapter deployment patterns for external ingress/egress systems.

## Command

```bash
make integration-stacks
```

## Procedure

1. Load stack manifests from `infra/integration_stacks/*.json`.
2. Validate profile, adapter, scenario assets, ingress event mappings, and egress action mappings.
3. Build the runtime using the stack's deployment profile.
4. Run adapter policy evaluation against stack scenario proposal.
5. Execute stack smoke query and verify expected query type.
6. Run eval suite for stack-level smoke confidence.
