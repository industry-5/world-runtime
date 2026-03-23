# App Server Protocol v1

## Wire Contract

Requests, responses, and notifications use explicit envelopes.

### Request

- `protocol_version` (required)
- `id` (required)
- `method` (required)
- `params` (optional object)

### Response

- `wire_type=response`
- `protocol_version`
- `compatibility` (`policy`, `server_version`)
- `id`
- `ok`
- `result` (when `ok=true`) or `error` (when `ok=false`)

### Notification

- `wire_type=notification`
- `protocol_version`
- `method`
- `params`

## Compatibility Policy

- Policy: **major-compatible**
- Server protocol version: `1.0`
- Requests are accepted when client/server major versions match.
- Requests with incompatible major versions return `protocol_version_incompatible`.
- Existing direct method entrypoint (`handle_request`) remains supported for backward compatibility.

## Stabilization Guarantees

- Stable method names under v1.
- Error envelope always includes `code` and `message`.
- Event stream entries include both legacy fields (`type`, `payload`) and protocol fields (`wire_type`, `method`, `params`).
- Domain runtime methods are additive and callable via `handle_request` and Public API runtime-call endpoint, including:
  - `world_game.scenario.list`
  - `world_game.session.create`
  - `world_game.session.get`
  - `world_game.session.actor.add`
  - `world_game.session.actor.remove`
  - `world_game.session.actor.list`
  - `world_game.session.stage.get`
  - `world_game.session.stage.set`
  - `world_game.session.stage.advance`
  - `world_game.session.export`
  - `world_game.session.import`
  - `world_game.scenario.load`
  - `world_game.turn.run`
  - `world_game.branch.create`
  - `world_game.branch.compare`
  - `world_game.replay.run`
  - `world_game.network.inspect`
  - `world_game.equity.report`
  - `world_game.proposal.create`
  - `world_game.proposal.update`
  - `world_game.proposal.get`
  - `world_game.proposal.list`
  - `world_game.proposal.submit`
  - `world_game.proposal.adopt`
  - `world_game.proposal.reject`
  - `world_game.annotation.create`
  - `world_game.annotation.list`
  - `world_game.annotation.update`
  - `world_game.annotation.archive`
  - `world_game.provenance.inspect`
  - `world_game.authoring.template.list`
  - `world_game.authoring.draft.create`
  - `world_game.authoring.draft.validate`
  - `world_game.authoring.bundle.publish`
  - `world_game.authoring.bundle.instantiate`

## Public API Relationship

- Public HTTP API `v1` is documented in `api/PUBLIC_API_V1.md`.
- Public API `v1` maps to supported App Server methods and is the recommended external integration surface.
- `handle_request` remains supported for internal in-process use and backward compatibility.
