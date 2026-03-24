# Public Domain Adapter Program

_Last updated: 2026-03-23 (America/Chicago)_

This directory now carries the public domain adapter scenario program for `world-runtime`.

The public export keeps the runtime-facing package docs and portfolio story, but omits the internal milestone ledgers and thread handoff materials used to build the series.

## In-Scope Public Tracks

- `adapter-supply-network` (`SN`)
- `adapter-air-traffic` (`AT`)
- `adapter-semantic-system` (`SS`)
- `adapter-power-grid` (`PG`)
- `adapter-city-ops` (`CO`)
- `adapter-lab-science` (`LS`)
- `adapter-market-micro` (`MM`)
- `adapter-multiplayer-game` (`MPG`)
- `adapter-autonomous-vehicle` (`AV`)
- `adapter-multi-agent-ai` (`MA`)
- `adapter-open-agent-world` (`OAW`)
- `adapter-digital-twin` (`DT`)

`adapter-digital-twin` is the current overlay exception: it is host-bound, validated first on `power_grid`, then `city_ops`, and should still not be treated as a standalone showcase world.

## Working Defaults

- Root docs stay rollup-only.
- `docs/what-you-can-build.md` is the primary public portfolio narrative.
- Package-local README files are the public-facing summary for each promoted track.
- No new stable App Server, HTTP API, or SDK surfaces are implied by this series unless a later milestone explicitly declares them.
