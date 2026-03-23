# CI/CD And Release Playbook

## CI merge gate

Run the same checks as CI before merging:

```bash
make ci-gate
```

This executes:

- schema validation and test suite (`make validate`)
- eval enforcement (`make evals`)
- fixture and adapter checks (`make examples`, `make adapters`)
- App Server protocol/schema compatibility checks (`make protocol-compat`)

## v1.0 release gate

Run the aggregate M25 release gate:

```bash
make m25-validate
```

This command validates release-readiness docs, security/trust-boundary disposition,
and executes baseline/milestone/regression command matrix checks while writing:

- `tmp/diagnostics/m25_release_candidate_gate.latest.json`

## Release artifact build

Build versioned release artifacts from `VERSION`:

```bash
make release-artifacts
```

Build with an explicit semantic version:

```bash
make release-artifacts RELEASE_VERSION=0.1.1
```

Build with the current GA version:

```bash
make release-artifacts RELEASE_VERSION=1.0.0
```

Artifacts are written to `dist/releases/v<version>/` and `dist/releases/v<version>.tar.gz`.

Release bundle includes:

- core docs and protocol contract
- schema set
- eval manifest
- release manifest (`release.manifest.json`)
- checksums (`SHA256SUMS`)

## GitHub workflows

- `.github/workflows/ci.yml` runs `make ci-gate` on pull requests and pushes to `main`/`codex/**`.
- `.github/workflows/release.yml` runs on `v*` tags or manual dispatch, builds release artifacts, uploads them, and publishes a GitHub release for tag events.
