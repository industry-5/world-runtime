# Public Domain Adapter Program Roadmap

_Last updated: 2026-03-23 (America/Chicago)_

## Goal

Build a coherent public-facing portfolio of compact domain adapter scenario packages inside `world-runtime` that can eventually be promoted downstream to the public `world-runtime` repository.

## Milestone Format

Each series milestone should leave the program more legible, more uniform, and easier to extend across multiple parallel threads.

Every milestone should update:

- series docs in `adapters/`
- touched package-local docs
- root rollup docs only when public positioning changes

## Working Defaults

- Treat `adapters/ROADMAP.md` as the strategy source for the public adapter program.
- Treat `adapters/STATUS.md` as the current execution ledger.
- Keep detailed milestone history in package-local docs.
- Keep `supply_ops` and `world_game` out of this program even though they remain in the repository.
- Use `semantic_system` as the semantic-coherence public track name; do not use `narrative_world` in new program materials.

## Milestones

### DA-M1 - Program bootstrap and public-doc reset

Status: Completed (2026-03-23)

Objective:

- establish the series-level governance docs, seed package-local governance docs for every in-scope track, normalize `air_traffic` and `supply_network` to package-doc parity, and reset touched public-facing docs around the public adapter portfolio

Delivered:

- series docs in `adapters/`
- package-local governance docs for all in-scope public tracks
- normalized package-doc shape for `air_traffic` and `supply_network`
- refreshed root/docs rollups for the public adapter portfolio
- explicit out-of-program framing for `supply_ops` and `world_game`

### DA-M2 - Shared adapter standards and generic validation

Status: Completed (2026-03-23)

Objective:

- generalize registry/example/test discovery, define the standard public scenario-bundle contract and package checklist, and preserve adapter-local supplemental proofs where generic checks are insufficient

Delivered:

- shared public-track metadata and checklist discovery in `adapters/public_program.py`
- default registry discovery for implemented public tracks no longer hard-coded to the original legacy pair
- generic non-overlay public scenario-bundle validation in scripts and tests
- preserved richer adapter-local proof surfaces on top of the shared baseline, including the air-traffic supplemental proposal path

Acceptance highlights:

- shared discovery is not hard-coded to only the legacy adapters
- scenario-bundle validation has a documented generic baseline
- richer adapters can still layer adapter-specific validation on top of that baseline

### DA-M3 - Foundation and legacy parity

Status: Completed (2026-03-23)

Objective:

- bring `air_traffic` and `supply_network` to full package parity and implement `semantic_system` through local `M1-M3`

Delivered:

- `air_traffic` and `supply_network` now describe their implemented public slices through local `M3` instead of remaining legacy `M1` carryovers
- `semantic_system` now has a runtime-authoritative adapter, schemas, policy, scenario bundle, playbook, and targeted validation through local `SS-M3`
- shared public adapter discovery and the generic non-overlay scenario-bundle baseline stayed green while the foundation trio expanded

Acceptance highlights:

- legacy public proof paths now have fuller package-local parity
- `adapter-semantic-system` landed as the third implemented public proof path
- touched series/package/root docs advance together to `DA-M4`

### DA-M4 - Infrastructure and civic coordination

Status: Completed (2026-03-23)

Objective:

- implement `power_grid` and `city_ops` through local `M1-M3`

Delivered:

- `power_grid` and `city_ops` now have runtime-authoritative adapters, schemas, policies, scenario bundles, playbooks, and targeted validation through local `PG-M3` and `CO-M3`
- shared public adapter discovery and the generic non-overlay scenario-bundle baseline stayed green while the public portfolio expanded to five implemented proof paths

Acceptance highlights:

- `adapter-power-grid` landed as the fourth implemented public proof path
- `adapter-city-ops` landed as the fifth implemented public proof path
- touched series/package/root docs advance together to `DA-M5`

### DA-M5 - Regulated and market pressure

Status: Completed (2026-03-23)

Objective:

- implement `lab_science` and `market_micro` through local `M1-M3`

Delivered:

