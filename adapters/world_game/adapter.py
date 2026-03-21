from pathlib import Path
from typing import Set

from adapters.base import DomainAdapter
from adapters.world_game.service import WorldGameService
from core.policy_engine import DeterministicPolicyEngine


class WorldGameAdapter(DomainAdapter):
    @property
    def adapter_id(self) -> str:
        return "adapter-world-game"

    @property
    def domain_name(self) -> str:
        return "world-game"

    @property
    def entity_types(self) -> Set[str]:
        return {
            "wg_region",
            "wg_population_group",
            "wg_resource_stock",
            "wg_resource_flow",
            "wg_infrastructure_asset",
            "wg_policy_instrument",
            "wg_constraint",
            "wg_goal",
            "wg_scenario",
            "wg_strategy",
            "wg_indicator_definition",
        }

    @property
    def event_types(self) -> Set[str]:
        return {
            "wg_baseline_loaded",
            "wg_indicator_observed",
            "wg_resource_flow_updated",
            "wg_constraint_registered",
            "wg_goal_declared",
            "wg_strategy_proposed",
            "wg_strategy_modified",
            "wg_policy_evaluated",
            "wg_approval_requested",
            "wg_approval_resolved",
            "wg_simulation_branch_created",
            "wg_turn_executed",
            "wg_shock_realized",
            "wg_outcome_projected",
            "wg_scenario_compared",
            "wg_run_published",
        }

    def scenario_dir(self, repo_root: Path) -> Path:
        return repo_root / "examples" / "scenarios" / "world-game-mini"

    def default_policy_path(self, repo_root: Path) -> Path:
        return repo_root / "adapters" / "world_game" / "policies" / "default_policy.json"

    def adapter_schema_paths(self, repo_root: Path):
        return [
            repo_root / "adapters" / "world_game" / "schemas" / "entity_types.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "event_types.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "indicator_definition.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "intervention.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "shock.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "scenario.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "strategy.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "comparison_report.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "constraint_pack.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "indicator_registry.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "intervention_library.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "shock_library.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "scenario_template.schema.json",
            repo_root / "adapters" / "world_game" / "schemas" / "template_bundle.schema.json",
        ]

    def build_service(self, repo_root: Path, policy_engine: DeterministicPolicyEngine) -> WorldGameService:
        return WorldGameService(repo_root=repo_root, policy_engine=policy_engine)
