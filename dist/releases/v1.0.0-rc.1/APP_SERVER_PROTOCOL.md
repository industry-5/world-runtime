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

## Public API Relationship

- Public HTTP API `v1` is documented in `api/PUBLIC_API_V1.md`.
- Public API `v1` maps to supported App Server methods and is the recommended external integration surface.
- `handle_request` remains supported for internal in-process use and backward compatibility.
