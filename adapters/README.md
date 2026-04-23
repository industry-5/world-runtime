# Public Domain Adapter Program

_Last updated: 2026-04-23 (America/Chicago)_

This directory carries the public domain adapter program for `world-runtime`.

The public export keeps the runtime-facing package docs and portfolio story while leaving private planning and handoff material out of the release.

## Current Public Portfolio

- standalone proof paths:
  - `adapter-supply-network`
  - `adapter-air-traffic`
  - `adapter-semantic-system`
  - `adapter-power-grid`
  - `adapter-city-ops`
  - `adapter-lab-science`
  - `adapter-market-micro`
  - `adapter-multiplayer-game`
  - `adapter-autonomous-vehicle`
  - `adapter-multi-agent-ai`
  - `adapter-open-agent-world`
- implemented overlay track:
  - `adapter-digital-twin`

## Out-Of-Program Tracks

- `adapter-supply-ops`
- `adapter-world-game`

These packages remain in the repository, but they are not part of the public adapter portfolio described here.

## Shared Public Package Shape

Every in-scope package keeps the same public-facing rollups:

- `README.md`
- `ROADMAP.md`
- `STATUS.md`
- `CHANGELOG.md`

The standard non-overlay public scenario-bundle contract is:

- `README.md`
- `entities.json`
- `relationships.json`
- `events.json`
- `proposal.json`
- `decision.json`
- `simulation.json`
- `policy.json`
- `rule.json`
- `projection.json`

The overlay bundle used by `adapter-digital-twin` keeps that same runtime artifact set and adds:

- `host_bindings.json`

## Working Defaults

- Root docs stay rollup-only.
- `docs/what-you-can-build.md` is the primary public portfolio narrative.
- Package-local docs are the source of truth for package-specific usage, boundaries, and validation paths.
- No new stable App Server, HTTP API, or SDK surfaces are implied by the adapter portfolio by itself.
