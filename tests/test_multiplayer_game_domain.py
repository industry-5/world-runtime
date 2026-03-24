from core.policy_engine import DeterministicPolicyEngine
from conftest import load_json


def test_multiplayer_game_policy_warns_and_requires_approval(multiplayer_game_scenario_dir):
    policy = load_json(multiplayer_game_scenario_dir / "policy.json")
    proposal = load_json(multiplayer_game_scenario_dir / "proposal.json")

    report = DeterministicPolicyEngine().evaluate_policies([policy], proposal)

    assert report.final_outcome == "require_approval"
    assert report.requires_approval is True
    assert any(e.outcome == "warn" for e in report.evaluations)


def test_multiplayer_game_resolution_options_cover_deny_and_allow_paths(
    multiplayer_game_scenario_dir,
):
    policy = load_json(multiplayer_game_scenario_dir / "policy.json")
    proposals = load_json(multiplayer_game_scenario_dir / "resolution_options.json")

    unsafe = proposals[0]
    serialized = proposals[1]
    engine = DeterministicPolicyEngine()

    unsafe_report = engine.evaluate_policies([policy], unsafe)
    serialized_report = engine.evaluate_policies([policy], serialized)

    assert unsafe_report.final_outcome == "deny"
    assert unsafe_report.denied is True
    assert serialized_report.final_outcome == "allow"
    assert serialized_report.requires_approval is False


def test_multiplayer_game_decision_tracks_reviewed_reconciliation(multiplayer_game_scenario_dir):
    proposal = load_json(multiplayer_game_scenario_dir / "proposal.json")
    decision = load_json(multiplayer_game_scenario_dir / "decision.json")
    simulation = load_json(multiplayer_game_scenario_dir / "simulation.json")

    assert decision["selected_proposal_id"] == proposal["proposal_id"]
    assert decision["approval_status"] == "approved"
    assert decision["policy_results"][0]["outcome"] == "require_approval"
    assert simulation["outcomes"]["recommended_proposal_id"] == (
        "proposal.multiplayer-game.serialized.0003"
    )
    assert simulation["outcomes"]["projected_desync_players_avoided"] == 7
