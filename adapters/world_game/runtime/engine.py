from __future__ import annotations

import json
import hashlib
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from uuid import uuid4

from core.policy_engine import DeterministicPolicyEngine, PolicyReport


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _round(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


def _sorted_effects(effects: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        effects,
        key=lambda item: (
            str(item.get("region_id", "")),
            str(item.get("indicator_id", "")),
            float(item.get("delta", 0.0)),
            float(item.get("multiplier", 1.0)),
        ),
    )


def _coerce_positive_or_zero(value: Any, field_name: str) -> float:
    coerced = float(value)
    if coerced < 0:
        raise ValueError("%s must be >= 0" % field_name)
    return coerced


def _normalized_weight_map(region_ids: Sequence[str], explicit_weights: Dict[str, Any]) -> Dict[str, float]:
    weights: Dict[str, float] = {}
    for region_id in region_ids:
        if region_id in explicit_weights:
            candidate = float(explicit_weights[region_id])
            if candidate < 0:
                raise ValueError("equity_dimensions.region_weights contains negative value for %s" % region_id)
            weights[region_id] = candidate
        else:
            weights[region_id] = 1.0

    total = sum(weights.values())
    if total <= 0:
        return {region_id: 1.0 for region_id in region_ids}
    return weights


def _topological_sort(node_ids: Sequence[str], outgoing_by_node: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    indegree = {node_id: 0 for node_id in node_ids}
    for node_id in node_ids:
        for edge in outgoing_by_node.get(node_id, []):
            indegree[edge["to_node_id"]] += 1

    frontier = sorted([node_id for node_id, degree in indegree.items() if degree == 0])
    order: List[str] = []

    while frontier:
        node_id = frontier.pop(0)
        order.append(node_id)
        edges = sorted(
            outgoing_by_node.get(node_id, []),
            key=lambda edge: (str(edge["to_node_id"]), str(edge["edge_id"])),
        )
        for edge in edges:
            target = edge["to_node_id"]
            indegree[target] -= 1
            if indegree[target] == 0:
                frontier.append(target)
                frontier.sort()

    if len(order) != len(node_ids):
        raise ValueError("dependency_graph contains a cycle; Phase 2 requires a DAG")
    return order


def _compute_reachability(
    topological_order: Sequence[str],
    outgoing_by_node: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Set[str]]:
    reachable: Dict[str, Set[str]] = {node_id: set() for node_id in topological_order}
    for node_id in reversed(topological_order):
        for edge in outgoing_by_node.get(node_id, []):
            target = edge["to_node_id"]
            reachable[node_id].add(target)
            reachable[node_id].update(reachable.get(target, set()))
    return reachable


def _normalize_dependency_graph(raw_graph: Any, region_ids: Sequence[str]) -> Dict[str, Any]:
    empty = {
        "nodes": [],
        "edges": [],
        "nodes_by_id": {},
        "edges_by_id": {},
        "incoming_by_node": {},
        "outgoing_by_node": {},
        "topological_order": [],
        "topological_index": {},
        "reachable_by_node": {},
    }
    if raw_graph is None:
        return empty
    if not isinstance(raw_graph, dict):
        raise ValueError("dependency_graph must be an object")

    region_set = set(region_ids)
    raw_nodes = raw_graph.get("nodes", [])
    raw_edges = raw_graph.get("edges", [])

    if not isinstance(raw_nodes, list):
        raise ValueError("dependency_graph.nodes must be a list")
    if not isinstance(raw_edges, list):
        raise ValueError("dependency_graph.edges must be a list")

    nodes: List[Dict[str, Any]] = []
    nodes_by_id: Dict[str, Dict[str, Any]] = {}
    for item in raw_nodes:
        node_id = str(item.get("node_id", "")).strip()
        if not node_id:
            raise ValueError("dependency_graph.nodes[].node_id is required")
        if node_id in nodes_by_id:
            raise ValueError("dependency_graph.nodes has duplicate node_id: %s" % node_id)

        region_id = str(item.get("region_id", "")).strip()
        if not region_id:
            raise ValueError("dependency_graph.nodes[%s].region_id is required" % node_id)
        if region_id not in region_set:
            raise ValueError("dependency_graph.nodes[%s] references unknown region_id: %s" % (node_id, region_id))

        normalized = {
            "node_id": node_id,
            "region_id": region_id,
            "label": item.get("label") or node_id,
        }
        nodes.append(normalized)
        nodes_by_id[node_id] = normalized

    edges: List[Dict[str, Any]] = []
    edges_by_id: Dict[str, Dict[str, Any]] = {}
    outgoing_by_node: Dict[str, List[Dict[str, Any]]] = {node_id: [] for node_id in nodes_by_id}
    incoming_by_node: Dict[str, List[Dict[str, Any]]] = {node_id: [] for node_id in nodes_by_id}

    for index, item in enumerate(raw_edges):
        from_node_id = str(item.get("from_node_id", "")).strip()
        to_node_id = str(item.get("to_node_id", "")).strip()
        if from_node_id not in nodes_by_id:
            raise ValueError("dependency_graph.edges[%d] references unknown from_node_id: %s" % (index, from_node_id))
        if to_node_id not in nodes_by_id:
            raise ValueError("dependency_graph.edges[%d] references unknown to_node_id: %s" % (index, to_node_id))
        if from_node_id == to_node_id:
            raise ValueError("dependency_graph.edges[%d] contains self-edge on %s" % (index, from_node_id))

        edge_id = str(item.get("edge_id", "")).strip() or "edge.%s.%s" % (from_node_id, to_node_id)
        if edge_id in edges_by_id:
            raise ValueError("dependency_graph.edges has duplicate edge_id: %s" % edge_id)

        capacity = _coerce_positive_or_zero(item.get("capacity", 0.0), "dependency_graph.edge.capacity")
        latency_turns = int(item.get("latency_turns", 0))
        if latency_turns < 0:
            raise ValueError("dependency_graph.edges[%s].latency_turns must be >= 0" % edge_id)

        normalized = {
            "edge_id": edge_id,
            "from_node_id": from_node_id,
            "to_node_id": to_node_id,
            "capacity": capacity,
            "latency_turns": latency_turns,
        }
        edges.append(normalized)
        edges_by_id[edge_id] = normalized
        outgoing_by_node[from_node_id].append(normalized)
        incoming_by_node[to_node_id].append(normalized)

    for node_id in outgoing_by_node:
        outgoing_by_node[node_id] = sorted(outgoing_by_node[node_id], key=lambda edge: str(edge["edge_id"]))
    for node_id in incoming_by_node:
        incoming_by_node[node_id] = sorted(incoming_by_node[node_id], key=lambda edge: str(edge["edge_id"]))

    node_ids = sorted(nodes_by_id.keys())
    topological_order = _topological_sort(node_ids=node_ids, outgoing_by_node=outgoing_by_node)
    topological_index = {node_id: index for index, node_id in enumerate(topological_order)}
    reachable_by_node = _compute_reachability(topological_order=topological_order, outgoing_by_node=outgoing_by_node)

    return {
        "nodes": sorted(nodes, key=lambda item: str(item["node_id"])),
        "edges": sorted(edges, key=lambda item: str(item["edge_id"])),
        "nodes_by_id": nodes_by_id,
        "edges_by_id": edges_by_id,
        "incoming_by_node": incoming_by_node,
        "outgoing_by_node": outgoing_by_node,
        "topological_order": topological_order,
        "topological_index": topological_index,
        "reachable_by_node": reachable_by_node,
    }


def _normalize_resource_stocks(
    raw_stocks: Any,
    dependency_graph: Dict[str, Any],
    region_ids: Sequence[str],
    indicator_ids: Sequence[str],
) -> Dict[str, Any]:
    empty = {"items": [], "by_id": {}}
    if raw_stocks is None:
        return empty
    if not isinstance(raw_stocks, list):
        raise ValueError("resource_stocks must be a list")

    region_set = set(region_ids)
    indicator_set = set(indicator_ids)
    nodes_by_id = dependency_graph.get("nodes_by_id", {})

    items: List[Dict[str, Any]] = []
    by_id: Dict[str, Dict[str, Any]] = {}
    for item in raw_stocks:
        stock_id = str(item.get("stock_id", "")).strip()
        if not stock_id:
            raise ValueError("resource_stocks[].stock_id is required")
        if stock_id in by_id:
            raise ValueError("resource_stocks has duplicate stock_id: %s" % stock_id)

        region_id = str(item.get("region_id", "")).strip()
        if region_id not in region_set:
            raise ValueError("resource_stocks[%s] references unknown region_id: %s" % (stock_id, region_id))

        node_id = str(item.get("node_id", "")).strip()
        if nodes_by_id:
            if not node_id:
                raise ValueError("resource_stocks[%s].node_id is required when dependency_graph is defined" % stock_id)
            if node_id not in nodes_by_id:
                raise ValueError("resource_stocks[%s] references unknown node_id: %s" % (stock_id, node_id))
            node_region = nodes_by_id[node_id]["region_id"]
            if node_region != region_id:
                raise ValueError(
                    "resource_stocks[%s] region/node mismatch: region_id=%s node.region_id=%s"
                    % (stock_id, region_id, node_region)
                )

        indicator_id = str(item.get("indicator_id", "")).strip()
        if indicator_id not in indicator_set:
            raise ValueError("resource_stocks[%s] references unknown indicator_id: %s" % (stock_id, indicator_id))

        baseline = float(item.get("baseline", 0.0))
        min_bound = float(item.get("min_bound", baseline))
        max_bound = float(item.get("max_bound", baseline))
        if max_bound < min_bound:
            raise ValueError("resource_stocks[%s] has invalid bounds (max_bound < min_bound)" % stock_id)
        if baseline < min_bound or baseline > max_bound:
            raise ValueError("resource_stocks[%s].baseline must be within [min_bound, max_bound]" % stock_id)

        regen_rate = float(item.get("regen_rate", 0.0))
        demand_rate = _coerce_positive_or_zero(item.get("demand_rate", 0.0), "resource_stocks.demand_rate")
        response_factor = float(item.get("response_factor", 0.0))

        normalized = {
            "stock_id": stock_id,
            "node_id": node_id,
            "region_id": region_id,
            "indicator_id": indicator_id,
            "baseline": baseline,
            "min_bound": min_bound,
            "max_bound": max_bound,
            "regen_rate": regen_rate,
            "demand_rate": demand_rate,
            "response_factor": response_factor,
        }
        items.append(normalized)
        by_id[stock_id] = normalized

    items = sorted(items, key=lambda entry: str(entry["stock_id"]))
    return {
        "items": items,
        "by_id": by_id,
    }


def _find_direct_edge(
    dependency_graph: Dict[str, Any],
    from_node_id: str,
    to_node_id: str,
) -> Optional[Dict[str, Any]]:
    for edge in dependency_graph.get("outgoing_by_node", {}).get(from_node_id, []):
        if edge["to_node_id"] == to_node_id:
            return edge
    return None


def _normalize_resource_flows(
    raw_flows: Any,
    dependency_graph: Dict[str, Any],
    resource_stocks: Dict[str, Any],
) -> Dict[str, Any]:
    empty = {"items": [], "by_id": {}}
    if raw_flows is None:
        return empty
    if not isinstance(raw_flows, list):
        raise ValueError("resource_flows must be a list")

    nodes_by_id = dependency_graph.get("nodes_by_id", {})
    topological_index = dependency_graph.get("topological_index", {})
    reachable_by_node = dependency_graph.get("reachable_by_node", {})
    if not nodes_by_id:
        raise ValueError("resource_flows requires dependency_graph nodes")

    stock_by_id = resource_stocks.get("by_id", {})
    if not stock_by_id:
        raise ValueError("resource_flows requires resource_stocks")

    items: List[Dict[str, Any]] = []
    by_id: Dict[str, Dict[str, Any]] = {}
    for item in raw_flows:
        flow_id = str(item.get("flow_id", "")).strip()
        if not flow_id:
            raise ValueError("resource_flows[].flow_id is required")
        if flow_id in by_id:
            raise ValueError("resource_flows has duplicate flow_id: %s" % flow_id)

        source_stock_id = str(item.get("source_stock_id", "")).strip()
        target_stock_id = str(item.get("target_stock_id", "")).strip()
        if source_stock_id not in stock_by_id:
            raise ValueError("resource_flows[%s] references unknown source_stock_id: %s" % (flow_id, source_stock_id))
        if target_stock_id not in stock_by_id:
            raise ValueError("resource_flows[%s] references unknown target_stock_id: %s" % (flow_id, target_stock_id))

        source_stock = stock_by_id[source_stock_id]
        target_stock = stock_by_id[target_stock_id]

        from_node_id = str(item.get("from_node_id", source_stock.get("node_id", ""))).strip()
        to_node_id = str(item.get("to_node_id", target_stock.get("node_id", ""))).strip()
        if from_node_id not in nodes_by_id:
            raise ValueError("resource_flows[%s] references unknown from_node_id: %s" % (flow_id, from_node_id))
        if to_node_id not in nodes_by_id:
            raise ValueError("resource_flows[%s] references unknown to_node_id: %s" % (flow_id, to_node_id))
        if from_node_id == to_node_id:
            raise ValueError("resource_flows[%s] cannot self-reference node %s" % (flow_id, from_node_id))

        if source_stock.get("node_id") and source_stock["node_id"] != from_node_id:
            raise ValueError(
                "resource_flows[%s] source node mismatch (flow=%s stock=%s)"
                % (flow_id, from_node_id, source_stock["node_id"])
            )
        if target_stock.get("node_id") and target_stock["node_id"] != to_node_id:
            raise ValueError(
                "resource_flows[%s] target node mismatch (flow=%s stock=%s)"
                % (flow_id, to_node_id, target_stock["node_id"])
            )

        if to_node_id not in reachable_by_node.get(from_node_id, set()):
            raise ValueError(
                "resource_flows[%s] must point to a downstream connected node (%s -> %s)"
                % (flow_id, from_node_id, to_node_id)
            )
        if int(topological_index[from_node_id]) >= int(topological_index[to_node_id]):
            raise ValueError(
                "resource_flows[%s] violates DAG ordering (%s -> %s)" % (flow_id, from_node_id, to_node_id)
            )

        capacity = _coerce_positive_or_zero(item.get("capacity", 0.0), "resource_flows.capacity")
        loss_factor = float(item.get("loss_factor", 0.0))
        if loss_factor < 0 or loss_factor > 1:
            raise ValueError("resource_flows[%s].loss_factor must be within [0, 1]" % flow_id)

        indicator_conversion = float(item.get("indicator_conversion", 1.0))
        direct_edge = _find_direct_edge(dependency_graph, from_node_id, to_node_id)

        normalized = {
            "flow_id": flow_id,
            "source_stock_id": source_stock_id,
            "target_stock_id": target_stock_id,
            "from_node_id": from_node_id,
            "to_node_id": to_node_id,
            "capacity": capacity,
            "loss_factor": loss_factor,
            "indicator_conversion": indicator_conversion,
            "edge_id": direct_edge.get("edge_id") if direct_edge else None,
        }
        items.append(normalized)
        by_id[flow_id] = normalized

    items = sorted(
        items,
        key=lambda flow: (
            int(topological_index[flow["to_node_id"]]),
            int(topological_index[flow["from_node_id"]]),
            str(flow["flow_id"]),
        ),
    )
    return {
        "items": items,
        "by_id": by_id,
    }


def _normalize_spillover_rules(
    raw_rules: Any,
    dependency_graph: Dict[str, Any],
    indicator_ids: Sequence[str],
) -> Dict[str, Any]:
    empty = {"items": [], "by_id": {}}
    if raw_rules is None:
        return empty
    if not isinstance(raw_rules, list):
        raise ValueError("spillover_rules must be a list")

    nodes_by_id = dependency_graph.get("nodes_by_id", {})
    edges_by_id = dependency_graph.get("edges_by_id", {})
    topological_index = dependency_graph.get("topological_index", {})
    reachable_by_node = dependency_graph.get("reachable_by_node", {})
    indicator_set = set(indicator_ids)

    if not nodes_by_id:
        raise ValueError("spillover_rules requires dependency_graph nodes")

    items: List[Dict[str, Any]] = []
    by_id: Dict[str, Dict[str, Any]] = {}
    for item in raw_rules:
        rule_id = str(item.get("rule_id", "")).strip()
        if not rule_id:
            raise ValueError("spillover_rules[].rule_id is required")
        if rule_id in by_id:
            raise ValueError("spillover_rules has duplicate rule_id: %s" % rule_id)

        edge_id = str(item.get("edge_id", "")).strip()
        if edge_id:
            edge = edges_by_id.get(edge_id)
            if edge is None:
                raise ValueError("spillover_rules[%s] references unknown edge_id: %s" % (rule_id, edge_id))
            from_node_id = edge["from_node_id"]
            to_node_id = edge["to_node_id"]
        else:
            from_node_id = str(item.get("from_node_id", "")).strip()
            to_node_id = str(item.get("to_node_id", "")).strip()

        if from_node_id not in nodes_by_id:
            raise ValueError("spillover_rules[%s] references unknown from_node_id: %s" % (rule_id, from_node_id))
        if to_node_id not in nodes_by_id:
            raise ValueError("spillover_rules[%s] references unknown to_node_id: %s" % (rule_id, to_node_id))
        if from_node_id == to_node_id:
            raise ValueError("spillover_rules[%s] cannot self-reference node %s" % (rule_id, from_node_id))

        if to_node_id not in reachable_by_node.get(from_node_id, set()):
            raise ValueError(
                "spillover_rules[%s] must point to a downstream connected node (%s -> %s)"
                % (rule_id, from_node_id, to_node_id)
            )
        if int(topological_index[from_node_id]) >= int(topological_index[to_node_id]):
            raise ValueError(
                "spillover_rules[%s] violates DAG ordering (%s -> %s)" % (rule_id, from_node_id, to_node_id)
            )

        source_indicator_id = str(item.get("source_indicator_id", item.get("indicator_id", ""))).strip()
        target_indicator_id = str(item.get("target_indicator_id", source_indicator_id)).strip()
        if source_indicator_id not in indicator_set:
            raise ValueError(
                "spillover_rules[%s] references unknown source_indicator_id: %s" % (rule_id, source_indicator_id)
            )
        if target_indicator_id not in indicator_set:
            raise ValueError(
                "spillover_rules[%s] references unknown target_indicator_id: %s" % (rule_id, target_indicator_id)
            )

        coefficient = float(item.get("coefficient", 0.0))
        max_abs_transfer = item.get("max_abs_transfer")
        if max_abs_transfer is not None:
            max_abs_transfer = _coerce_positive_or_zero(max_abs_transfer, "spillover_rules.max_abs_transfer")

        normalized = {
            "rule_id": rule_id,
            "edge_id": edge_id or None,
            "from_node_id": from_node_id,
            "to_node_id": to_node_id,
            "source_indicator_id": source_indicator_id,
            "target_indicator_id": target_indicator_id,
            "coefficient": coefficient,
            "max_abs_transfer": max_abs_transfer,
        }
        items.append(normalized)
        by_id[rule_id] = normalized

    items = sorted(
        items,
        key=lambda rule: (
            int(topological_index[rule["to_node_id"]]),
            int(topological_index[rule["from_node_id"]]),
            str(rule["rule_id"]),
        ),
    )
    return {
        "items": items,
        "by_id": by_id,
    }


def _normalize_equity_dimensions(raw_dimensions: Any, region_ids: Sequence[str]) -> Dict[str, Any]:
    empty = {
        "region_weights": {region_id: 1.0 for region_id in region_ids},
        "groups": [],
        "baseline_targets": {},
    }
    if raw_dimensions is None:
        return empty
    if not isinstance(raw_dimensions, dict):
        raise ValueError("equity_dimensions must be an object")

    region_set = set(region_ids)
    raw_region_weights = raw_dimensions.get("region_weights", {})
    if not isinstance(raw_region_weights, dict):
        raise ValueError("equity_dimensions.region_weights must be an object")

    for region_id in raw_region_weights.keys():
        if region_id not in region_set:
            raise ValueError("equity_dimensions.region_weights references unknown region_id: %s" % region_id)

    region_weights = _normalized_weight_map(region_ids, raw_region_weights)

    raw_groups = raw_dimensions.get("groups", [])
    if not isinstance(raw_groups, list):
        raise ValueError("equity_dimensions.groups must be a list")

    groups: List[Dict[str, Any]] = []
    seen_group_ids: Set[str] = set()
    for item in raw_groups:
        group_id = str(item.get("group_id", "")).strip()
        if not group_id:
            raise ValueError("equity_dimensions.groups[].group_id is required")
        if group_id in seen_group_ids:
            raise ValueError("equity_dimensions.groups has duplicate group_id: %s" % group_id)
        seen_group_ids.add(group_id)

        members = [str(member) for member in item.get("region_ids", [])]
        if not members:
            raise ValueError("equity_dimensions.groups[%s].region_ids must not be empty" % group_id)
        unknown = sorted(set(members) - region_set)
        if unknown:
            raise ValueError(
                "equity_dimensions.groups[%s] references unknown region_ids: %s" % (group_id, ", ".join(unknown))
            )

        weight = float(item.get("weight", 1.0))
        if weight < 0:
            raise ValueError("equity_dimensions.groups[%s].weight must be >= 0" % group_id)

        baseline_target = item.get("baseline_target")
        normalized_group = {
            "group_id": group_id,
            "region_ids": sorted(set(members)),
            "weight": weight,
            "baseline_target": None if baseline_target is None else float(baseline_target),
        }
        groups.append(normalized_group)

    raw_baseline_targets = raw_dimensions.get("baseline_targets", {})
    if not isinstance(raw_baseline_targets, dict):
        raise ValueError("equity_dimensions.baseline_targets must be an object")
    baseline_targets: Dict[str, float] = {}
    for key in ("disparity_spread", "weighted_variance"):
        if key in raw_baseline_targets:
            baseline_targets[key] = float(raw_baseline_targets[key])

    return {
        "region_weights": region_weights,
        "groups": sorted(groups, key=lambda group: str(group["group_id"])),
        "baseline_targets": baseline_targets,
    }


def list_world_game_scenarios(examples_root: Path) -> List[Dict[str, Any]]:
    scenarios_dir = examples_root / "scenarios"
    items: List[Dict[str, Any]] = []
    if not scenarios_dir.exists():
        return items

    for child in sorted(scenarios_dir.iterdir()):
        if not child.is_dir():
            continue
        scenario_file = child / "scenario.json"
        if not scenario_file.exists():
            continue

        payload = load_world_game_scenario(scenario_file)
        items.append(
            {
                "scenario_id": payload["scenario_id"],
                "label": payload["label"],
                "description": payload["description"],
                "path": str(scenario_file),
                "regions": [region["region_id"] for region in payload["regions"]],
                "indicator_count": len(payload["indicator_definitions"]),
            }
        )

    return items


def load_world_game_scenario(path_or_payload: Path | Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(path_or_payload, Path):
        with path_or_payload.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = deepcopy(path_or_payload)

    return normalize_scenario_definition(payload)


_TEMPLATE_PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")


def _json_path(path_parts: Sequence[Any]) -> str:
    if not path_parts:
        return "$"

    chunks: List[str] = ["$"]
    for item in path_parts:
        if isinstance(item, int):
            chunks.append("[%d]" % item)
        else:
            chunks.append(".%s" % str(item))
    return "".join(chunks)


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _world_game_schema_dir(schema_dir: Optional[Path] = None) -> Path:
    if schema_dir is not None:
        return schema_dir
    return Path(__file__).resolve().parents[1] / "schemas"


def _build_world_game_schema_validator(schema_name: str, schema_dir: Optional[Path] = None) -> Any:
    try:
        from jsonschema import Draft202012Validator, RefResolver
    except Exception as exc:  # pragma: no cover - dependency/import error
        raise RuntimeError("jsonschema is required for world-game authoring validation") from exc

    directory = _world_game_schema_dir(schema_dir)
    schema_path = directory / schema_name
    if not schema_path.exists():
        raise ValueError("authoring schema not found: %s" % schema_path)

    with schema_path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)

    store: Dict[str, Any] = {}
    for local_path in directory.glob("*.schema.json"):
        with local_path.open("r", encoding="utf-8") as handle:
            local_schema = json.load(handle)
        schema_id = local_schema.get("$id")
        if schema_id:
            store[schema_id] = local_schema

    resolver = RefResolver(base_uri="%s/" % directory.as_uri(), referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


def validate_world_game_template_bundle(
    bundle: Dict[str, Any],
    schema_dir: Optional[Path] = None,
) -> List[Dict[str, str]]:
    validator = _build_world_game_schema_validator("template_bundle.schema.json", schema_dir=schema_dir)
    errors = sorted(validator.iter_errors(bundle), key=lambda err: list(err.path))
    return [
        {
            "path": _json_path(list(error.path)),
            "message": str(error.message),
        }
        for error in errors
    ]


def compute_world_game_template_bundle_hash(bundle: Dict[str, Any]) -> str:
    metadata = bundle.get("bundle_metadata", {})
    seed = str(metadata.get("deterministic_version_seed", "")).strip()
    if not seed:
        raise ValueError("bundle_metadata.deterministic_version_seed is required")

    hash_payload = {
        "seed": seed,
        "indicator_registries": bundle.get("indicator_registries", []),
        "intervention_libraries": bundle.get("intervention_libraries", []),
        "shock_libraries": bundle.get("shock_libraries", []),
        "scenario_templates": bundle.get("scenario_templates", []),
    }
    digest = hashlib.sha256(_stable_json(hash_payload).encode("utf-8")).hexdigest()
    return "sha256:%s" % digest


def _sort_and_assert_unique(
    items: Sequence[Dict[str, Any]],
    key_field: str,
    field_label: str,
) -> List[Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for item in items:
        item_id = str(item.get(key_field, "")).strip()
        if not item_id:
            raise ValueError("%s[].%s is required" % (field_label, key_field))
        if item_id in by_id:
            raise ValueError("%s contains duplicate %s: %s" % (field_label, key_field, item_id))
        by_id[item_id] = deepcopy(item)
    return sorted(by_id.values(), key=lambda entry: str(entry[key_field]))


def _normalize_world_game_template_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    normalized = deepcopy(bundle)
    normalized["indicator_registries"] = _sort_and_assert_unique(
        normalized.get("indicator_registries", []),
        key_field="registry_id",
        field_label="indicator_registries",
    )
    for registry in normalized["indicator_registries"]:
        registry["indicators"] = _sort_and_assert_unique(
            registry.get("indicators", []),
            key_field="indicator_id",
            field_label="indicator_registries[%s].indicators" % registry["registry_id"],
        )

    normalized["intervention_libraries"] = _sort_and_assert_unique(
        normalized.get("intervention_libraries", []),
        key_field="library_id",
        field_label="intervention_libraries",
    )
    for library in normalized["intervention_libraries"]:
        library["interventions"] = _sort_and_assert_unique(
            library.get("interventions", []),
            key_field="intervention_id",
            field_label="intervention_libraries[%s].interventions" % library["library_id"],
        )

    normalized["shock_libraries"] = _sort_and_assert_unique(
        normalized.get("shock_libraries", []),
        key_field="library_id",
        field_label="shock_libraries",
    )
    for library in normalized["shock_libraries"]:
        library["shocks"] = _sort_and_assert_unique(
            library.get("shocks", []),
            key_field="shock_id",
            field_label="shock_libraries[%s].shocks" % library["library_id"],
        )

    normalized["scenario_templates"] = _sort_and_assert_unique(
        normalized.get("scenario_templates", []),
        key_field="template_id",
        field_label="scenario_templates",
    )
    for template in normalized["scenario_templates"]:
        template["region_pool"] = _sort_and_assert_unique(
            template.get("region_pool", []),
            key_field="region_id",
            field_label="scenario_templates[%s].region_pool" % template["template_id"],
        )
        parameters = template.get("parameter_model", {}).get("parameters", [])
        deduped = _sort_and_assert_unique(
            parameters,
            key_field="name",
            field_label="scenario_templates[%s].parameter_model.parameters" % template["template_id"],
        )
        template.setdefault("parameter_model", {})["parameters"] = deduped

    return normalized


def load_world_game_template_bundle(
    path_or_payload: Path | Dict[str, Any],
    schema_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    if isinstance(path_or_payload, Path):
        with path_or_payload.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = deepcopy(path_or_payload)

    errors = validate_world_game_template_bundle(payload, schema_dir=schema_dir)
    if errors:
        first = errors[0]
        raise ValueError("template bundle schema validation failed at %s: %s" % (first["path"], first["message"]))

    normalized = _normalize_world_game_template_bundle(payload)
    expected_hash = compute_world_game_template_bundle_hash(normalized)
    declared_hash = str(normalized["bundle_metadata"].get("deterministic_version_hash", "")).strip()
    if declared_hash != expected_hash:
        raise ValueError(
            "bundle_metadata.deterministic_version_hash mismatch: expected %s but found %s"
            % (expected_hash, declared_hash)
        )
    normalized["bundle_metadata"]["deterministic_version_hash"] = expected_hash
    return normalized


def _load_world_game_bundle_payload(path_or_payload: Path | Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(path_or_payload, Path):
        with path_or_payload.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = deepcopy(path_or_payload)
    if not isinstance(payload, dict):
        raise ValueError("template bundle payload must be an object")
    return payload


def list_world_game_template_bundles(authoring_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    root = authoring_root or (Path(__file__).resolve().parents[3] / "examples" / "world-game-authoring")
    if not root.exists():
        return []

    entries: List[Dict[str, Any]] = []
    for bundle_path in sorted(root.rglob("*.json")):
        if not bundle_path.is_file():
            continue
        try:
            payload = _load_world_game_bundle_payload(bundle_path)
            metadata = payload.get("bundle_metadata", {})
            templates = payload.get("scenario_templates", [])
            if not isinstance(metadata, dict) or not isinstance(templates, list):
                continue
            if "bundle_id" not in metadata:
                continue
            entries.append(
                {
                    "bundle_path": str(bundle_path),
                    "bundle_id": str(metadata.get("bundle_id", "")),
                    "status": str(metadata.get("status", "")),
                    "template_version": metadata.get("template_version"),
                    "content_version": metadata.get("content_version"),
                    "deterministic_version_hash": metadata.get("deterministic_version_hash"),
                    "template_count": len(templates),
                    "templates": [
                        {
                            "template_id": str(template.get("template_id", "")),
                            "label": str(template.get("label", "")),
                            "parameter_names": sorted(
                                str(parameter.get("name", ""))
                                for parameter in template.get("parameter_model", {}).get("parameters", [])
                                if str(parameter.get("name", "")).strip()
                            ),
                        }
                        for template in templates
                        if isinstance(template, dict) and str(template.get("template_id", "")).strip()
                    ],
                }
            )
        except Exception as exc:
            entries.append(
                {
                    "bundle_path": str(bundle_path),
                    "error": str(exc),
                }
            )
    return entries


def create_world_game_template_bundle_draft(
    source_bundle: Path | Dict[str, Any],
    bundle_id: Optional[str] = None,
    label: Optional[str] = None,
    description: Optional[str] = None,
    content_version: Optional[str] = None,
    deterministic_version_seed: Optional[str] = None,
    tags: Optional[Sequence[str]] = None,
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,
) -> Dict[str, Any]:
    draft = load_world_game_template_bundle(source_bundle)
    metadata = draft.setdefault("bundle_metadata", {})

    metadata["status"] = "draft"
    metadata.pop("published_at", None)
    if bundle_id is not None:
        metadata["bundle_id"] = str(bundle_id)
    if label is not None:
        metadata["label"] = str(label)
    if description is not None:
        metadata["description"] = str(description)
    if content_version is not None:
        metadata["content_version"] = str(content_version)
    if deterministic_version_seed is not None:
        metadata["deterministic_version_seed"] = str(deterministic_version_seed)
    if tags is not None:
        metadata["tags"] = sorted({str(tag) for tag in tags if str(tag).strip()})
    if created_at is not None:
        metadata["created_at"] = str(created_at)
    if updated_at is not None:
        metadata["updated_at"] = str(updated_at)
    elif "updated_at" not in metadata:
        metadata["updated_at"] = metadata.get("created_at") or _utc_now()

    metadata["deterministic_version_hash"] = compute_world_game_template_bundle_hash(draft)
    return load_world_game_template_bundle(draft)


def _semantic_validate_world_game_template_bundle(bundle: Dict[str, Any]) -> List[Dict[str, str]]:
    errors: List[Dict[str, str]] = []

    try:
        normalized = _normalize_world_game_template_bundle(bundle)
    except Exception as exc:
        return [{"path": "$", "message": str(exc)}]

    metadata = normalized.get("bundle_metadata", {})
    declared_hash = str(metadata.get("deterministic_version_hash", "")).strip()
    try:
        expected_hash = compute_world_game_template_bundle_hash(normalized)
        if declared_hash != expected_hash:
            errors.append(
                {
                    "path": "$.bundle_metadata.deterministic_version_hash",
                    "message": "expected %s but found %s" % (expected_hash, declared_hash),
                }
            )
    except Exception as exc:
        errors.append(
            {
                "path": "$.bundle_metadata.deterministic_version_seed",
                "message": str(exc),
            }
        )

    indicator_registries = _as_id_map(normalized.get("indicator_registries", []), "registry_id")
    intervention_libraries = _as_id_map(normalized.get("intervention_libraries", []), "library_id")
    shock_libraries = _as_id_map(normalized.get("shock_libraries", []), "library_id")

    for template_index, template in enumerate(normalized.get("scenario_templates", [])):
        template_path = "$.scenario_templates[%d]" % template_index
        template_id = str(template.get("template_id", ""))

        try:
            defaults = _resolve_template_parameters(template, overrides=None)
        except Exception as exc:
            errors.append(
                {
                    "path": "%s.parameter_model.parameters" % template_path,
                    "message": str(exc),
                }
            )
            continue

        refs = [
            ("indicator_registry_ref_template", indicator_registries),
            ("intervention_library_ref_template", intervention_libraries),
            ("shock_library_ref_template", shock_libraries),
        ]
        for field_name, catalog in refs:
            try:
                rendered_ref = str(_render_template_value(template.get(field_name), defaults))
            except Exception as exc:
                errors.append(
                    {
                        "path": "%s.%s" % (template_path, field_name),
                        "message": str(exc),
                    }
                )
                continue
            if rendered_ref not in catalog:
                errors.append(
                    {
                        "path": "%s.%s" % (template_path, field_name),
                        "message": "references unknown id: %s" % rendered_ref,
                    }
                )

        try:
            instantiate_world_game_template_bundle(
                normalized,
                template_id=template_id,
                parameter_values=defaults,
            )
        except Exception as exc:
            errors.append(
                {
                    "path": template_path,
                    "message": "default instantiation failed: %s" % exc,
                }
            )

    return sorted(
        errors,
        key=lambda item: (str(item.get("path", "")), str(item.get("message", ""))),
    )


def validate_world_game_template_bundle_workflow(
    path_or_payload: Path | Dict[str, Any],
    schema_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    payload = _load_world_game_bundle_payload(path_or_payload)
    schema_errors = validate_world_game_template_bundle(payload, schema_dir=schema_dir)
    semantic_errors: List[Dict[str, str]] = []
    if not schema_errors:
        semantic_errors = _semantic_validate_world_game_template_bundle(payload)
    errors = sorted(
        schema_errors + semantic_errors,
        key=lambda item: (str(item.get("path", "")), str(item.get("message", ""))),
    )

    metadata = payload.get("bundle_metadata") if isinstance(payload.get("bundle_metadata"), dict) else {}
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "schema_errors": schema_errors,
        "semantic_errors": semantic_errors,
        "bundle_metadata": {
            "bundle_id": metadata.get("bundle_id"),
            "status": metadata.get("status"),
            "content_version": metadata.get("content_version"),
            "deterministic_version_hash": metadata.get("deterministic_version_hash"),
        },
    }


def publish_world_game_template_bundle(
    path_or_payload: Path | Dict[str, Any],
    published_at: Optional[str] = None,
    updated_at: Optional[str] = None,
    schema_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    payload = _load_world_game_bundle_payload(path_or_payload)
    report = validate_world_game_template_bundle_workflow(payload, schema_dir=schema_dir)
    if not report["valid"]:
        first_error = report["errors"][0]
        raise ValueError("cannot publish invalid template bundle at %s: %s" % (first_error["path"], first_error["message"]))

    published = load_world_game_template_bundle(payload, schema_dir=schema_dir)
    metadata = published.setdefault("bundle_metadata", {})

    publish_time = str(published_at or metadata.get("updated_at") or metadata.get("created_at") or _utc_now())
    metadata["status"] = "published"
    metadata["published_at"] = publish_time
    metadata["updated_at"] = str(updated_at or publish_time)
    metadata["deterministic_version_hash"] = compute_world_game_template_bundle_hash(published)

    final_report = validate_world_game_template_bundle_workflow(published, schema_dir=schema_dir)
    if not final_report["valid"]:
        first_error = final_report["errors"][0]
        raise ValueError(
            "published bundle validation failed at %s: %s" % (first_error["path"], first_error["message"])
        )

    bundle_hash = str(metadata["deterministic_version_hash"])
    published_bundle_id = "%s@%s" % (str(metadata.get("bundle_id", "")), bundle_hash.replace("sha256:", "")[:12])
    return {
        "bundle": published,
        "publication": {
            "published_bundle_id": published_bundle_id,
            "bundle_id": metadata.get("bundle_id"),
            "bundle_hash": bundle_hash,
            "published_at": metadata.get("published_at"),
            "status": metadata.get("status"),
        },
        "validation": final_report,
    }


def _coerce_template_parameter(parameter: Dict[str, Any], candidate: Any) -> Any:
    parameter_type = str(parameter.get("type"))
    name = str(parameter.get("name"))

    if parameter_type == "string":
        if not isinstance(candidate, str):
            raise ValueError("parameter %s must be a string" % name)
        if "min_length" in parameter and len(candidate) < int(parameter["min_length"]):
            raise ValueError("parameter %s must have length >= %d" % (name, int(parameter["min_length"])))
        if "max_length" in parameter and len(candidate) > int(parameter["max_length"]):
            raise ValueError("parameter %s must have length <= %d" % (name, int(parameter["max_length"])))
        if "enum" in parameter and candidate not in parameter["enum"]:
            raise ValueError("parameter %s must be one of %s" % (name, ", ".join(sorted(parameter["enum"]))))
        return candidate

    if parameter_type == "integer":
        if isinstance(candidate, bool):
            raise ValueError("parameter %s must be an integer" % name)
        if isinstance(candidate, int):
            value = candidate
        elif isinstance(candidate, float) and candidate.is_integer():
            value = int(candidate)
        elif isinstance(candidate, str) and candidate.strip().lstrip("-").isdigit():
            value = int(candidate.strip())
        else:
            raise ValueError("parameter %s must be an integer" % name)

        if "minimum" in parameter and value < int(parameter["minimum"]):
            raise ValueError("parameter %s must be >= %d" % (name, int(parameter["minimum"])))
        if "maximum" in parameter and value > int(parameter["maximum"]):
            raise ValueError("parameter %s must be <= %d" % (name, int(parameter["maximum"])))
        if "enum" in parameter and value not in parameter["enum"]:
            raise ValueError("parameter %s must be one of %s" % (name, ", ".join(str(item) for item in parameter["enum"])))
        return value

    if parameter_type == "number":
        if isinstance(candidate, bool):
            raise ValueError("parameter %s must be a number" % name)
        value = float(candidate)
        if "minimum" in parameter and value < float(parameter["minimum"]):
            raise ValueError("parameter %s must be >= %s" % (name, parameter["minimum"]))
        if "maximum" in parameter and value > float(parameter["maximum"]):
            raise ValueError("parameter %s must be <= %s" % (name, parameter["maximum"]))
        if "enum" in parameter:
            enum_values = [float(item) for item in parameter["enum"]]
            if value not in enum_values:
                raise ValueError("parameter %s must be one of %s" % (name, ", ".join(str(item) for item in parameter["enum"])))
        return value

    if parameter_type == "boolean":
        if not isinstance(candidate, bool):
            raise ValueError("parameter %s must be a boolean" % name)
        return candidate

    raise ValueError("unsupported parameter type for %s: %s" % (name, parameter_type))


def _resolve_template_parameters(
    template: Dict[str, Any],
    overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    provided = dict(overrides or {})
    parameters = template.get("parameter_model", {}).get("parameters", [])
    known_names = {str(item["name"]) for item in parameters}
    unknown_names = sorted(set(provided.keys()) - known_names)
    if unknown_names:
        raise ValueError("unknown template parameter(s): %s" % ", ".join(unknown_names))

    resolved: Dict[str, Any] = {}
    for definition in parameters:
        name = str(definition["name"])
        if name in provided:
            candidate = provided[name]
        elif "default" in definition:
            candidate = definition["default"]
        else:
            raise ValueError("missing required template parameter: %s" % name)
        resolved[name] = _coerce_template_parameter(definition, candidate)

    return {name: resolved[name] for name in sorted(resolved.keys())}


def _render_template_string(value: str, parameters: Dict[str, Any]) -> Any:
    matches = list(_TEMPLATE_PLACEHOLDER_PATTERN.finditer(value))
    if not matches:
        return value

    if len(matches) == 1 and matches[0].span() == (0, len(value)):
        key = matches[0].group(1)
        if key not in parameters:
            raise ValueError("template placeholder references unknown parameter: %s" % key)
        return deepcopy(parameters[key])

    rendered = value
    for match in matches:
        key = match.group(1)
        if key not in parameters:
            raise ValueError("template placeholder references unknown parameter: %s" % key)
        rendered = rendered.replace(match.group(0), str(parameters[key]))
    return rendered


def _render_template_value(value: Any, parameters: Dict[str, Any]) -> Any:
    if isinstance(value, str):
        return _render_template_string(value, parameters)
    if isinstance(value, list):
        return [_render_template_value(item, parameters) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _render_template_value(item, parameters)
            for key, item in value.items()
        }
    return deepcopy(value)


def _materialize_time_horizon(template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, int]:
    rendered = _render_template_value(template.get("time_horizon", {}), parameters)
    start_year = int(rendered["start_year"])
    years_per_turn = int(rendered["years_per_turn"])
    turn_count = int(rendered["turn_count"])
    if years_per_turn <= 0:
        raise ValueError("template time_horizon.years_per_turn must be > 0")
    if turn_count <= 0:
        raise ValueError("template time_horizon.turn_count must be > 0")
    return {
        "start_year": start_year,
        "years_per_turn": years_per_turn,
        "turn_count": turn_count,
    }


def _as_id_map(items: Sequence[Dict[str, Any]], key_field: str) -> Dict[str, Dict[str, Any]]:
    return {str(item[key_field]): item for item in items}


def _filter_interventions(
    interventions: Sequence[Dict[str, Any]],
    region_ids: Set[str],
    indicator_ids: Set[str],
) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    for source in interventions:
        intervention = deepcopy(source)
        intervention["applicable_regions"] = sorted(set(region for region in intervention.get("applicable_regions", []) if region in region_ids))
        intervention["direct_effects"] = sorted(
            [
                effect
                for effect in intervention.get("direct_effects", [])
                if str(effect.get("region_id")) in region_ids and str(effect.get("indicator_id")) in indicator_ids
            ],
            key=lambda item: (
                str(item.get("region_id", "")),
                str(item.get("indicator_id", "")),
                float(item.get("delta", 0.0)),
                float(item.get("multiplier", 1.0)),
            ),
        )
        intervention["tradeoffs"] = sorted(
            [
                effect
                for effect in intervention.get("tradeoffs", [])
                if str(effect.get("region_id")) in region_ids and str(effect.get("indicator_id")) in indicator_ids
            ],
            key=lambda item: (
                str(item.get("region_id", "")),
                str(item.get("indicator_id", "")),
                float(item.get("delta", 0.0)),
                str(item.get("note", "")),
            ),
        )
        if not intervention["applicable_regions"]:
            continue
        if not intervention["direct_effects"]:
            continue
        filtered.append(intervention)

    filtered = sorted(filtered, key=lambda item: str(item["intervention_id"]))
    valid_ids = {item["intervention_id"] for item in filtered}
    for item in filtered:
        item["prerequisites"] = [
            prereq
            for prereq in item.get("prerequisites", [])
            if prereq in valid_ids
        ]
    return filtered


def _filter_shocks(
    shocks: Sequence[Dict[str, Any]],
    region_ids: Set[str],
    indicator_ids: Set[str],
) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    for source in shocks:
        shock = deepcopy(source)
        shock["applicable_regions"] = sorted(set(region for region in shock.get("applicable_regions", []) if region in region_ids))
        shock["effects"] = sorted(
            [
                effect
                for effect in shock.get("effects", [])
                if str(effect.get("region_id")) in region_ids and str(effect.get("indicator_id")) in indicator_ids
            ],
            key=lambda item: (
                str(item.get("region_id", "")),
                str(item.get("indicator_id", "")),
                float(item.get("delta", 0.0)),
            ),
        )
        if not shock["applicable_regions"]:
            continue
        if not shock["effects"]:
            continue
        filtered.append(shock)
    return sorted(filtered, key=lambda item: str(item["shock_id"]))


def _materialize_network_fields(
    template: Dict[str, Any],
    parameters: Dict[str, Any],
    region_ids: Set[str],
    indicator_ids: Set[str],
) -> Dict[str, Any]:
    dependency_graph_template = template.get("dependency_graph_template")
    resource_stocks_template = template.get("resource_stocks_template")
    resource_flows_template = template.get("resource_flows_template")
    spillover_rules_template = template.get("spillover_rules_template")
    equity_dimensions_template = template.get("equity_dimensions_template")

    output: Dict[str, Any] = {}
    if dependency_graph_template is not None:
        graph = _render_template_value(dependency_graph_template, parameters)
        nodes = sorted(
            [
                node
                for node in graph.get("nodes", [])
                if str(node.get("region_id", "")) in region_ids
            ],
            key=lambda item: str(item.get("node_id", "")),
        )
        node_ids = {str(node.get("node_id")) for node in nodes}
        edges = sorted(
            [
                edge
                for edge in graph.get("edges", [])
                if str(edge.get("from_node_id", "")) in node_ids and str(edge.get("to_node_id", "")) in node_ids
            ],
            key=lambda item: str(item.get("edge_id", "")),
        )
        output["dependency_graph"] = {"nodes": nodes, "edges": edges}
    else:
        node_ids = set()

    if resource_stocks_template is not None:
        stocks = _render_template_value(resource_stocks_template, parameters)
        stocks = sorted(
            [
                stock
                for stock in stocks
                if str(stock.get("region_id", "")) in region_ids
                and str(stock.get("indicator_id", "")) in indicator_ids
                and (not node_ids or str(stock.get("node_id", "")) in node_ids)
            ],
            key=lambda item: str(item.get("stock_id", "")),
        )
        stock_ids = {str(stock.get("stock_id")) for stock in stocks}
        output["resource_stocks"] = stocks
    else:
        stock_ids = set()

    if resource_flows_template is not None:
        flows = _render_template_value(resource_flows_template, parameters)
        flows = sorted(
            [
                flow
                for flow in flows
                if str(flow.get("source_stock_id", "")) in stock_ids
                and str(flow.get("target_stock_id", "")) in stock_ids
                and (not node_ids or str(flow.get("from_node_id", "")) in node_ids)
                and (not node_ids or str(flow.get("to_node_id", "")) in node_ids)
            ],
            key=lambda item: str(item.get("flow_id", "")),
        )
        output["resource_flows"] = flows

    if spillover_rules_template is not None:
        rules = _render_template_value(spillover_rules_template, parameters)
        rules = sorted(
            [
                rule
                for rule in rules
                if (
                    (
                        str(rule.get("from_node_id", "")) in node_ids
                        and str(rule.get("to_node_id", "")) in node_ids
                    )
                    or (
                        str(rule.get("edge_id", "")) and not node_ids
                    )
                )
                and str(rule.get("source_indicator_id", "")) in indicator_ids
                and str(rule.get("target_indicator_id", "")) in indicator_ids
            ],
            key=lambda item: str(item.get("rule_id", "")),
        )
        output["spillover_rules"] = rules

    if equity_dimensions_template is not None:
        dimensions = _render_template_value(equity_dimensions_template, parameters)
        region_weights = {
            region_id: float(weight)
            for region_id, weight in dimensions.get("region_weights", {}).items()
            if region_id in region_ids
        }
        groups = []
        for group in dimensions.get("groups", []):
            members = sorted(set(member for member in group.get("region_ids", []) if member in region_ids))
            if not members:
                continue
            normalized_group = deepcopy(group)
            normalized_group["region_ids"] = members
            groups.append(normalized_group)
        dimensions["region_weights"] = region_weights
        dimensions["groups"] = sorted(groups, key=lambda item: str(item.get("group_id", "")))
        output["equity_dimensions"] = dimensions

    return output


def instantiate_world_game_template_bundle(
    bundle: Dict[str, Any] | Path,
    template_id: str,
    parameter_values: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    loaded_bundle = load_world_game_template_bundle(bundle)
    templates_by_id = _as_id_map(loaded_bundle.get("scenario_templates", []), "template_id")
    template = templates_by_id.get(template_id)
    if template is None:
        raise ValueError("unknown scenario template_id: %s" % template_id)

    parameters = _resolve_template_parameters(template, overrides=parameter_values)

    indicator_registry_ref = str(_render_template_value(template["indicator_registry_ref_template"], parameters))
    intervention_library_ref = str(_render_template_value(template["intervention_library_ref_template"], parameters))
    shock_library_ref = str(_render_template_value(template["shock_library_ref_template"], parameters))
    policy_pack_ref = str(_render_template_value(template["policy_pack_ref_template"], parameters))

    indicator_registries = _as_id_map(loaded_bundle.get("indicator_registries", []), "registry_id")
    intervention_libraries = _as_id_map(loaded_bundle.get("intervention_libraries", []), "library_id")
    shock_libraries = _as_id_map(loaded_bundle.get("shock_libraries", []), "library_id")

    indicator_registry = indicator_registries.get(indicator_registry_ref)
    if indicator_registry is None:
        raise ValueError("unknown indicator registry ref: %s" % indicator_registry_ref)
    intervention_library = intervention_libraries.get(intervention_library_ref)
    if intervention_library is None:
        raise ValueError("unknown intervention library ref: %s" % intervention_library_ref)
    shock_library = shock_libraries.get(shock_library_ref)
    if shock_library is None:
        raise ValueError("unknown shock library ref: %s" % shock_library_ref)

    region_pool = sorted(template.get("region_pool", []), key=lambda item: str(item["region_id"]))
    default_region_count = len(region_pool)
    region_count = int(parameters.get("region_count", default_region_count))
    if region_count <= 0:
        raise ValueError("parameter region_count must be >= 1")
    if region_count > len(region_pool):
        raise ValueError("parameter region_count=%d exceeds region_pool size=%d" % (region_count, len(region_pool)))
    selected_regions = region_pool[:region_count]
    region_ids = {item["region_id"] for item in selected_regions}

    indicators = sorted(indicator_registry.get("indicators", []), key=lambda item: str(item["indicator_id"]))
    indicator_ids = {item["indicator_id"] for item in indicators}

    baseline_indicators: Dict[str, Dict[str, float]] = {}
    for region in selected_regions:
        baseline_seed = region.get("baseline_indicators", {})
        baseline_indicators[region["region_id"]] = {
            indicator["indicator_id"]: float(baseline_seed.get(indicator["indicator_id"], 0.0))
            for indicator in indicators
        }

    interventions = _filter_interventions(
        intervention_library.get("interventions", []),
        region_ids=region_ids,
        indicator_ids=indicator_ids,
    )
    shocks = _filter_shocks(
        shock_library.get("shocks", []),
        region_ids=region_ids,
        indicator_ids=indicator_ids,
    )
    shock_ids = {item["shock_id"] for item in shocks}
    intervention_ids = {item["intervention_id"] for item in interventions}

    rendered_schedule = _render_template_value(template.get("shock_schedule_template", []), parameters)
    if not isinstance(rendered_schedule, list):
        raise ValueError("template shock_schedule_template must render to a list")

    time_horizon = _materialize_time_horizon(template, parameters)
    turn_count = int(time_horizon["turn_count"])
    shock_schedule: List[List[str]] = []
    for turn in rendered_schedule:
        if not isinstance(turn, list):
            raise ValueError("template shock_schedule_template turns must be arrays")
        resolved_turn = [shock_id for shock_id in turn if shock_id in shock_ids]
        shock_schedule.append(sorted(set(resolved_turn)))

    if len(shock_schedule) < turn_count:
        shock_schedule.extend([[] for _ in range(turn_count - len(shock_schedule))])
    if len(shock_schedule) > turn_count:
        shock_schedule = shock_schedule[:turn_count]

    rendered_weights = _render_template_value(template.get("weights_template", {}), parameters)
    if not isinstance(rendered_weights, dict):
        raise ValueError("template weights_template must render to an object")
    weights: Dict[str, float] = {}
    for indicator in indicators:
        indicator_id = indicator["indicator_id"]
        if indicator_id in rendered_weights:
            weights[indicator_id] = float(rendered_weights[indicator_id])
        else:
            weights[indicator_id] = float(indicator.get("weight", 1.0))

    rendered_strategies = _render_template_value(template.get("strategy_templates", []), parameters)
    strategies = []
    if rendered_strategies:
        for strategy in rendered_strategies:
            selected = [item for item in strategy.get("selected_interventions", []) if item in intervention_ids]
            if not selected:
                continue
            normalized_strategy = deepcopy(strategy)
            normalized_strategy["selected_interventions"] = selected
            strategies.append(normalized_strategy)
    strategies = sorted(strategies, key=lambda item: str(item.get("strategy_id", "")))

    network_fields = _materialize_network_fields(
        template=template,
        parameters=parameters,
        region_ids=region_ids,
        indicator_ids=indicator_ids,
    )

    metadata_template = template.get("metadata_template") or {}
    rendered_metadata = _render_template_value(metadata_template, parameters)
    if not isinstance(rendered_metadata, dict):
        raise ValueError("template metadata_template must render to an object")
    rendered_metadata["template_bundle_id"] = loaded_bundle["bundle_metadata"]["bundle_id"]
    rendered_metadata["template_id"] = template_id
    rendered_metadata["bundle_version_hash"] = loaded_bundle["bundle_metadata"]["deterministic_version_hash"]
    rendered_metadata["instantiation_parameters"] = deepcopy(parameters)

    scenario_payload: Dict[str, Any] = {
        "scenario_id": str(_render_template_value(template["scenario_id_template"], parameters)),
        "label": str(template["label"]),
        "description": str(template["description"]),
        "baseline_version": str(_render_template_value(template["baseline_version_template"], parameters)),
        "metadata": rendered_metadata,
        "time_horizon": time_horizon,
        "regions": [
            {
                "region_id": item["region_id"],
                "label": item["label"],
                **({"description": item["description"]} if item.get("description") else {}),
            }
            for item in selected_regions
        ],
        "indicator_definitions": indicators,
        "baseline_indicators": baseline_indicators,
        "interventions": interventions,
        "shocks": shocks,
        "shock_schedule": shock_schedule,
        "policy_pack_ref": policy_pack_ref,
        "weights": weights,
        "success_criteria": _render_template_value(template.get("success_criteria_template", {}), parameters),
        "strategies": strategies,
    }
    scenario_payload.update(network_fields)

    normalized_scenario = load_world_game_scenario(scenario_payload)
    instantiation_payload = {
        "bundle_id": loaded_bundle["bundle_metadata"]["bundle_id"],
        "bundle_hash": loaded_bundle["bundle_metadata"]["deterministic_version_hash"],
        "template_id": template_id,
        "parameters": parameters,
    }
    instantiation_id = "inst.%s" % hashlib.sha256(_stable_json(instantiation_payload).encode("utf-8")).hexdigest()[:16]
    return {
        "instantiation_id": instantiation_id,
        "scenario": normalized_scenario,
        "scenario_payload": deepcopy(scenario_payload),
        "bundle_metadata": deepcopy(loaded_bundle["bundle_metadata"]),
        "template_id": template_id,
        "parameters": deepcopy(parameters),
    }


def normalize_scenario_definition(scenario: Dict[str, Any]) -> Dict[str, Any]:
    required = {
        "scenario_id",
        "label",
        "description",
        "baseline_version",
        "time_horizon",
        "regions",
        "indicator_definitions",
        "baseline_indicators",
        "interventions",
        "shocks",
    }
    missing = sorted(required - set(scenario.keys()))
    if missing:
        raise ValueError("scenario missing required fields: %s" % ", ".join(missing))

    normalized = deepcopy(scenario)
    normalized["regions"] = sorted(
        normalized.get("regions", []),
        key=lambda item: str(item.get("region_id", "")),
    )
    region_ids = [str(item["region_id"]) for item in normalized["regions"]]
    region_id_set = set(region_ids)
    if len(region_id_set) != len(region_ids):
        raise ValueError("scenario.regions contains duplicate region_id values")

    indicator_defs = sorted(
        normalized.get("indicator_definitions", []),
        key=lambda item: str(item.get("indicator_id", "")),
    )
    if not indicator_defs:
        raise ValueError("scenario must define at least one indicator")

    indicator_ids = [str(item["indicator_id"]) for item in indicator_defs]
    indicator_id_set = set(indicator_ids)
    if len(indicator_id_set) != len(indicator_ids):
        raise ValueError("scenario.indicator_definitions contains duplicate indicator_id values")

    indicator_defs_by_id = {item["indicator_id"]: item for item in indicator_defs}

    baseline = normalized.get("baseline_indicators", {})
    for region_id in region_ids:
        region_values = baseline.setdefault(region_id, {})
        for indicator_id in indicator_ids:
            region_values.setdefault(indicator_id, 0.0)
            region_values[indicator_id] = float(region_values[indicator_id])

    interventions = sorted(
        normalized.get("interventions", []),
        key=lambda item: str(item.get("intervention_id", "")),
    )
    intervention_by_id = {item["intervention_id"]: item for item in interventions}

    for intervention in interventions:
        intervention_id = intervention["intervention_id"]
        for effect in intervention.get("direct_effects", []):
            region_id = str(effect.get("region_id", ""))
            indicator_id = str(effect.get("indicator_id", ""))
            if region_id not in region_id_set:
                raise ValueError(
                    "intervention %s direct_effect references unknown region_id: %s" % (intervention_id, region_id)
                )
            if indicator_id not in indicator_id_set:
                raise ValueError(
                    "intervention %s direct_effect references unknown indicator_id: %s"
                    % (intervention_id, indicator_id)
                )
        for tradeoff in intervention.get("tradeoffs", []):
            region_id = str(tradeoff.get("region_id", ""))
            indicator_id = str(tradeoff.get("indicator_id", ""))
            if region_id not in region_id_set:
                raise ValueError(
                    "intervention %s tradeoff references unknown region_id: %s" % (intervention_id, region_id)
                )
            if indicator_id not in indicator_id_set:
                raise ValueError(
                    "intervention %s tradeoff references unknown indicator_id: %s" % (intervention_id, indicator_id)
                )

    shocks = sorted(
        normalized.get("shocks", []),
        key=lambda item: str(item.get("shock_id", "")),
    )
    shock_by_id = {item["shock_id"]: item for item in shocks}
    for shock in shocks:
        shock_id = shock["shock_id"]
        for effect in shock.get("effects", []):
            region_id = str(effect.get("region_id", ""))
            indicator_id = str(effect.get("indicator_id", ""))
            if region_id not in region_id_set:
                raise ValueError("shock %s effect references unknown region_id: %s" % (shock_id, region_id))
            if indicator_id not in indicator_id_set:
                raise ValueError("shock %s effect references unknown indicator_id: %s" % (shock_id, indicator_id))

    weights = {key: float(value) for key, value in normalized.get("weights", {}).items()}
    for indicator in indicator_defs:
        indicator_id = indicator["indicator_id"]
        if indicator_id not in weights:
            weights[indicator_id] = float(indicator.get("weight", 1.0))

    time_horizon = normalized["time_horizon"]
    for field in ("start_year", "years_per_turn", "turn_count"):
        if field not in time_horizon:
            raise ValueError("time_horizon missing field: %s" % field)

    dependency_graph = _normalize_dependency_graph(normalized.get("dependency_graph"), region_ids=region_ids)
    resource_stocks = _normalize_resource_stocks(
        normalized.get("resource_stocks"),
        dependency_graph=dependency_graph,
        region_ids=region_ids,
        indicator_ids=indicator_ids,
    )
    resource_flows = _normalize_resource_flows(
        normalized.get("resource_flows"),
        dependency_graph=dependency_graph,
        resource_stocks=resource_stocks,
    )
    spillover_rules = _normalize_spillover_rules(
        normalized.get("spillover_rules"),
        dependency_graph=dependency_graph,
        indicator_ids=indicator_ids,
    )
    equity_dimensions = _normalize_equity_dimensions(normalized.get("equity_dimensions"), region_ids=region_ids)

    normalized["indicator_definitions"] = indicator_defs
    normalized["indicator_ids"] = indicator_ids
    normalized["indicator_defs_by_id"] = indicator_defs_by_id
    normalized["region_ids"] = region_ids
    normalized["interventions"] = interventions
    normalized["interventions_by_id"] = intervention_by_id
    normalized["shocks"] = shocks
    normalized["shocks_by_id"] = shock_by_id
    normalized["weights"] = weights
    normalized.setdefault("shock_schedule", [])
    normalized.setdefault("metadata", {})
    normalized.setdefault("success_criteria", {})
    normalized.setdefault("strategies", [])

    normalized["dependency_graph"] = dependency_graph
    normalized["resource_stocks"] = resource_stocks
    normalized["resource_flows"] = resource_flows
    normalized["spillover_rules"] = spillover_rules
    normalized["equity_dimensions"] = equity_dimensions
    normalized["has_network_contract"] = any(
        key in scenario for key in ("dependency_graph", "resource_stocks", "resource_flows", "spillover_rules")
    )
    normalized["has_equity_contract"] = "equity_dimensions" in scenario

    return normalized


def _initialize_resource_stock_state(scenario: Dict[str, Any]) -> Dict[str, float]:
    stocks: Dict[str, float] = {}
    for stock in scenario.get("resource_stocks", {}).get("items", []):
        stocks[stock["stock_id"]] = float(stock["baseline"])
    return stocks


def initialize_baseline_state(
    scenario: Dict[str, Any],
    branch_id: str = "baseline",
    parent_branch_id: Optional[str] = None,
) -> Dict[str, Any]:
    state = {
        "scenario_id": scenario["scenario_id"],
        "branch_id": branch_id,
        "parent_branch_id": parent_branch_id,
        "turn": 0,
        "regions": [region["region_id"] for region in scenario["regions"]],
        "indicator_definitions": deepcopy(scenario["indicator_definitions"]),
        "indicator_values": deepcopy(scenario["baseline_indicators"]),
        "resource_stocks": _initialize_resource_stock_state(scenario),
        "active_interventions": [],
        "active_shocks": [],
        "applied_interventions": [],
        "realized_shocks": [],
        "event_log": [
            {
                "event_id": "evt.%s.baseline" % scenario["scenario_id"],
                "event_type": "wg_baseline_loaded",
                "turn": 0,
                "sequence": 0,
                "payload": {
                    "scenario_id": scenario["scenario_id"],
                    "baseline_version": scenario["baseline_version"],
                },
            }
        ],
        "pending_policy_results": [],
        "network_diagnostics_history": [],
        "equity_history": [],
    }
    state["scorecard"] = compute_scorecard(state, scenario)
    baseline_equity = build_equity_report(state, scenario)
    state["latest_equity_report"] = deepcopy(baseline_equity)
    state["equity_history"] = [deepcopy(baseline_equity)]
    state["latest_network_diagnostics"] = {
        "mode": "baseline",
        "turn_index": 0,
        "stock_deltas": [],
        "flow_transfers": [],
        "saturated_edges": [],
        "unmet_demand": [],
        "spillover_contributions": [],
        "conservation_check": {
            "total_before_flows": _round(sum(state["resource_stocks"].values())),
            "total_after_flows": _round(sum(state["resource_stocks"].values())),
            "expected_loss": 0.0,
            "balance_error": 0.0,
        },
        "stock_levels": {stock_id: _round(value) for stock_id, value in sorted(state["resource_stocks"].items())},
    }
    return state


def _indicator_bounds(indicator_def: Dict[str, Any]) -> Tuple[float, float]:
    low = float(indicator_def.get("min_value", 0.0))
    high = float(indicator_def.get("max_value", 100.0))
    if high <= low:
        high = low + 1.0
    return low, high


def compute_indicator_score(indicator_def: Dict[str, Any], raw_value: float) -> float:
    direction = indicator_def.get("direction", "higher_is_better")
    low, high = _indicator_bounds(indicator_def)
    value = float(raw_value)

    if direction == "higher_is_better":
        return _clamp(((value - low) / (high - low)) * 100.0)

    if direction == "lower_is_better":
        return _clamp(((high - value) / (high - low)) * 100.0)

    target_band = indicator_def.get("target_band") or {}
    band_min = float(target_band.get("min", indicator_def.get("target", low)))
    band_max = float(target_band.get("max", indicator_def.get("target", high)))
    if band_max < band_min:
        band_max = band_min

    if band_min <= value <= band_max:
        return 100.0

    distance = min(abs(value - band_min), abs(value - band_max))
    scale = max(high - low, 1.0)
    return _clamp(100.0 - ((distance / scale) * 100.0))


def _indicator_region_values(state: Dict[str, Any], indicator_id: str) -> List[float]:
    values = []
    for region_id in state["regions"]:
        region_values = state["indicator_values"].get(region_id, {})
        values.append(float(region_values.get(indicator_id, 0.0)))
    return values


def compute_scorecard(state: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    weights = dict(scenario.get("weights", {}))
    weight_total = float(sum(weights.values()))
    if weight_total <= 0:
        weights = {indicator_id: 1.0 for indicator_id in scenario["indicator_ids"]}
        weight_total = float(len(weights))

    indicator_scores: Dict[str, float] = {}
    raw_averages: Dict[str, float] = {}

    for indicator in scenario["indicator_definitions"]:
        indicator_id = indicator["indicator_id"]
        values = _indicator_region_values(state, indicator_id)
        raw_average = sum(values) / max(len(values), 1)
        raw_averages[indicator_id] = _round(raw_average)
        indicator_scores[indicator_id] = _round(compute_indicator_score(indicator, raw_average))

    composite = 0.0
    for indicator_id, normalized in indicator_scores.items():
        weight = float(weights.get(indicator_id, 0.0))
        composite += normalized * (weight / weight_total)

    return {
        "indicator_scores": indicator_scores,
        "raw_averages": raw_averages,
        "composite_score": _round(_clamp(composite)),
    }


def _resolve_indicator_value(
    state: Dict[str, Any],
    scenario: Dict[str, Any],
    region_id: str,
    indicator_id: str,
) -> float:
    if region_id not in state["indicator_values"]:
        state["indicator_values"][region_id] = {key: 0.0 for key in scenario["indicator_ids"]}
    if indicator_id not in state["indicator_values"][region_id]:
        state["indicator_values"][region_id][indicator_id] = 0.0
    return float(state["indicator_values"][region_id][indicator_id])


def _apply_effect(state: Dict[str, Any], scenario: Dict[str, Any], effect: Dict[str, Any]) -> None:
    region_id = effect["region_id"]
    indicator_id = effect["indicator_id"]
    current = _resolve_indicator_value(state, scenario, region_id, indicator_id)

    multiplier = float(effect.get("multiplier", 1.0))
    delta = float(effect.get("delta", 0.0))
    next_value = (current * multiplier) + delta

    indicator_def = scenario["indicator_defs_by_id"][indicator_id]
    low, high = _indicator_bounds(indicator_def)
    state["indicator_values"][region_id][indicator_id] = _clamp(next_value, low, high)


def _intervention_effects(intervention: Dict[str, Any]) -> List[Dict[str, Any]]:
    effects = [
        {
            "region_id": item["region_id"],
            "indicator_id": item["indicator_id"],
            "delta": float(item.get("delta", 0.0)),
            "multiplier": float(item.get("multiplier", 1.0)),
        }
        for item in intervention.get("direct_effects", [])
    ]
    for item in intervention.get("tradeoffs", []):
        effects.append(
            {
                "region_id": item["region_id"],
                "indicator_id": item["indicator_id"],
                "delta": float(item.get("delta", 0.0)),
                "multiplier": 1.0,
            }
        )
    return _sorted_effects(effects)


def _shock_effects(shock: Dict[str, Any]) -> List[Dict[str, Any]]:
    effects = [
        {
            "region_id": item["region_id"],
            "indicator_id": item["indicator_id"],
            "delta": float(item.get("delta", 0.0)),
            "multiplier": 1.0,
        }
        for item in shock.get("effects", [])
    ]
    return _sorted_effects(effects)


def apply_intervention(state: Dict[str, Any], intervention: Dict[str, Any], turn_index: int) -> Dict[str, Any]:
    entry = {
        "entry_id": intervention["intervention_id"],
        "start_turn": int(turn_index) + int(intervention.get("latency_turns", 0)),
        "remaining_turns": int(intervention.get("duration_turns", 1)),
        "effects": _intervention_effects(intervention),
        "cost": float(intervention.get("cost", {}).get("amount", 0.0)),
    }
    state["active_interventions"].append(entry)
    return entry


def apply_shock(state: Dict[str, Any], shock: Dict[str, Any], turn_index: int) -> Dict[str, Any]:
    entry = {
        "entry_id": shock["shock_id"],
        "start_turn": int(shock.get("start_turn", turn_index)),
        "remaining_turns": int(shock.get("duration_turns", 1)),
        "effects": _shock_effects(shock),
    }
    state["active_shocks"].append(entry)
    return entry


def _apply_active_entries(
    state: Dict[str, Any],
    scenario: Dict[str, Any],
    turn_index: int,
    entries: List[Dict[str, Any]],
) -> List[str]:
    applied: List[str] = []
    for entry in sorted(entries, key=lambda item: str(item["entry_id"])):
        if turn_index < int(entry["start_turn"]):
            continue
        if int(entry["remaining_turns"]) <= 0:
            continue

        for effect in _sorted_effects(entry.get("effects", [])):
            _apply_effect(state, scenario, effect)

        entry["remaining_turns"] = int(entry["remaining_turns"]) - 1
        applied.append(str(entry["entry_id"]))

    entries[:] = [entry for entry in entries if int(entry["remaining_turns"]) > 0]
    return applied


def _build_policy_proposal(
    scenario: Dict[str, Any],
    turn_index: int,
    intervention_ids: Sequence[str],
    shock_ids: Sequence[str],
    projected_state: Dict[str, Any],
) -> Dict[str, Any]:
    projected_region_scores = deepcopy(projected_state["indicator_values"])
    projected_composite = float(projected_state["scorecard"]["composite_score"])

    total_cost = 0.0
    affected_regions = set()
    for intervention_id in intervention_ids:
        intervention = scenario["interventions_by_id"][intervention_id]
        total_cost += float(intervention.get("cost", {}).get("amount", 0.0))
        affected_regions.update(intervention.get("applicable_regions", []))

    for shock_id in shock_ids:
        shock = scenario["shocks_by_id"][shock_id]
        affected_regions.update(shock.get("applicable_regions", []))

    latest_network = projected_state.get("latest_network_diagnostics", {})
    unmet_demand_total = sum(float(item.get("amount", 0.0)) for item in latest_network.get("unmet_demand", []))

    return {
        "proposal_id": "proposal.world-game.turn-%d" % turn_index,
        "proposed_action": {
            "action_type": "apply_world_game_turn",
            "parameters": {
                "turn_index": turn_index,
                "intervention_ids": list(intervention_ids),
                "shock_ids": list(shock_ids),
                "projected_indicator_values": projected_region_scores,
                "projected_indicator_scores": deepcopy(projected_state["scorecard"]["indicator_scores"]),
                "projected_composite_score": projected_composite,
                "projected_equity": deepcopy(projected_state.get("latest_equity_report", {})),
                "network_unmet_demand": _round(unmet_demand_total),
                "total_cost": total_cost,
                "affected_region_count": len(affected_regions),
            },
        },
    }


def _policy_to_dict(report: Optional[PolicyReport]) -> Optional[Dict[str, Any]]:
    if report is None:
        return None
    return report.as_dict()


def _network_model_enabled(scenario: Dict[str, Any]) -> bool:
    return bool(scenario.get("resource_stocks", {}).get("items") or scenario.get("resource_flows", {}).get("items"))


def _update_resource_stocks(
    state: Dict[str, Any],
    scenario: Dict[str, Any],
) -> List[Dict[str, Any]]:
    deltas: List[Dict[str, Any]] = []
    stocks = scenario.get("resource_stocks", {}).get("items", [])
    if not stocks:
        return deltas

    for stock in stocks:
        stock_id = stock["stock_id"]
        current = float(state["resource_stocks"].get(stock_id, stock["baseline"]))
        baseline_indicator = float(
            scenario["baseline_indicators"].get(stock["region_id"], {}).get(stock["indicator_id"], 0.0)
        )
        current_indicator = float(
            state["indicator_values"].get(stock["region_id"], {}).get(stock["indicator_id"], baseline_indicator)
        )

        delta = float(stock.get("regen_rate", 0.0)) - float(stock.get("demand_rate", 0.0))
        delta += (current_indicator - baseline_indicator) * float(stock.get("response_factor", 0.0))

        next_value = _clamp(current + delta, stock["min_bound"], stock["max_bound"])
        state["resource_stocks"][stock_id] = next_value
        deltas.append(
            {
                "stock_id": stock_id,
                "region_id": stock["region_id"],
                "indicator_id": stock["indicator_id"],
                "before": _round(current),
                "after": _round(next_value),
                "delta": _round(next_value - current),
            }
        )

    return deltas


def _run_resource_flows(
    state: Dict[str, Any],
    scenario: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    flow_transfers: List[Dict[str, Any]] = []
    saturated_edges: List[Dict[str, Any]] = []
    unmet_demand: List[Dict[str, Any]] = []

    flows = scenario.get("resource_flows", {}).get("items", [])
    stock_by_id = scenario.get("resource_stocks", {}).get("by_id", {})
    if not flows:
        total = float(sum(state.get("resource_stocks", {}).values()))
        return flow_transfers, saturated_edges, unmet_demand, {
            "total_before_flows": _round(total),
            "total_after_flows": _round(total),
            "expected_loss": 0.0,
            "balance_error": 0.0,
        }

    total_before_flows = float(sum(state.get("resource_stocks", {}).values()))
    expected_loss = 0.0

    for flow in flows:
        source_stock = stock_by_id[flow["source_stock_id"]]
        target_stock = stock_by_id[flow["target_stock_id"]]

        source_before = float(state["resource_stocks"].get(source_stock["stock_id"], source_stock["baseline"]))
        target_before = float(state["resource_stocks"].get(target_stock["stock_id"], target_stock["baseline"]))

        target_gap = max(0.0, float(target_stock["max_bound"]) - target_before)
        loss_factor = float(flow["loss_factor"])
        retained_ratio = max(0.0, 1.0 - loss_factor)

        if retained_ratio <= 0:
            required_source_for_gap = 0.0
        else:
            required_source_for_gap = target_gap / retained_ratio

        transfer = min(float(flow["capacity"]), source_before, required_source_for_gap)
        transfer = max(0.0, transfer)
        delivered = transfer * retained_ratio
        expected_loss += transfer - delivered

        source_after = source_before - transfer
        target_after = _clamp(target_before + delivered, float(target_stock["min_bound"]), float(target_stock["max_bound"]))

        state["resource_stocks"][source_stock["stock_id"]] = source_after
        state["resource_stocks"][target_stock["stock_id"]] = target_after

        indicator_delta = delivered * float(flow.get("indicator_conversion", 1.0))
        if indicator_delta:
            _apply_effect(
                state,
                scenario,
                {
                    "region_id": target_stock["region_id"],
                    "indicator_id": target_stock["indicator_id"],
                    "delta": indicator_delta,
                    "multiplier": 1.0,
                },
            )

        unmet = max(0.0, target_gap - delivered)

        transfer_entry = {
            "flow_id": flow["flow_id"],
            "edge_id": flow.get("edge_id"),
            "from_node_id": flow["from_node_id"],
            "to_node_id": flow["to_node_id"],
            "source_stock_id": source_stock["stock_id"],
            "target_stock_id": target_stock["stock_id"],
            "capacity": _round(flow["capacity"]),
            "transfer": _round(transfer),
            "delivered": _round(delivered),
            "loss_factor": _round(loss_factor),
            "indicator_delta": _round(indicator_delta),
        }
        flow_transfers.append(transfer_entry)

        if flow["capacity"] > 0 and transfer >= float(flow["capacity"]) - 1e-9:
            saturated_edges.append(
                {
                    "flow_id": flow["flow_id"],
                    "edge_id": flow.get("edge_id"),
                    "from_node_id": flow["from_node_id"],
                    "to_node_id": flow["to_node_id"],
                    "capacity": _round(flow["capacity"]),
                    "transfer": _round(transfer),
                    "utilization": _round(transfer / float(flow["capacity"])),
                }
            )

        if unmet > 0:
            unmet_demand.append(
                {
                    "flow_id": flow["flow_id"],
                    "target_stock_id": target_stock["stock_id"],
                    "region_id": target_stock["region_id"],
                    "amount": _round(unmet),
                }
            )

    total_after_flows = float(sum(state.get("resource_stocks", {}).values()))
    balance_error = (total_before_flows - total_after_flows) - expected_loss

    conservation = {
        "total_before_flows": _round(total_before_flows),
        "total_after_flows": _round(total_after_flows),
        "expected_loss": _round(expected_loss),
        "balance_error": _round(balance_error),
    }
    return flow_transfers, saturated_edges, unmet_demand, conservation


def _apply_spillovers(
    state: Dict[str, Any],
    scenario: Dict[str, Any],
) -> List[Dict[str, Any]]:
    contributions: List[Dict[str, Any]] = []
    rules = scenario.get("spillover_rules", {}).get("items", [])
    if not rules:
        return contributions

    nodes_by_id = scenario.get("dependency_graph", {}).get("nodes_by_id", {})
    for rule in rules:
        from_region = nodes_by_id[rule["from_node_id"]]["region_id"]
        to_region = nodes_by_id[rule["to_node_id"]]["region_id"]

        source_indicator = rule["source_indicator_id"]
        target_indicator = rule["target_indicator_id"]

        current_source = float(state["indicator_values"].get(from_region, {}).get(source_indicator, 0.0))
        baseline_source = float(
            scenario["baseline_indicators"].get(from_region, {}).get(source_indicator, current_source)
        )
        source_delta = current_source - baseline_source
        contribution = source_delta * float(rule["coefficient"])

        max_abs_transfer = rule.get("max_abs_transfer")
        if max_abs_transfer is not None:
            contribution = _clamp(contribution, -float(max_abs_transfer), float(max_abs_transfer))

        if contribution:
            _apply_effect(
                state,
                scenario,
                {
                    "region_id": to_region,
                    "indicator_id": target_indicator,
                    "delta": contribution,
                    "multiplier": 1.0,
                },
            )

        contributions.append(
            {
                "rule_id": rule["rule_id"],
                "from_node_id": rule["from_node_id"],
                "to_node_id": rule["to_node_id"],
                "source_region_id": from_region,
                "target_region_id": to_region,
                "source_indicator_id": source_indicator,
                "target_indicator_id": target_indicator,
                "source_delta": _round(source_delta),
                "coefficient": _round(rule["coefficient"]),
                "contribution": _round(contribution),
            }
        )

    return contributions


def _run_network_pipeline(state: Dict[str, Any], scenario: Dict[str, Any], turn_index: int) -> Dict[str, Any]:
    if not _network_model_enabled(scenario):
        return {
            "mode": "direct_effects_only",
            "turn_index": turn_index,
            "stock_deltas": [],
            "flow_transfers": [],
            "saturated_edges": [],
            "unmet_demand": [],
            "spillover_contributions": [],
            "conservation_check": {
                "total_before_flows": _round(sum(state.get("resource_stocks", {}).values())),
                "total_after_flows": _round(sum(state.get("resource_stocks", {}).values())),
                "expected_loss": 0.0,
                "balance_error": 0.0,
            },
            "stock_levels": {stock_id: _round(value) for stock_id, value in sorted(state.get("resource_stocks", {}).items())},
        }

    stock_deltas = _update_resource_stocks(state, scenario)
    flow_transfers, saturated_edges, unmet_demand, conservation = _run_resource_flows(state, scenario)
    spillover_contributions = _apply_spillovers(state, scenario)

    diagnostics = {
        "mode": "networked_propagation",
        "turn_index": turn_index,
        "stock_deltas": stock_deltas,
        "flow_transfers": flow_transfers,
        "saturated_edges": saturated_edges,
        "unmet_demand": unmet_demand,
        "spillover_contributions": spillover_contributions,
        "conservation_check": conservation,
        "stock_levels": {stock_id: _round(value) for stock_id, value in sorted(state.get("resource_stocks", {}).items())},
    }
    return diagnostics


def _compute_region_outcomes(values_by_region: Dict[str, Dict[str, Any]], scenario: Dict[str, Any]) -> Dict[str, float]:
    weights = dict(scenario.get("weights", {}))
    weight_total = float(sum(weights.values()))
    if weight_total <= 0:
        weights = {indicator_id: 1.0 for indicator_id in scenario["indicator_ids"]}
        weight_total = float(len(weights))

    outcomes: Dict[str, float] = {}
    for region_id in scenario["region_ids"]:
        region_values = values_by_region.get(region_id, {})
        total = 0.0
        for indicator in scenario["indicator_definitions"]:
            indicator_id = indicator["indicator_id"]
            raw_value = float(region_values.get(indicator_id, 0.0))
            score = compute_indicator_score(indicator, raw_value)
            weight = float(weights.get(indicator_id, 0.0))
            total += score * (weight / weight_total)
        outcomes[region_id] = _round(_clamp(total))
    return outcomes


def build_equity_report(state: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    region_ids = scenario["region_ids"]
    dimensions = scenario.get("equity_dimensions", {})
    region_weights = dict(dimensions.get("region_weights", {region_id: 1.0 for region_id in region_ids}))
    region_weights = _normalized_weight_map(region_ids, region_weights)

    current_outcomes = _compute_region_outcomes(state.get("indicator_values", {}), scenario)
    baseline_outcomes = _compute_region_outcomes(scenario.get("baseline_indicators", {}), scenario)

    weight_total = float(sum(region_weights.values()))
    weighted_mean = sum(current_outcomes[region_id] * region_weights[region_id] for region_id in region_ids) / max(
        weight_total, 1.0
    )
    baseline_weighted_mean = sum(
        baseline_outcomes[region_id] * region_weights[region_id] for region_id in region_ids
    ) / max(weight_total, 1.0)

    values = [current_outcomes[region_id] for region_id in region_ids]
    spread = max(values) - min(values) if values else 0.0
    weighted_variance = (
        sum(region_weights[region_id] * ((current_outcomes[region_id] - weighted_mean) ** 2) for region_id in region_ids)
        / max(weight_total, 1.0)
    )

    per_region = []
    for region_id in region_ids:
        delta_vs_baseline = current_outcomes[region_id] - baseline_outcomes[region_id]
        per_region.append(
            {
                "region_id": region_id,
                "normalized_outcome": _round(current_outcomes[region_id]),
                "baseline_normalized_outcome": _round(baseline_outcomes[region_id]),
                "delta_vs_baseline": _round(delta_vs_baseline),
                "weight": _round(region_weights[region_id]),
            }
        )

    winners = sorted(
        [
            {"region_id": item["region_id"], "delta_vs_baseline": item["delta_vs_baseline"]}
            for item in per_region
            if item["delta_vs_baseline"] > 0
        ],
        key=lambda item: (-float(item["delta_vs_baseline"]), str(item["region_id"])),
    )
    losers = sorted(
        [
            {"region_id": item["region_id"], "delta_vs_baseline": item["delta_vs_baseline"]}
            for item in per_region
            if item["delta_vs_baseline"] < 0
        ],
        key=lambda item: (float(item["delta_vs_baseline"]), str(item["region_id"])),
    )

    group_summaries = []
    for group in dimensions.get("groups", []):
        members = list(group["region_ids"])
        if not members:
            continue
        group_weight_total = sum(region_weights[region_id] for region_id in members)
        group_outcome = sum(current_outcomes[region_id] * region_weights[region_id] for region_id in members) / max(
            group_weight_total, 1.0
        )
        entry = {
            "group_id": group["group_id"],
            "region_ids": members,
            "weight": _round(group.get("weight", 1.0)),
            "normalized_outcome": _round(group_outcome),
        }
        if group.get("baseline_target") is not None:
            baseline_target = float(group["baseline_target"])
            entry["baseline_target"] = _round(baseline_target)
            entry["delta_vs_target"] = _round(group_outcome - baseline_target)
        group_summaries.append(entry)

    baseline_targets = dimensions.get("baseline_targets", {})
    target_gap = {}
    if "disparity_spread" in baseline_targets:
        target_gap["disparity_spread"] = _round(spread - float(baseline_targets["disparity_spread"]))
    if "weighted_variance" in baseline_targets:
        target_gap["weighted_variance"] = _round(weighted_variance - float(baseline_targets["weighted_variance"]))

    return {
        "weighted_mean_outcome": _round(weighted_mean),
        "baseline_weighted_mean_outcome": _round(baseline_weighted_mean),
        "equity_trend_vs_baseline": _round(weighted_mean - baseline_weighted_mean),
        "disparity_index": {
            "spread": _round(spread),
            "weighted_variance": _round(weighted_variance),
        },
        "per_region": sorted(per_region, key=lambda item: str(item["region_id"])),
        "groups": sorted(group_summaries, key=lambda item: str(item["group_id"])),
        "winners": winners,
        "losers": losers,
        "target_gap": target_gap,
    }


def scenario_network_summary(scenario: Dict[str, Any]) -> Dict[str, Any]:
    graph = scenario.get("dependency_graph", {})
    stocks = scenario.get("resource_stocks", {})
    flows = scenario.get("resource_flows", {})
    spillovers = scenario.get("spillover_rules", {})
    has_config = bool(graph.get("nodes") or stocks.get("items") or flows.get("items") or spillovers.get("items"))

    return {
        "enabled": has_config,
        "node_count": len(graph.get("nodes", [])),
        "edge_count": len(graph.get("edges", [])),
        "stock_count": len(stocks.get("items", [])),
        "flow_count": len(flows.get("items", [])),
        "spillover_rule_count": len(spillovers.get("items", [])),
        "topological_order": list(graph.get("topological_order", [])),
    }


def scenario_equity_summary(scenario: Dict[str, Any]) -> Dict[str, Any]:
    dimensions = scenario.get("equity_dimensions", {})
    groups = dimensions.get("groups", [])
    targets = dimensions.get("baseline_targets", {})
    enabled = bool(scenario.get("has_equity_contract"))

    return {
        "enabled": enabled,
        "region_weights": deepcopy(dimensions.get("region_weights", {})),
        "groups": [
            {
                "group_id": group["group_id"],
                "region_ids": list(group["region_ids"]),
                "weight": _round(group.get("weight", 1.0)),
                "baseline_target": group.get("baseline_target"),
            }
            for group in groups
        ],
        "baseline_targets": deepcopy(targets),
    }


def inspect_network_state(scenario: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    graph = scenario.get("dependency_graph", {})
    stocks = scenario.get("resource_stocks", {})
    flows = scenario.get("resource_flows", {})
    spillovers = scenario.get("spillover_rules", {})

    last_diagnostics = state.get("latest_network_diagnostics", {})
    transfer_by_flow = {
        item.get("flow_id"): item for item in last_diagnostics.get("flow_transfers", []) if item.get("flow_id")
    }

    stock_entries = []
    for stock in stocks.get("items", []):
        stock_entries.append(
            {
                "stock_id": stock["stock_id"],
                "region_id": stock["region_id"],
                "indicator_id": stock["indicator_id"],
                "baseline": _round(stock["baseline"]),
                "current": _round(state.get("resource_stocks", {}).get(stock["stock_id"], stock["baseline"])),
                "min_bound": _round(stock["min_bound"]),
                "max_bound": _round(stock["max_bound"]),
            }
        )

    flow_entries = []
    for flow in flows.get("items", []):
        latest = transfer_by_flow.get(flow["flow_id"], {})
        flow_entries.append(
            {
                "flow_id": flow["flow_id"],
                "edge_id": flow.get("edge_id"),
                "from_node_id": flow["from_node_id"],
                "to_node_id": flow["to_node_id"],
                "source_stock_id": flow["source_stock_id"],
                "target_stock_id": flow["target_stock_id"],
                "capacity": _round(flow["capacity"]),
                "loss_factor": _round(flow["loss_factor"]),
                "last_transfer": _round(latest.get("transfer", 0.0)),
                "last_delivered": _round(latest.get("delivered", 0.0)),
            }
        )

    spillover_entries = []
    for rule in spillovers.get("items", []):
        spillover_entries.append(
            {
                "rule_id": rule["rule_id"],
                "from_node_id": rule["from_node_id"],
                "to_node_id": rule["to_node_id"],
                "source_indicator_id": rule["source_indicator_id"],
                "target_indicator_id": rule["target_indicator_id"],
                "coefficient": _round(rule["coefficient"]),
                "max_abs_transfer": rule.get("max_abs_transfer"),
            }
        )

    return {
        "scenario_id": scenario["scenario_id"],
        "branch_id": state["branch_id"],
        "turn": int(state.get("turn", 0)),
        "network_summary": scenario_network_summary(scenario),
        "dependency_graph": {
            "nodes": [
                {
                    "node_id": node["node_id"],
                    "region_id": node["region_id"],
                    "label": node.get("label"),
                }
                for node in graph.get("nodes", [])
            ],
            "edges": [
                {
                    "edge_id": edge["edge_id"],
                    "from_node_id": edge["from_node_id"],
                    "to_node_id": edge["to_node_id"],
                    "capacity": _round(edge.get("capacity", 0.0)),
                    "latency_turns": int(edge.get("latency_turns", 0)),
                }
                for edge in graph.get("edges", [])
            ],
            "topological_order": list(graph.get("topological_order", [])),
        },
        "resource_stocks": stock_entries,
        "resource_flows": flow_entries,
        "spillover_rules": spillover_entries,
        "latest_turn_diagnostics": deepcopy(last_diagnostics),
    }


def run_turn(
    state: Dict[str, Any],
    scenario: Dict[str, Any],
    intervention_ids: Optional[Sequence[str]] = None,
    shock_ids: Optional[Sequence[str]] = None,
    policy_evaluator: Optional[DeterministicPolicyEngine] = None,
    policies: Optional[List[Dict[str, Any]]] = None,
    approval_status: str = "not_required",
) -> Dict[str, Any]:
    base_state = deepcopy(state)
    turn_index = int(base_state["turn"]) + 1

    selected_interventions = sorted(set(intervention_ids or []))
    selected_shocks = sorted(set(shock_ids or []))

    projected_state = deepcopy(base_state)

    for intervention_id in selected_interventions:
        intervention = scenario["interventions_by_id"].get(intervention_id)
        if intervention is None:
            raise ValueError("unknown intervention_id: %s" % intervention_id)
        apply_intervention(projected_state, intervention, turn_index)

    for shock_id in selected_shocks:
        shock = scenario["shocks_by_id"].get(shock_id)
        if shock is None:
            raise ValueError("unknown shock_id: %s" % shock_id)
        apply_shock(projected_state, shock, turn_index)

    due_interventions = _apply_active_entries(
        projected_state,
        scenario,
        turn_index,
        projected_state["active_interventions"],
    )
    due_shocks = _apply_active_entries(
        projected_state,
        scenario,
        turn_index,
        projected_state["active_shocks"],
    )

    network_diagnostics = _run_network_pipeline(projected_state, scenario, turn_index)
    projected_state["latest_network_diagnostics"] = deepcopy(network_diagnostics)

    projected_state["scorecard"] = compute_scorecard(projected_state, scenario)
    equity_report = build_equity_report(projected_state, scenario)
    projected_state["latest_equity_report"] = deepcopy(equity_report)

    policy_report: Optional[PolicyReport] = None
    policy_payload = None
    if policy_evaluator is not None and policies:
        proposal = _build_policy_proposal(
            scenario=scenario,
            turn_index=turn_index,
            intervention_ids=selected_interventions,
            shock_ids=selected_shocks,
            projected_state=projected_state,
        )
        policy_report = policy_evaluator.evaluate_policies(policies, proposal)
        policy_payload = policy_report.as_dict()

    policy_outcome = "allow"
    requires_approval = False
    if policy_report is not None:
        policy_outcome = policy_report.final_outcome
        requires_approval = policy_report.requires_approval

    commit_allowed = True
    resolved_approval_status = approval_status

    if policy_outcome == "deny":
        commit_allowed = False
        resolved_approval_status = "rejected"
    elif requires_approval and approval_status not in {"approved", "overridden"}:
        commit_allowed = False
        resolved_approval_status = "pending"

    if not commit_allowed:
        turn_result = {
            "turn_index": turn_index,
            "policy_outcome": policy_outcome,
            "approval_status": resolved_approval_status,
            "applied_intervention_ids": due_interventions,
            "applied_shock_ids": due_shocks,
            "scorecard": deepcopy(projected_state["scorecard"]),
            "network_diagnostics": deepcopy(network_diagnostics),
            "equity_report": deepcopy(equity_report),
            "committed": False,
        }
        return {
            "state": base_state,
            "turn_result": turn_result,
            "events": [],
            "policy_report": policy_payload,
        }

    projected_state["turn"] = turn_index
    projected_state["applied_interventions"].extend(selected_interventions)
    projected_state["realized_shocks"].extend(selected_shocks)
    projected_state.setdefault("network_diagnostics_history", []).append(deepcopy(network_diagnostics))
    projected_state.setdefault("equity_history", []).append(deepcopy(equity_report))

    sequence = len(projected_state["event_log"]) + 1
    event = {
        "event_id": "evt.%s.turn.%04d" % (projected_state["branch_id"], turn_index),
        "event_type": "wg_turn_executed",
        "turn": turn_index,
        "sequence": sequence,
        "payload": {
            "selected_intervention_ids": list(selected_interventions),
            "selected_shock_ids": list(selected_shocks),
            "applied_intervention_ids": list(due_interventions),
            "applied_shock_ids": list(due_shocks),
            "policy_outcome": policy_outcome,
            "approval_status": resolved_approval_status,
            "scorecard": deepcopy(projected_state["scorecard"]),
            "network_diagnostics": deepcopy(network_diagnostics),
            "equity_report": deepcopy(equity_report),
            "resource_stocks": deepcopy(projected_state.get("resource_stocks", {})),
        },
    }
    projected_state["event_log"].append(event)

    turn_result = {
        "turn_index": turn_index,
        "policy_outcome": policy_outcome,
        "approval_status": resolved_approval_status,
        "applied_intervention_ids": due_interventions,
        "applied_shock_ids": due_shocks,
        "scorecard": deepcopy(projected_state["scorecard"]),
        "network_diagnostics": deepcopy(network_diagnostics),
        "equity_report": deepcopy(equity_report),
        "committed": True,
    }

    return {
        "state": projected_state,
        "turn_result": turn_result,
        "events": [event],
        "policy_report": policy_payload,
    }


def create_branch(
    base_state: Dict[str, Any],
    branch_id: str,
    parent_branch_id: Optional[str] = None,
) -> Dict[str, Any]:
    branch = deepcopy(base_state)
    branch["branch_id"] = branch_id
    branch["parent_branch_id"] = parent_branch_id or base_state.get("branch_id")
    branch["event_log"] = deepcopy(base_state.get("event_log", []))
    return branch


def replay_world_game(
    scenario: Dict[str, Any],
    events: Sequence[Dict[str, Any]],
    policy_evaluator: Optional[DeterministicPolicyEngine] = None,
    policies: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    state = initialize_baseline_state(scenario, branch_id="replay", parent_branch_id=None)
    turn_results: List[Dict[str, Any]] = []

    ordered_events = sorted(
        events,
        key=lambda item: (
            int(item.get("turn", 0)),
            int(item.get("sequence", 0)),
            str(item.get("event_id", "")),
        ),
    )

    for event in ordered_events:
        if event.get("event_type") != "wg_turn_executed":
            continue
        payload = event.get("payload", {})
        result = run_turn(
            state=state,
            scenario=scenario,
            intervention_ids=payload.get("selected_intervention_ids", []),
            shock_ids=payload.get("selected_shock_ids", []),
            policy_evaluator=policy_evaluator,
            policies=policies,
            approval_status=payload.get("approval_status", "approved"),
        )
        state = result["state"]
        turn_results.append(result["turn_result"])

    return {
        "state": state,
        "turn_results": turn_results,
    }


def _summarize_regional_tradeoffs(branch_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_region: Dict[str, List[Tuple[str, float]]] = {}
    for branch in branch_rows:
        branch_id = branch["branch_id"]
        equity = branch.get("equity", {})
        for entry in equity.get("per_region", []):
            region_id = entry["region_id"]
            by_region.setdefault(region_id, []).append((branch_id, float(entry["normalized_outcome"])))

    tradeoffs: List[Dict[str, Any]] = []
    for region_id, rows in by_region.items():
        if len(rows) < 2:
            continue
        ranked = sorted(rows, key=lambda item: (-float(item[1]), str(item[0])))
        best_branch, best_value = ranked[0]
        worst_branch, worst_value = sorted(rows, key=lambda item: (float(item[1]), str(item[0])))[0]
        gap = best_value - worst_value
        tradeoffs.append(
            {
                "region_id": region_id,
                "best_branch_id": best_branch,
                "best_outcome": _round(best_value),
                "worst_branch_id": worst_branch,
                "worst_outcome": _round(worst_value),
                "gap": _round(gap),
            }
        )

    return sorted(tradeoffs, key=lambda item: (-float(item["gap"]), str(item["region_id"])))


def generate_comparison_report(
    scenario: Dict[str, Any],
    branch_states: Sequence[Dict[str, Any]],
    comparison_id: Optional[str] = None,
) -> Dict[str, Any]:
    if len(branch_states) < 2:
        raise ValueError("comparison requires at least two branches")

    normalized_branches = []
    for branch in branch_states:
        scorecard = branch.get("scorecard") or compute_scorecard(branch, scenario)
        equity = branch.get("latest_equity_report") or build_equity_report(branch, scenario)
        normalized_branches.append(
            {
                "branch_id": branch["branch_id"],
                "parent_branch_id": branch.get("parent_branch_id"),
                "composite_score": float(scorecard["composite_score"]),
                "indicator_scores": deepcopy(scorecard["indicator_scores"]),
                "equity": deepcopy(equity),
            }
        )

    ranked = sorted(
        normalized_branches,
        key=lambda item: (-float(item["composite_score"]), str(item["branch_id"])),
    )

    equity_ranked = sorted(
        normalized_branches,
        key=lambda item: (
            float(item.get("equity", {}).get("disparity_index", {}).get("spread", 0.0)),
            float(item.get("equity", {}).get("disparity_index", {}).get("weighted_variance", 0.0)),
            -float(item.get("equity", {}).get("equity_trend_vs_baseline", 0.0)),
            str(item["branch_id"]),
        ),
    )

    tradeoffs = _summarize_regional_tradeoffs(normalized_branches)

    report = {
        "comparison_id": comparison_id or "cmp.%s" % uuid4().hex[:12],
        "scenario_id": scenario["scenario_id"],
        "created_at": _utc_now(),
        "branches": normalized_branches,
        "rankings": [item["branch_id"] for item in ranked],
        "summary": {
            "branch_count": len(normalized_branches),
            "best_composite_score_branch": ranked[0]["branch_id"],
            "best_composite_score": ranked[0]["composite_score"],
            "best_equity_branch": equity_ranked[0]["branch_id"],
            "lowest_disparity_branch": equity_ranked[0]["branch_id"],
            "regional_tradeoffs": tradeoffs,
        },
    }
    return report


def compare_branches(scenario: Dict[str, Any], branch_states: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return generate_comparison_report(scenario=scenario, branch_states=branch_states)
