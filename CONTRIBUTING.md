# Contributing

Thanks for contributing to World Runtime.

_Documentation note: `README.md` is the front door, `STATUS.md` is the current-state operational snapshot, `CHANGELOG.md` is the release narrative, and `ROADMAP.md` is the strategic plus historical milestone record._

## Public Collaboration Posture

- Issues are open
- Pull requests are welcome
- Public support is best-effort
- Maintainers may decline changes that do not fit project direction, supported surfaces, or current support capacity

## Development Setup

1. Install dependencies:
   - `make install`
2. Run validation:
   - `make validate`
3. Run full CI gate before opening a PR:
   - `make ci-gate`

## Pull Request Expectations

- Keep changes focused and scoped.
- Add or update tests for behavioral changes.
- Update docs when public behavior or workflows change.
- Ensure `make m25-validate` passes for release-critical changes.
- Expect maintainer review and final merge decisions to be discretionary.

## Documentation Maintenance

- Update `STATUS.md` when the current repo truth changes: current phase, supported workflow surface, command baseline, recent milestone completion summary, or validation evidence.
- Update `CHANGELOG.md` when a change materially affects the release narrative, tagged release contents, or post-RC/GA stabilization story.
- Update `ROADMAP.md` when strategy, milestone sequencing, milestone framing, or preserved historical roadmap context changes.
- Keep package-local milestone depth in package-local docs such as `adapters/world_game/ROADMAP.md` and `adapters/world_game/STATUS.md` unless the change affects root-level strategy or release posture.

## Commit and PR Hygiene

- Use clear commit messages.
- Reference related issue(s) when applicable.
- Avoid committing generated artifacts from `tmp/` or `dist/releases/`.

## Code of Conduct

By participating, you agree to follow the repository Code of Conduct in
`CODE_OF_CONDUCT.md`.
