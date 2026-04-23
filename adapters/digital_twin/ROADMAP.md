# Digital Twin Public Adapter Roadmap

_Last updated: 2026-03-23 (America/Chicago)_

## Goal

Establish `adapter-digital-twin` as the host-bound overlay track for the public adapter program rather than as a standalone showcase domain.

## Milestones

### DT-M0 - Bootstrap and hygiene

Status: Completed (2026-03-23)

### DT-M1 - Overlay positioning, host-bound contract, and minimal metadata wiring

Status: Completed (2026-03-23)

Objective:

- define the overlay-first boundaries and the minimum host-binding contract without inventing a new stable public API

Delivered:

- `adapter-digital-twin` now exists on the shared adapter contract with package-local schemas, default policy, and overlay bundle metadata
- `digital-twin-mini` now carries the host-bound runtime artifact set and explicit `host_bindings.json` support
- registry/example/test surfaces recognize the package as an implemented public overlay track

### DT-M2 - Power-grid overlay proof

Status: Completed (2026-03-23)

Objective:

- prove the twin layer first against `power_grid`

Delivered:

- `host_bindings.json` now records the first overlay proof against `adapter-power-grid`
- `overlay_options.json` and `tests/test_digital_twin_domain.py` validate deny/allow/require-approval behavior around the power-grid-first proof path

### DT-M3 - City-ops overlay expansion and docs completion

Status: Completed (2026-03-23)

Objective:

- extend the twin layer to `city_ops` and complete package docs/playbook parity

Delivered:

- the host-bound overlay path now extends from `power_grid` into `city_ops` without turning the package into a standalone showcase domain
- replay/simulation artifacts, playbook guidance, and package docs are now aligned around the implemented public overlay slice

### DT-M4 - Promotion hardening

Status: Completed (2026-03-23)

Objective:

- harden the overlay package for downstream public promotion readiness

Delivered:

- package docs, scenario README/playbook guidance, and validation posture were audited for downstream public promotion readiness
- package-local current-state docs now record the completed `DT-M4` hardening pass without widening stable App Server, HTTP API, or SDK surfaces

## Package Notes

- The overlay package is now promotion-hardened through `DT-M4`; future work should stay host-bound and be scoped as post-promotion follow-through or a newly declared milestone.
- Root docs should stay rollup-only while package-local docs carry milestone detail.
