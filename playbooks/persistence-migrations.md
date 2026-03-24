# Playbook: Persistence Migration Strategy

## Goal

Apply deterministic schema migrations for production-ready event/snapshot persistence adapters.

## Migration model

- migrations are ordered SQL files in `infra/migrations/persistence/`
- migration state is tracked in `schema_migrations` (`version`, `checksum`, `applied_at`)
- re-running migrations is idempotent
- checksum mismatch for an applied version is treated as a hard failure

## Commands

```bash
make migrate-local
make migrate-dev
```

## Procedure

1. Review pending SQL files in `infra/migrations/persistence/`.
2. Run migration command for target profile.
3. Confirm applied/skipped output.
4. Run `make test` and `make deploy-local` / `make deploy-dev`.
5. For incompatible schema changes, add a new migration file; do not edit already-applied migrations.
