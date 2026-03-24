from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter


class MultiplayerGameAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-multiplayer-game"

    @property
    def domain_name(self) -> str:
        return "multiplayer-game"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "game_shard",
            "match_instance",
            "player_party",
            "consistency_guard",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "simultaneous_action_window_opened",
            "state_divergence_detected",
            "reconciliation_plan_submitted",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "multiplayer-game-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "multiplayer_game" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "multiplayer_game" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "multiplayer_game" / "schemas" / "event_types.schema.json",
        ]
