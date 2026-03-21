# WG-P6 Cutover and Legacy Retirement Decision

Date: 2026-03-14 (America/Chicago)
Milestone: WG-P6 - Hardening, cutover, and legacy containment

## Decision

`labs/world_game_studio_next` is the primary World Game studio surface for demos, workshops, and ongoing feature work.

`labs/world_game_studio` was initially retained as a contained legacy baseline during WG-P6 stabilization and has since been retired after Studio Next stabilization completed.

## Scope of legacy containment

- no new feature development in `labs/world_game_studio`
- legacy removal is allowed once Studio Next stabilization and docs cutover are complete
- runtime/domain truth remains in `adapters/world_game`
- all new studio UX, hardening, and workflow investment goes to `labs/world_game_studio_next`

## Why this decision

- WG-P0 through WG-P6 goals are now implemented in studio-next, including:
  - Dymaxion-centered planning workflow
  - compare/replay/provenance workflows
  - facilitation and collaboration durability controls
  - accessibility and onboarding hardening
- temporary legacy availability lowered operational risk during stabilization without splitting product direction

## Compatibility expectations

- runtime method support remains identical because both studios call `world_game.*` methods
- studio-next is preferred for active demonstrations and contributor onboarding
- legacy is now retired, with historical references preserved only where they document past milestones

## Retirement outcome

Legacy retirement is now complete after:

- browser interaction coverage landed for studio-next onboarding and facilitation flows
- WG-P10 stabilization completed
- current repo docs and tests moved to Studio Next as the only active showcase UI path
