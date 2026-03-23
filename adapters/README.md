# Domain Adapters

This directory contains domain-specific adapter packages that extend the domain-neutral kernel.

Current adapters:

- `adapter-supply-network`
- `adapter-air-traffic`
- `adapter-world-game`

Each adapter provides:

- adapter-level schemas
- adapter-level default policy
- scenario binding to `examples/scenarios/*-mini`
- a stable adapter contract via `adapters/base.py`
