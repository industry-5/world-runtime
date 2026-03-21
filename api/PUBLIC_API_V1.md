# World Runtime Public API v1

This is the supported external HTTP surface for World Runtime.

## Versioning and compatibility

- Public API version: `v1`
- Backing App Server protocol: `1.0`
- Compatibility policy: major-compatible (`v1.x` clients remain supported across `v1` server minors)

## Endpoints

- `GET /health` - unauthenticated liveness
- `GET /v1/meta` - API/protocol compatibility metadata
- `POST /v1/runtime/call` - generic method bridge for advanced users
- `POST /v1/sessions` - create runtime session
- `POST /v1/proposals/submit` - submit proposal + policy evaluation
- `POST /v1/simulations/run` - create/run simulation with hypothetical events
- `POST /v1/approvals/respond` - approve/reject/escalate/override an approval request
- `POST /v1/connectors/inbound/run` - run inbound connector flow
- `POST /v1/connectors/outbound/run` - run outbound connector flow
- `GET /v1/observability/telemetry/summary` - observability summary surface

For a first local API run:

```bash
make api-server
make sdk-example
```

Runtime-call domain methods now include world-game flows:

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

## Authentication and configuration

- Local profile: run without bearer auth for local-only development.
- Dev profile: set `WORLD_RUNTIME_API_TOKEN` and send `Authorization: Bearer <token>`.
- API base URL default for local examples: `http://127.0.0.1:8080`.

## Deprecation notes

- `core.app_server.WorldRuntimeAppServer.handle_request` remains supported for internal/in-process usage.
- External clients should prefer Public API `v1` or the SDK surface.
- Breaking public changes require a new API major (`v2`).
