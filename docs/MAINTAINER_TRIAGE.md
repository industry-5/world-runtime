# Maintainer Triage Guide

This guide is for maintainers running the public `world-runtime` repository.

## Public Posture

- Repository visibility: public
- Collaboration posture: Issues open, PRs welcome
- Support posture: best-effort
- Owning company: `INDUSTRY 5, Inc.`

## Response Targets

- New public issue: acknowledge or disposition within 7 calendar days when possible
- New pull request: acknowledge within 7 calendar days when possible
- Security reports: follow `SECURITY.md` response targets
- Conduct reports: acknowledge privately as soon as practical

These are target behaviors, not guaranteed SLAs.

## Default Labels

Use a small starter label set:

- `bug`
- `documentation`
- `feature-request`
- `question`
- `good first issue`
- `needs-repro`
- `blocked`
- `wontfix`
- `duplicate`

## Triage Flow

1. Confirm the report is understandable.
2. Label it.
3. Decide whether it is:
   - actionable now
   - needs more information
   - roadmap-later
   - out of scope
4. Reply clearly and politely.
5. Close promptly if it is duplicate, out of scope, or not reproducible after follow-up.

## Suggested Maintainer Replies

- For roadmap-later:
  - “Thanks for writing this up. We agree it is interesting, but we are not committing to it in the current release window.”
- For out-of-scope PRs:
  - “Thanks for the contribution. We are keeping the repo open to PRs, but we are not able to take this change into the supported surface right now.”
- For support questions:
  - “Thanks. Public support is best-effort, so response times may vary, but we will try to point you in the right direction.”

## When To Close

Close when:

- the issue is resolved
- the issue is duplicate
- the report cannot be reproduced after requested follow-up
- the change is clearly outside project direction
- the question has been answered and there is no remaining action

## Release And Docs Discipline

- If public behavior changes, update `README.md`, `docs/SUPPORT_POLICY.md`, and the relevant contract docs in the same change.
- If release posture changes, update `STATUS.md`, `CHANGELOG.md`, and release-readiness docs together.
