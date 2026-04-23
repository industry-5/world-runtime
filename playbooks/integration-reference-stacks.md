# Playbook: Integration Reference Stacks

## Goal

Validate end-to-end reference stack patterns. This now includes both adapter-facing external integration stacks and the M30 local AI structured extraction stack.

## Command

```bash
make integration-stacks
```

## Procedure

1. Load stack manifests from `infra/integration_stacks/*.json`.
2. Validate the manifest by stack kind:
   - adapter integration stacks validate profile, adapter, scenario assets, ingress mappings, and egress mappings
   - the M30 local AI stack validates managed services, provider bindings, task profiles, smoke fixtures, and eval references
3. Run the stack smoke path using the declared deployment profile or supported runtime-admin surface.
4. Confirm the stack-specific outputs:
   - adapter integration stacks must preserve their reasoning query and connector behavior
   - the M30 local AI stack must reconcile its managed service, preserve routing traces, and produce schema-valid extraction outputs
5. Run stack-level evals when the stack defines them.
