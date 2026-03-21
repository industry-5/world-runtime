# Playbook: Operator Quickstart

## Goal

Run a first operator workflow without editing runtime internals.

## Fast Path

```bash
make workflow-quickstart
```

If you want the supported HTTP + SDK surface after that:

```bash
make api-server
make sdk-example
```

If you want the primary showcase demo path after that:

```bash
python3 -m api.http_server --host 127.0.0.1 --port 8080
python3 labs/world_game_studio_next/server.py --host 127.0.0.1 --port 8093 --upstream http://127.0.0.1:8080
```

## Procedure

1. Start with the default adapter (`adapter-supply-network`).
2. Run quickstart command.
3. Review returned reasoning summary and generated draft proposal.
4. Inspect emitted task events for auditability.
5. For high-constraint workflows, run `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-air-traffic`.
6. For the World Game domain/runtime path behind the showcase app, use `python3 scripts/run_operator_workflow.py quickstart --adapter-id adapter-world-game`.
7. For the guided showcase UI flow, continue with [playbooks/world-game-studio-next-demo.md](world-game-studio-next-demo.md).
8. For external integration smoke checks, run API + SDK commands and verify a session plus proposal policy result are returned.