- `lab_science` and `market_micro` now have runtime-authoritative adapters, schemas, policies, scenario bundles, playbooks, and targeted validation through local `LS-M3` and `MM-M3`
- shared public adapter discovery and the generic non-overlay scenario-bundle baseline stayed green while the public portfolio expanded to seven implemented proof paths

Acceptance highlights:

- `adapter-lab-science` landed as the sixth implemented public proof path
- `adapter-market-micro` landed as the seventh implemented public proof path
- touched series/package/root docs advance together to `DA-M6`

### DA-M6 - Concurrency and motion safety

Status: Completed (2026-03-23)

Objective:

- implement `multiplayer_game` and `autonomous_vehicle` through local `M1-M3`

Delivered:

- `multiplayer_game` and `autonomous_vehicle` now have runtime-authoritative adapters, schemas, policies, scenario bundles, playbooks, and targeted validation through local `MPG-M3` and `AV-M3`
- shared public adapter discovery and the generic non-overlay scenario-bundle baseline stayed green while the public portfolio expanded to nine implemented proof paths

Acceptance highlights:

- `adapter-multiplayer-game` landed as the eighth implemented public proof path
- `adapter-autonomous-vehicle` landed as the ninth implemented public proof path
- touched series/package/root docs advance together to `DA-M7`

### DA-M7 - Agent coordination and governance

Status: Completed (2026-03-23)

Objective:

- implement `multi_agent_ai` and `open_agent_world` through local `M1-M3`

Delivered:

- `multi_agent_ai` and `open_agent_world` now have runtime-authoritative adapters, schemas, policies, scenario bundles, playbooks, and targeted validation through local `MA-M3` and `OAW-M3`
- shared public adapter discovery and the generic non-overlay scenario-bundle baseline stayed green while the public portfolio expanded to eleven implemented proof paths

Acceptance highlights:

- `adapter-multi-agent-ai` landed as the tenth implemented public proof path
- `adapter-open-agent-world` landed as the eleventh implemented public proof path
- touched series/package/root docs advance together to `DA-M8`

### DA-M8 - Digital twin overlay

Status: Completed (2026-03-23)

Objective:

- implement `adapter-digital-twin` as a host-bound overlay track, first against `power_grid`, then `city_ops`

Delivered:

- `adapter-digital-twin` now has a runtime-authoritative overlay adapter, schemas, policy, host-binding metadata, scenario bundle, playbook, and targeted validation through local `DT-M3`
- the overlay proof is established first against `power_grid` and then extended to `city_ops` without turning the package into a standalone showcase domain
- shared public adapter discovery, the generic non-overlay scenario-bundle baseline, and the explicit overlay boundary stayed green while the public portfolio gained its first implemented overlay track

### DA-M9 - Promotion hardening and public-export readiness

Status: Completed (2026-03-23)

Objective:

- run the final public adapter audit across package docs, root rollups, `docs/what-you-can-build.*`, validation surfaces, and public-export wording so the portfolio is ready for downstream promotion

Delivered:

- final public audit closed across package-local `M4` docs, series docs, root rollups, `docs/what-you-can-build.*`, and public-export rewrites
- package-local promotion-hardening closeout now lands across every in-scope public track without widening stable App Server, HTTP API, or SDK surfaces
- public-export wording and validation now match the full eleven-track-plus-overlay portfolio posture

## Post-Series Note

- `DA-M1` through `DA-M9` are complete.
- Further public-adapter work should be scoped as downstream promotion/export follow-through or a newly declared series milestone.

## Package Track Summary

- Foundation and legacy: `supply_network`, `air_traffic`, `semantic_system`
- Infrastructure and civic: `power_grid`, `city_ops`
- Regulated and market: `lab_science`, `market_micro`
- Concurrency and safety: `multiplayer_game`, `autonomous_vehicle`
- Agent governance: `multi_agent_ai`, `open_agent_world`
- Overlay track: `digital_twin`

## Milestone Advancement Discipline

- Every milestone closeout updates `STATUS.md`, `CHANGELOG.md`, `ROADMAP.md`, the kickoff prompt, and the next active brief together when a next milestone exists.
- Package-local docs advance alongside the series docs for any touched track.
- Root docs remain concise and rollup-focused even when package-local milestones get deeper.
