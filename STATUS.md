# Status

_Last updated: 2026-03-22 (America/Chicago)_

## Current Snapshot

- Release posture: `v1.0.0`
- Public support posture: best-effort
- Primary public focus: runtime core, Public API `/v1`, SDK starter, persistence migrations, extension contracts, and the public supply-network / air-traffic adapter examples

## Included Public Surface

- `adapter-supply-network`
- `adapter-air-traffic`
- App Server protocol
- Public API `/v1`
- Python SDK starter
- Connector and persistence tooling
- Extension scaffolding and compatibility docs

## Validation Baseline

The intended public baseline is:

```bash
make install
make validate
make workflow-quickstart
make api-server
make sdk-example
```

## Notes

- This public export is intentionally narrower than the private development repo.
- Additional adapters, labs, and showcase surfaces may continue to evolve privately before they are promoted into public support.
