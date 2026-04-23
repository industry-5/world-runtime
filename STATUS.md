# Status

_Last updated: 2026-04-23 (America/Chicago)_

## Current Snapshot

- Release posture: `v1.1.0`
- Public support posture: best-effort
- Primary public focus: runtime core, Public API `/v1`, SDK starter, supported package serve entrypoints, additive runtime-admin surfaces, persistence migrations, extension contracts, and the public domain adapter scenario program

## Included Public Surface

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
- `adapter-digital-twin`
- public adapter program docs under `adapters/`
- App Server protocol
- Public API `/v1`
- Python SDK starter
- Connector and persistence tooling
- Extension scaffolding and compatibility docs

## Public Adapter Program

- Program status: `DA-M1 through DA-M9 complete`
- Current implemented standalone proof paths: `adapter-supply-network`, `adapter-air-traffic`, `adapter-semantic-system`, `adapter-power-grid`, `adapter-city-ops`, `adapter-lab-science`, `adapter-market-micro`, `adapter-multiplayer-game`, `adapter-autonomous-vehicle`, `adapter-multi-agent-ai`, and `adapter-open-agent-world`
- Implemented overlay track: `adapter-digital-twin` (host-bound across `power_grid` and `city_ops`)

## Validation Baseline

The intended public baseline is:

```bash
make install
make validate
make workflow-quickstart
python -m world_runtime serve --profile local
make sdk-example
```

## Notes

- This public export is intentionally narrower than the private development repo.
- World Runtime 1.1.0 adds package-hosted consumption, managed local services, provider/task routing, runtime-admin inspection plus bounded reconcile, and a local AI structured-extraction reference stack.
- Future adapter additions should be introduced as explicit public promotions rather than implied.
