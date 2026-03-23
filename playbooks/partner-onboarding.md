# Playbook: Partner Onboarding

## Purpose

Run a predictable partner onboarding path for extension authors.

## Inputs

- partner adapter name
- partner connector provider id
- repo checkout with dependencies installed

## Steps

1. Generate adapter scaffold.

```bash
python3 scripts/scaffold_extension.py adapter --name "Partner Domain" --output-dir tmp/onboarding/partner-adapter
```

2. Generate connector plugin scaffold.

```bash
python3 scripts/scaffold_extension.py connector-plugin --name "Partner Queue" --provider "partner.queue" --output-dir tmp/onboarding/partner-queue-plugin
```

3. Run extension boundary checks.

```bash
make extension-contracts
make adapters
make connector-plugins
```

4. Run compatibility checks.

```bash
make protocol-compat
make public-api-compat
```

5. Build release bundle for handoff.

```bash
make release-artifacts
```

## Outputs

- generated adapter/plugin starter directories under `tmp/onboarding/`
- passing extension and compatibility checks
- release artifact bundle under `dist/releases/`
