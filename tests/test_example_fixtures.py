from conftest import load_json


def test_event_example_has_temporal_order(top_level_example_paths):
    event = load_json(top_level_example_paths["event"])
    assert event["recorded_at"] >= event["occurred_at"]


def test_entity_example_has_version(top_level_example_paths):
    entity = load_json(top_level_example_paths["entity"])
    assert entity["version"] >= 1


def test_proposal_example_has_action_type(top_level_example_paths):
    proposal = load_json(top_level_example_paths["proposal"])
    assert proposal["proposed_action"]["action_type"]


def test_decision_example_references_selected_proposal(top_level_example_paths):
    decision = load_json(top_level_example_paths["decision"])
    assert decision["selected_proposal_id"]
    assert decision["selected_action"]["action_type"]


def test_simulation_example_has_status(top_level_example_paths):
    sim = load_json(top_level_example_paths["simulation"])
    assert sim["status"] in {"draft", "running", "completed", "failed", "cancelled"}
