# Contributing

Thanks for contributing to World Runtime.

_Documentation note: `README.md` is the front door and `CHANGELOG.md` carries the release narrative for this public export._

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

## Commit and PR Hygiene

- Use clear commit messages.
- Reference related issue(s) when applicable.
- Avoid committing generated artifacts from `tmp/` or `dist/releases/`.

## Code of Conduct

By participating, you agree to follow the repository Code of Conduct in `CODE_OF_CONDUCT.md`.
