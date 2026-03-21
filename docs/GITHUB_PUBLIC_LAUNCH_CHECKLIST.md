# GitHub Public Launch Checklist

Use this checklist when preparing to flip the repository public or immediately after doing so.

## Repository Settings

- Enable branch protection on `main`
- Require the CI workflow to pass before merge
- Restrict direct pushes to maintainers
- Keep Releases enabled
- Keep Issues enabled
- Keep Pull Requests enabled
- Leave Discussions disabled for the initial public launch unless a dedicated community Q&A surface is desired

## Maintainer Setup

- Confirm `security@world-runtime.dev` is monitored
- Confirm `conduct@world-runtime.dev` is monitored
- Confirm at least one maintainer is watching repo notifications
- Confirm `CODEOWNERS` reflects the intended maintainer account(s)

## Public Hygiene

- Confirm no local filesystem paths remain in public docs/templates
- Confirm no secrets or private customer data are committed
- Confirm README quickstart works from a clean checkout
- Confirm release/version messaging is consistent across `README.md`, `STATUS.md`, `CHANGELOG.md`, tags, and `VERSION`

## Launch-Day Verification

- Open the repo as a signed-out viewer and read the README top-to-bottom
- Open the issue chooser and verify templates are visible and understandable
- Open the pull request template and verify expectations are clear
- Confirm Actions are green on the latest default-branch commit
