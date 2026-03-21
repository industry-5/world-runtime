# Partner Onboarding Guide

This guide is for external domain teams integrating with World Runtime.

## Prerequisites

- Python 3.10+
- `pip install -r requirements-dev.txt`
- Clone repository and verify baseline:
  - `make test`
  - `make validate`

## Onboarding flow

1. Read contracts and compatibility boundaries.
   - `docs/EXTENSION_CONTRACTS.md`
   - `docs/COMPATIBILITY_MATRIX.md`
2. Scaffold extension starters.
   - Adapter starter:
     `python3 scripts/scaffold_extension.py adapter --name "Acme Ops" --output-dir tmp/onboarding/acme-adapter`
   - Connector plugin starter:
     `python3 scripts/scaffold_extension.py connector-plugin --name "Acme Queue" --provider "acme.queue" --output-dir tmp/onboarding/acme-queue-plugin`
3. Integrate scaffolded code into your domain package and registry wiring.
4. Add policy pack and scenario fixtures.
5. Run milestone checks:
   - `make extension-contracts`
   - `make adapters`
   - `make connectors`
   - `make connector-plugins`
6. Run compatibility checks before release:
   - `make protocol-compat`
   - `make public-api-compat`

## Release bundle assets for partners

`make release-artifacts` now ships extension onboarding assets:

- extension contracts (`docs/EXTENSION_CONTRACTS.md`)
- onboarding guide (`docs/PARTNER_ONBOARDING.md`)
- compatibility matrix (`docs/COMPATIBILITY_MATRIX.md`)
- scaffold templates (`templates/adapter_starter/`, `templates/connector_plugin_starter/`)
- scaffold tooling (`scripts/scaffold_extension.py`)

## Expected success criteria

A partner should be able to generate both starters and pass:

- `make extension-contracts`
- `make m24-validate`
