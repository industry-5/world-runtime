# v1.0 Release Readiness Checklist

Milestone: M25 (v1.0 release candidate gate)

## Go/No-Go Criteria

- [x] Baseline command bundle is green on the release candidate commit.
- [x] Domain/eval/provenance/performance/recovery checks are green and reproducible.
- [x] Security and trust-boundary findings are either resolved or explicitly waived.
- [x] Release artifacts are reproducible and include required runtime, protocol, and extension onboarding assets.
- [x] Stability/support commitments are published for protocol, API/SDK, migrations, and extension contracts.

## Aggregate RC Gate Matrix

| Group | Command | Purpose |
| --- | --- | --- |
| Baseline | `make test` | Full unit/integration suite gate |
| Baseline | `make validate` | Schema + test gate |
| Milestone | `make evals` | Eval harness confidence gate |
| Milestone | `make benchmark` | Performance envelope evidence |
| Milestone | `make recovery-check` | Recovery + migration-volume evidence |
| Milestone | `make provenance-audit` | Provenance/export redaction gate |
| Milestone | `make release-artifacts RELEASE_VERSION=1.0.0-rc.1` | Tagged RC artifact build |
| Regression | `make examples` | Scenario coherence regression |
| Regression | `make adapters` | Adapter contract regression |
| Regression | `make connectors` | Connector runtime regression |
| Regression | `make connector-plugins` | Connector plugin contract/state regression |
| Regression | `make integration-stacks` | Integration stack regression |
| Regression | `make protocol-compat` | Protocol compatibility contract gate |
| Regression | `make public-api-compat` | Public API/SDK compatibility gate |
| Regression | `make extension-contracts` | Extension seam stability gate |

## Evidence Artifacts

- `tmp/diagnostics/m25_release_candidate_gate.latest.json`
- `tmp/diagnostics/m23_benchmarks.latest.json`
- `tmp/diagnostics/m23_recovery.latest.json`
- `tmp/diagnostics/audit_export.latest.json`
- `dist/releases/v1.0.0-rc.1/`
- `dist/releases/v1.0.0-rc.1.tar.gz`
