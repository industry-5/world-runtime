from conftest import load_json


def _scenario_integrity(scenario_dir):
    scenario = load_json(scenario_dir / "scenario.json")
    interventions = load_json(scenario_dir / "interventions.json")
    shocks = load_json(scenario_dir / "shocks.json")

    region_ids = {region["region_id"] for region in scenario["regions"]}
    indicator_ids = {indicator["indicator_id"] for indicator in scenario["indicator_definitions"]}
    intervention_ids = {item["intervention_id"] for item in scenario["interventions"]}
    shock_ids = {item["shock_id"] for item in scenario["shocks"]}

    assert set(scenario["baseline_indicators"].keys()) == region_ids
    for values in scenario["baseline_indicators"].values():
        assert set(values.keys()) == indicator_ids

    for intervention in scenario["interventions"]:
        assert set(intervention["applicable_regions"]).issubset(region_ids)

    for shock in scenario["shocks"]:
        assert set(shock["applicable_regions"]).issubset(region_ids)

    dependency_graph = scenario.get("dependency_graph") or {}
    if dependency_graph:
        node_ids = {node["node_id"] for node in dependency_graph.get("nodes", [])}
        for node in dependency_graph.get("nodes", []):
            assert node["region_id"] in region_ids
        for edge in dependency_graph.get("edges", []):
            assert edge["from_node_id"] in node_ids
            assert edge["to_node_id"] in node_ids
            assert edge["from_node_id"] != edge["to_node_id"]
            assert float(edge["capacity"]) >= 0

    resource_stocks = scenario.get("resource_stocks", [])
    stock_ids = {stock["stock_id"] for stock in resource_stocks}
    for stock in resource_stocks:
        assert stock["region_id"] in region_ids
        assert stock["indicator_id"] in indicator_ids
        assert float(stock.get("max_bound", stock["baseline"])) >= float(stock.get("min_bound", stock["baseline"]))

    for flow in scenario.get("resource_flows", []):
        assert flow["source_stock_id"] in stock_ids
        assert flow["target_stock_id"] in stock_ids
        assert float(flow["capacity"]) >= 0
        assert 0 <= float(flow.get("loss_factor", 0.0)) <= 1

    for rule in scenario.get("spillover_rules", []):
        assert rule["rule_id"]
        if "from_node_id" in rule:
            assert rule["from_node_id"]
        if "to_node_id" in rule:
            assert rule["to_node_id"]
        assert float(rule["coefficient"]) == float(rule["coefficient"])

    assert set(interventions["interventions"]).issubset(intervention_ids)
    assert set(shocks["shocks"]).issubset(shock_ids)


def test_world_game_multi_region_example_integrity(world_game_multi_region_scenario_dir):
    _scenario_integrity(world_game_multi_region_scenario_dir)
