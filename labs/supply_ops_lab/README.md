# Supply Ops Lab

`labs/supply_ops_lab` is the thin runnable `SO-P2` operator-facing Supply Ops lab surface, hardened through `SO-P3`, with a bounded `SO-P4` Decision Explorer concept surface now landed in parallel.

## Purpose

- provide a lightweight operator/demo surface for the Supply Ops adapter
- demonstrate the intended flow:
  - inbound ERP/WMS-style signal
  - translated proposal
  - policy gate
  - simulation before action
  - approval/decision outcome
  - readable result timeline and telemetry summary

## Current State

- current state: `SO-P4` is complete while preserving the truthful `SO-P3` operator/reference route
- the lab now ships `index.html`, `decision-explorer.html`, `styles.css`, `app.js`, `decision-explorer.js`, `server.py`, and `tests/labs/test_supply_ops_lab.py`
- the supported runnable path remains intentionally narrow and honest:
  - four fixture-backed presets for `allow`, `warn`, `require_approval`, and `deny`
  - readable proposal, policy, replay, simulation, and timeline surfaces
  - package-backed scenario evidence references that keep execution-evidence UI out of required scope
- the lab is now planning around two surfaces:
  - the existing `SO-P3` preset-driven operator/reference path
  - the landed `SO-P4` Decision Explorer parallel concept surface
- the browser remains thin and render-only; the lab server owns Supply Ops translation, policy previewing, replay/simulation assembly, startup/run guidance, and stable upstream session/proposal wiring
- `SO-P3` adds:
  - explicit loading, empty, and bootstrap/run error handling for the supported UI path
  - built-in startup commands, smoke checks, and demo walkthrough guidance
  - targeted HTTP smoke coverage for `/health`, `/api/supply-ops/bootstrap`, and `/api/supply-ops/run`
- `SO-P4` now adds a bounded parallel pitch/demo route without replacing the truthful `SO-P3` path or changing stable runtime/public API commitments:
  - `/decision-explorer` serves the separate concept page
  - `/api/supply-ops/decision-explorer/bootstrap` and `/api/supply-ops/decision-explorer/evaluate` provide the lab-only comparison contract
  - the concept route renders 1 commitment, 3 proposals, and 2 plans with explicit truth/provenance notes
  - default weights pick Plan A and service-heavy weights flip to Plan B
- connector-ingress UI, execution-evidence UI, and broader operator/demo expansion remain deferred outside the explicitly bounded `SO-P4` scope

## Boundaries

- this lab should remain thin relative to runtime logic
- it should use existing stable HTTP endpoints only
- it should not add new domain-specific runtime methods in v1
- it should depend on `adapter-supply-ops` as the domain track, but should not reimplement translator, simulation, or policy logic in frontend code
- it should not require connector-ingress or execution-evidence UI dependencies in `SO-P1`, `SO-P2`, `SO-P3`, or the first `SO-P4` pass
- it should stay honest about the current server boundary: replay/simulation/timeline storytelling is assembled server-side because the stock upstream public API bootstrap is not seeded with Supply Ops baseline events
- it should stay honest about authority: the runtime and Supply Ops package remain the source of truth, while the lab is a demo/operator surface over stable public HTTP endpoints
- any `SO-P4` concept-layer comparison payload must be labeled honestly with provenance/truth notes rather than represented as a native stable runtime comparison API

## Working Defaults

- lab package path: `labs/supply_ops_lab`
- domain package dependency: `adapters/supply_ops`
- current runnable asset shape:
  - `index.html`
  - `styles.css`
  - `app.js`
  - `server.py`
- current targeted lab test path: `tests/labs/test_supply_ops_lab.py`
- current runnable pass depends on the documented Supply Ops `SO-M3` flow rather than any newer in-flight adapter slices
- current default reviewed flow fixture: `require_approval_high_expedite`

## Current Runnable Slice

- static shell plus standalone server under `labs/supply_ops_lab/`
- `/api/v1/*` proxy path to the upstream public HTTP API
- `/decision-explorer` parallel concept route for the lab-authored comparison surface
- preset-driven run flow that renders:
  - translated proposal plus readable proposal summary
  - upstream policy gate result with approval posture
  - replay and simulation summaries
  - operator-facing timeline flow
  - package-backed scenario evidence references
- Decision Explorer flow that renders:
  - one curated commitment anchored to the reviewed Supply Ops scenario
  - three proposals assembled into two plans by the server
  - server-authored comparison scores, why-selected/why-not reasoning, and policy-shift notes

## Quick Start

Start the supported runnable path with:

- `python3 -m api.http_server --host 127.0.0.1 --port 8080`
- `python3 labs/supply_ops_lab/server.py --host 127.0.0.1 --port 8094 --upstream http://127.0.0.1:8080`
- open `http://127.0.0.1:8094` for the preserved operator route
- open `http://127.0.0.1:8094/decision-explorer` for the bounded concept route
- optional health check: `curl -sS http://127.0.0.1:8094/health`

## Demo Walkthrough

1. Load the lab and confirm the boundary notes: the browser is render-only and the server remains the Supply Ops/runtime-facing authority.
2. Click through the four presets to inspect translated proposal, policy preview, replay summary, simulation summary, and timeline surfaces before running anything.
3. Run the selected preset to exercise the stable upstream session/proposal path and compare the executed policy posture to the previewed result.
4. Visit `/decision-explorer` to inspect the parallel concept route and verify that the comparison payload is clearly labeled as lab-authored rather than a stable runtime API.
5. Use the scenario artifact list as supporting evidence only; connector-ingress UI and execution-evidence UI remain out of scope for the supported lab demo.

## Smoke Validation

Use the targeted lab bundle when touching this surface:

- `find labs/supply_ops_lab -maxdepth 1 -type f | sort`
- `env PYTHONPYCACHEPREFIX=/tmp/world-runtime-pycache python3 -m py_compile labs/supply_ops_lab/server.py`
- `python3 -m pytest -q tests/labs/test_supply_ops_lab.py`

This remains a small coherent runnable slice. `SO-P3` hardens the supported path and makes it easier to boot and demo, while `SO-P4` adds a bounded parallel Decision Explorer concept route without widening into connector-ingress UI, execution-evidence UI, or broader runtime/API commitments.

Internal milestone ledgers and thread handoff prompts are intentionally omitted from this public export.
