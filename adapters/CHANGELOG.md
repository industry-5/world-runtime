# Public Domain Adapter Program Changelog

This file records milestone closeout narrative for the public domain adapter scenario program.

## Unreleased

### DA-M9 - Promotion hardening and public-export readiness

Added:

- public-export rewrite regression coverage in `tests/test_adapters.py`

Changed:

- package-local `M4` ledgers now close across every in-scope public track
- series docs, root rollups, `docs/what-you-can-build.*`, and public-export rewrite text now agree on the downstream-promotion-ready portfolio posture

### DA-M8 - Digital twin overlay

Added:

- the first runtime-authoritative `digital_twin` overlay slice, host-binding metadata, public overlay bundle, playbook, and targeted validation through local `DT-M3`
- package-local milestone briefs needed to advance `digital_twin` to its next package milestone

Changed:

- series state, package docs, and touched root/docs rollups now advance together to `DA-M9`
- shared discovery, the generic non-overlay scenario-bundle validation, and the explicit overlay boundary stayed intact while the public portfolio gained its first implemented overlay track

### DA-M7 - Agent coordination and governance

Added:

- the first runtime-authoritative `multi_agent_ai` and `open_agent_world` adapter slices, public scenario bundles, playbooks, and targeted validation through local `MA-M3` and `OAW-M3`
- package-local milestone briefs needed to advance `multi_agent_ai` and `open_agent_world` to their next package milestones

Changed:

- series state, package docs, and touched root/docs rollups now advance together to `DA-M8`
- shared discovery and generic non-overlay scenario-bundle validation stayed intact while the public portfolio expanded from nine to eleven implemented proof paths

### DA-M6 - Concurrency and motion safety

Added:

- the first runtime-authoritative `multiplayer_game` and `autonomous_vehicle` adapter slices, public scenario bundles, playbooks, and targeted validation through local `MPG-M3` and `AV-M3`
- package-local milestone briefs needed to advance `multiplayer_game` and `autonomous_vehicle` to their next package milestones

Changed:

- series state, package docs, and touched root/docs rollups now advance together to `DA-M7`
- shared discovery and generic non-overlay scenario-bundle validation stayed intact while the public portfolio expanded from seven to nine implemented proof paths

### DA-M5 - Regulated and market pressure

Added:

- the first runtime-authoritative `lab_science` and `market_micro` adapter slices, public scenario bundles, playbooks, and targeted validation through local `LS-M3` and `MM-M3`
- package-local milestone briefs needed to advance `lab_science` and `market_micro` to their next package milestones

Changed:

- series state, package docs, and touched root/docs rollups now advance together to `DA-M6`
- shared discovery and generic non-overlay scenario-bundle validation stayed intact while the public portfolio expanded from five to seven implemented proof paths

### DA-M4 - Infrastructure and civic coordination

Added:

- the first runtime-authoritative `power_grid` and `city_ops` adapter slices, public scenario bundles, playbooks, and targeted validation through local `PG-M3` and `CO-M3`
- package-local milestone briefs needed to advance `power_grid` and `city_ops` to their next package milestones

Changed:

- series state, package docs, and touched root/docs rollups now advance together to `DA-M5`
- shared discovery and generic non-overlay scenario-bundle validation stayed intact while the public portfolio expanded from three to five implemented proof paths

### DA-M3 - Foundation and legacy parity

Added:

- the first runtime-authoritative `semantic_system` adapter slice, public scenario bundle, playbook, and targeted validation through local `SS-M3`
- package-local milestone briefs needed to advance `air_traffic`, `supply_network`, and `semantic_system` to their next package milestones

Changed:

- `air_traffic` and `supply_network` package docs now describe implemented local `M3` slices instead of legacy `M1` carryovers
- series state, package docs, and touched root/docs rollups now advance together to `DA-M4`
- shared discovery and generic non-overlay scenario-bundle validation stayed intact while the foundation trio expanded

### DA-M2 - Shared adapter standards and generic validation

Added:

- shared public-track metadata, package checklist validation, and generic scenario-bundle helpers in `adapters/public_program.py`
- scenario-bundle `README.md` files for the implemented public proof paths in `examples/scenarios/supply-network-mini/` and `examples/scenarios/air-traffic-mini/`
- generic public scenario-bundle validation coverage in `scripts/check_examples.py`, `tests/test_adapters.py`, and `tests/test_scenario_bundles.py`

Changed:

- default registry discovery for implemented public tracks now flows from shared program metadata instead of hard-coded legacy imports
- adapter-program docs now define the standard non-overlay public scenario-bundle contract and package checklist while preserving richer adapter-local supplemental proofs
- series state advances to `DA-M3`

### DA-M1 - Program bootstrap and public-doc reset

Added:

- series-level governance docs in `adapters/`
- package-local governance docs for every in-scope public adapter track
- normalized package-doc shape for `adapters/air_traffic` and `adapters/supply_network`
- the semantic-coherence public naming standard: `semantic_system`

Changed:

- touched root/docs rollups now frame the public adapter portfolio as the primary public domain-adapter scenario program
- touched public-facing docs now mark `supply_ops` and `world_game` as internal and out-of-program for this series
- public-export rewrite text now matches the refreshed adapter-portfolio story
