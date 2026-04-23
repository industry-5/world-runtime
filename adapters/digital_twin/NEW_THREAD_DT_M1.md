# DT-M1 - Overlay Positioning, Host-Bound Contract, and Minimal Metadata Wiring

## Objective

Define the overlay-first boundaries for `adapter-digital-twin`, including host-binding expectations for `power_grid` and `city_ops`, without introducing a new stable public API surface.

## Acceptance Highlights

- `adapter-digital-twin` exists on the shared adapter contract
- package-local schemas and default policy exist
- `examples/scenarios/digital-twin-mini/` exists with the host-bound overlay bundle shape
- registry/example/test surfaces recognize the new package
