# Security and Trust-Boundary Review

Review date: 2026-04-23 (America/Chicago)
Scope: v1.1.0 release gate / GA cutover

## Findings Register

| ID | Boundary | Severity | Status | Disposition | Owner | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| STB-001 | Connector outbound effect boundary | High | Resolved | Fixed | runtime maintainers | `tests/test_connector_policy_guardrails.py` | Provider-aware deny/approval enforcement and durable decision records verified. |
| STB-002 | Approval actor authorization boundary | High | Resolved | Fixed | runtime maintainers | `tests/test_app_server.py` | Actor capability checks and approval-chain attribution verified. |
| STB-003 | Provenance/audit export boundary | Medium | Resolved | Fixed | runtime maintainers | `tests/test_provenance.py` | Redaction and deterministic fingerprinting preserved for exports. |

## Waivers

No active waivers for the v1.1.0 release gate.
