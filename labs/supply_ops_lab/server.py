from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adapters.supply_ops import SupplyOpsIngressPreparer, SupplyOpsTranslator
from adapters.supply_ops.replay import build_commitment_risk_event, build_recovery_hypothetical_events
from api.runtime_api import PUBLIC_ENDPOINTS
from core.event_store import InMemoryEventStore
from core.policy_engine import DeterministicPolicyEngine
from core.projector import SimpleProjector
from core.replay_engine import ReplayEngine
from core.simulation_engine import SimulationEngine


REVIEWED_FIXTURE_NAME = "require_approval_high_expedite"
PRESET_ORDER = [
    "allow_recovery",
    "warn_low_inventory_cover",
    "require_approval_high_expedite",
    "deny_low_fill_rate",
]
PRESET_DETAILS = {
    "allow_recovery": {
        "label": "Allow Recovery",
        "headline": "Recover with local inventory and standard capacity",
        "operator_goal": "Use nearby inventory and standard lane capacity without triggering approval.",
        "tradeoff": "Keeps the recovery clean and low-friction with healthy post-action cover.",
        "expected_outcome": "allow",
    },
    "warn_low_inventory_cover": {
        "label": "Warn On Low Cover",
        "headline": "Recover the commitment but accept thinner inventory cover",
        "operator_goal": "Preserve service levels while surfacing the inventory tradeoff explicitly.",
        "tradeoff": "Avoids premium freight, but leaves post-action inventory under the advisory threshold.",
        "expected_outcome": "warn",
    },
    "require_approval_high_expedite": {
        "label": "Require Approval",
        "headline": "Recover fully through an expedited lane with supervisor review",
        "operator_goal": "Eliminate late units quickly while keeping the expedite premium policy-visible.",
        "tradeoff": "Removes the shortfall, but requires approval because the expedite premium exceeds policy.",
        "expected_outcome": "require_approval",
    },
    "deny_low_fill_rate": {
        "label": "Deny Low Fill Rate",
        "headline": "Show a blocked recovery when fill rate stays below the minimum threshold",
        "operator_goal": "Expose the policy boundary where the available recovery is not credible enough to run.",
        "tradeoff": "Uses the best available standard recovery, but still leaves too many units late.",
        "expected_outcome": "deny",
    },
}
SCENARIO_DIR = REPO_ROOT / "examples" / "scenarios" / "supply-ops-mini"
LAB_MILESTONE = "SO-P4"
OPERATOR_REFERENCE_SURFACE = "SO-P3 operator/reference route"
DECISION_EXPLORER_ROUTE = "/decision-explorer"
DECISION_EXPLORER_BOOTSTRAP_ENDPOINT = "/api/supply-ops/decision-explorer/bootstrap"
DECISION_EXPLORER_EVALUATE_ENDPOINT = "/api/supply-ops/decision-explorer/evaluate"
DECISION_EXPLORER_DEFAULT_WEIGHTS = {
    "service_level": 45,
    "margin_guardrail": 35,
    "approval_friction": 20,
}
DECISION_EXPLORER_SERVICE_HEAVY_WEIGHTS = {
    "service_level": 70,
    "margin_guardrail": 15,
    "approval_friction": 15,
}
DECISION_EXPLORER_WEIGHT_LABELS = {
    "service_level": "Service level",
    "margin_guardrail": "Margin guardrail",
    "approval_friction": "Approval friction",
}
DECISION_EXPLORER_COMMITMENT = {
    "commitment_id": "commitment.retailer-4821",
    "customer": "Retailer 4821",
    "sku": "widget-alpha",
    "at_risk_units": 180,
    "promised_date": "2026-03-23",
    "current_risk": "Dallas inventory and packout are constrained; the commitment will miss promise unless the recovery is assembled intentionally.",
    "anchor_note": "Curated concept surface anchored to the reviewed Supply Ops recovery example and current default policy thresholds.",
}
DECISION_EXPLORER_PROPOSALS = [
    {
        "proposal_id": "proposal.supply-ops.decision-explorer.inventory-rebalance",
        "label": "Proposal 1",
        "headline": "Rebalance nearby inventory first",
        "summary": "Move 120 units from Dallas reserve stock to the at-risk commitment without premium freight.",
        "effect": "Reduces the exposure quickly while preserving approval headroom.",
        "recovery_units": 120,
        "lane_id": "lane.dallas-atl.standard",
    },
    {
        "proposal_id": "proposal.supply-ops.decision-explorer.capacity-reserve",
        "label": "Proposal 2",
        "headline": "Reserve an extra packout window",
        "summary": "Reserve a short overtime packout block so another 42 units can leave on the standard lane.",
        "effect": "Improves fill-rate recovery while keeping the plan inside normal approval posture.",
        "recovery_units": 42,
        "lane_id": "lane.dallas-atl.standard",
    },
    {
        "proposal_id": "proposal.supply-ops.decision-explorer.expedite-topoff",
        "label": "Proposal 3",
        "headline": "Top off the final units on an expedited lane",
        "summary": "Expedite the remaining 18 units to eliminate lateness entirely.",
        "effect": "Protects service level completely, but pushes the decision into higher-cost approval territory.",
        "recovery_units": 18,
        "lane_id": "lane.dallas-atl.expedited",
    },
]
DECISION_EXPLORER_PLANS = {
    "plan.margin-guardrail": {
        "plan_id": "plan.margin-guardrail",
        "label": "Plan A",
        "headline": "Balanced Recovery",
        "summary": "Use local inventory plus short-term packout capacity to recover most units while keeping policy posture clean.",
        "proposal_ids": [
            "proposal.supply-ops.decision-explorer.inventory-rebalance",
            "proposal.supply-ops.decision-explorer.capacity-reserve",
        ],
        "target_lane_id": "lane.dallas-atl.standard",
        "reallocation_units": 162,
        "projected_fill_rate_percent": 96,
        "projected_post_action_inventory_days": 4,
        "expedite_cost_delta_percent": 5,
        "projected_margin_delta_percent": -2,
        "late_units_after_action": 18,
        "simulation_confidence": 78,
        "dimension_scores": {
            "service_level": 72,
            "margin_guardrail": 88,
            "approval_friction": 93,
        },
    },
    "plan.service-first": {
        "plan_id": "plan.service-first",
        "label": "Plan B",
        "headline": "Service-First Recovery",
        "summary": "Add the expedited top-off to clear every late unit even though the premium crosses the default approval threshold.",
        "proposal_ids": [
            "proposal.supply-ops.decision-explorer.inventory-rebalance",
            "proposal.supply-ops.decision-explorer.capacity-reserve",
            "proposal.supply-ops.decision-explorer.expedite-topoff",
        ],
        "target_lane_id": "lane.dallas-atl.expedited",
        "reallocation_units": 180,
        "projected_fill_rate_percent": 98,
        "projected_post_action_inventory_days": 2,
        "expedite_cost_delta_percent": 14,
        "projected_margin_delta_percent": -6,
        "late_units_after_action": 0,
        "simulation_confidence": 92,
        "dimension_scores": {
            "service_level": 96,
            "margin_guardrail": 42,
            "approval_friction": 35,
        },
    },
}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _json_bytes(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True).encode("utf-8")


class SupplyOpsLabService:
    def __init__(self, repo_root: Path, upstream_base: str) -> None:
        self.repo_root = repo_root
        self.upstream_base = upstream_base.rstrip("/")
        self.ingress = SupplyOpsIngressPreparer()
        self.translator = SupplyOpsTranslator()
        self.policy_engine = DeterministicPolicyEngine()

    def build_bootstrap_payload(self) -> Dict[str, Any]:
        preset_snapshots = {
            fixture_name: self.build_preset_snapshot(fixture_name)
            for fixture_name in PRESET_ORDER
        }
        return {
            "lab_id": "supply_ops_lab",
            "milestone": LAB_MILESTONE,
            "mode": "preset_operator_reference_surface",
            "surface": OPERATOR_REFERENCE_SURFACE,
            "proxy": {
                "path_prefix": "/api",
                "upstream_base": self.upstream_base,
            },
            "parallel_routes": {
                "operator_reference": "/",
                "decision_explorer": DECISION_EXPLORER_ROUTE,
            },
            "boundary_notes": [
                "Thin lab shell only: the browser renders server-provided data and does not reimplement Supply Ops domain logic.",
                "This preserved operator/reference route still stays on the documented Supply Ops flow only: translated proposal, policy gate, replay summary, simulation summary, and package-backed scenario evidence.",
                "Stable public API wiring is still exercised through the lab proxy; replay and simulation storytelling remain server-assembled because the stock upstream bootstrap does not seed Supply Ops baseline events.",
                "Connector-ingress UI and execution-evidence UI remain out of required scope even though the package-local evidence artifacts are referenced for context.",
                "SO-P4 adds a separate Decision Explorer concept route, but this page remains the truthful runnable operator/reference path.",
                "Startup commands, smoke checks, and demo steps document the supported runnable path only; they do not imply broader runtime or connector support.",
            ],
            "stable_api_wiring": self._stable_api_wiring(),
            "startup_guide": self._startup_guide(),
            "default_preset_fixture_name": REVIEWED_FIXTURE_NAME,
            "preset_catalog": [preset_snapshots[name]["preset"] for name in PRESET_ORDER],
            "preset_snapshots": preset_snapshots,
        }

    def build_reviewed_snapshot(self) -> Dict[str, Any]:
        return self.build_preset_snapshot(REVIEWED_FIXTURE_NAME)

    def build_preset_snapshot(self, fixture_name: str) -> Dict[str, Any]:
        preset = self._preset_details(fixture_name)
        envelope = self.ingress.load_fixture_envelope(self.repo_root, fixture_name)
        ingress_metadata = self.ingress.extract_metadata(envelope)
        translated_proposal = self.translator.translate_ingress_envelope(envelope)
        fixture_bundle = self.translator.load_fixture_bundle(self.repo_root, fixture_name)
        default_policy = self._load_default_policy()
        policy_report = self.policy_engine.evaluate_policies(
            [default_policy],
            translated_proposal,
        ).as_dict()
        scenario = self._load_scenario_artifacts()
        proposal_overview = self._build_proposal_overview(
            preset=preset,
            bundle=fixture_bundle,
            proposal=translated_proposal,
        )
        policy_preview = self._build_policy_surface(
            policy_report,
            approval=None,
            preview=True,
        )
        replay_summary = self._build_replay_summary(
            fixture_bundle=fixture_bundle,
            proposal=translated_proposal,
        )
        simulation_summary = self._build_simulation_summary(
            fixture_bundle=fixture_bundle,
            proposal=translated_proposal,
            simulation_example=scenario["simulation"],
        )
        scenario_evidence = self._build_scenario_evidence(
            fixture_name=fixture_name,
            scenario=scenario,
            proposal=translated_proposal,
        )

        return {
            "fixture_name": fixture_name,
            "preset": preset,
            "ingress": ingress_metadata,
            "translated_proposal": translated_proposal,
            "proposal_overview": proposal_overview,
            "policy_preview": policy_preview,
            "replay_summary": replay_summary,
            "simulation_summary": simulation_summary,
            "scenario_evidence": scenario_evidence,
            "timeline": self._build_timeline(
                preset=preset,
                ingress=ingress_metadata,
                proposal=translated_proposal,
                policy_surface=policy_preview,
                replay_summary=replay_summary,
                simulation_summary=simulation_summary,
                scenario_evidence=scenario_evidence,
            ),
        }

    def run_reviewed_flow(self) -> Dict[str, Any]:
        return self.run_preset_flow(REVIEWED_FIXTURE_NAME)

    def run_preset_flow(self, fixture_name: str) -> Dict[str, Any]:
        snapshot = self.build_preset_snapshot(fixture_name)
        session = self._post_json(PUBLIC_ENDPOINTS["session_create"], {})
        proposal_result = self._post_json(
            PUBLIC_ENDPOINTS["proposal_submit"],
            {
                "session_id": session["session_id"],
                "proposal": snapshot["translated_proposal"],
                "policies": [self._load_default_policy()],
            },
        )
        policy_surface = self._build_policy_surface(
            proposal_result["policy_report"],
            approval=proposal_result.get("approval"),
            preview=False,
        )

        return {
            "milestone": LAB_MILESTONE,
            "fixture_name": fixture_name,
            "preset": snapshot["preset"],
            "session": session,
            "translated_proposal": snapshot["translated_proposal"],
            "proposal_overview": snapshot["proposal_overview"],
            "policy_gate": proposal_result["policy_report"],
            "policy_summary": policy_surface,
            "approval": proposal_result.get("approval"),
            "replay_summary": snapshot["replay_summary"],
            "simulation_summary": snapshot["simulation_summary"],
            "scenario_evidence": snapshot["scenario_evidence"],
            "timeline": self._build_timeline(
                preset=snapshot["preset"],
                ingress=snapshot["ingress"],
                proposal=snapshot["translated_proposal"],
                policy_surface=policy_surface,
                replay_summary=snapshot["replay_summary"],
                simulation_summary=snapshot["simulation_summary"],
                scenario_evidence=snapshot["scenario_evidence"],
                session_id=session["session_id"],
                executed=True,
                approval=proposal_result.get("approval"),
            ),
            "api_wiring": {
                "upstream_base": self.upstream_base,
                "proxied_endpoints": self._stable_api_wiring(),
                "executed_endpoints": [
                    PUBLIC_ENDPOINTS["session_create"],
                    PUBLIC_ENDPOINTS["proposal_submit"],
                ],
                "notes": [
                    "Session creation and proposal submission are exercised against the stable upstream HTTP API through the lab proxy.",
                    "Replay and simulation storytelling remain server-side in SO-P3 so the Supply Ops baseline stays faithful to the documented adapter path.",
                ],
            },
        }

    def build_decision_explorer_bootstrap_payload(self) -> Dict[str, Any]:
        default_evaluation = self.evaluate_decision_explorer(
            weights=DECISION_EXPLORER_DEFAULT_WEIGHTS,
            simulation_mode="include",
        )
        return {
            "lab_id": "supply_ops_lab",
            "milestone": LAB_MILESTONE,
            "mode": "decision_explorer_parallel_concept_surface",
            "surface": "SO-P4 Decision Explorer",
            "routes": {
                "operator_reference": "/",
                "decision_explorer": DECISION_EXPLORER_ROUTE,
            },
            "boundary_notes": [
                "This route is a bounded lab-authored concept surface layered alongside the preserved SO-P3 operator/reference page.",
                "Comparison assembly, weighting, and explanation shaping stay server-authored; the browser only submits controls and renders the response.",
                "No stable runtime/public API comparison endpoint is being claimed here; the payload exists only inside the Supply Ops lab server.",
                "Connector-ingress UI and execution-evidence UI are still out of required scope for this first SO-P4 pass.",
            ],
            "truth_notes": [
                "Commitment language, policy thresholds, and reviewed identifiers are anchored to the documented Supply Ops fixtures and scenario bundle.",
                "The three proposals and two assembled plans are curated comparison objects for this lab route, not a native runtime comparison API.",
                "Policy posture is still evaluated against the current Supply Ops default policy so the concept route stays tied to the real package rules.",
            ],
            "commitment": DECISION_EXPLORER_COMMITMENT,
            "proposal_catalog": DECISION_EXPLORER_PROPOSALS,
            "controls": {
                "weights": [
                    {
                        "id": weight_id,
                        "label": DECISION_EXPLORER_WEIGHT_LABELS[weight_id],
                        "min": 0,
                        "max": 100,
                        "step": 5,
                        "default_value": DECISION_EXPLORER_DEFAULT_WEIGHTS[weight_id],
                        "service_heavy_value": DECISION_EXPLORER_SERVICE_HEAVY_WEIGHTS[weight_id],
                    }
                    for weight_id in DECISION_EXPLORER_DEFAULT_WEIGHTS
                ],
                "simulation_modes": [
                    {
                        "id": "include",
                        "label": "Include simulation evidence",
                        "description": "Blend in the bounded recovery-confidence signal from the curated scenario.",
                    },
                    {
                        "id": "mute",
                        "label": "Mute simulation evidence",
                        "description": "Compare the plans on service, margin, and approval posture only.",
                    },
                ],
                "default_request": {
                    "weights": DECISION_EXPLORER_DEFAULT_WEIGHTS,
                    "simulation_mode": "include",
                },
                "service_heavy_example": {
                    "weights": DECISION_EXPLORER_SERVICE_HEAVY_WEIGHTS,
                    "simulation_mode": "include",
                },
            },
            "initial_evaluation": default_evaluation,
        }

    def evaluate_decision_explorer(
        self,
        *,
        weights: Dict[str, Any],
        simulation_mode: str,
    ) -> Dict[str, Any]:
        normalized_weights = self._normalize_decision_explorer_weights(weights)
        simulation_mode = self._normalize_simulation_mode(simulation_mode)
        plans = [
            self._evaluate_decision_plan(plan_definition, normalized_weights, simulation_mode)
            for plan_definition in DECISION_EXPLORER_PLANS.values()
        ]
        plans.sort(
            key=lambda item: (-item["score"]["total"], item["plan"]["label"]),
        )
        selected_plan = plans[0]
        runner_up = plans[1]
        default_selected_plan_id = self._default_decision_explorer_selected_plan_id()
        selection_changed_from_default = selected_plan["plan"]["plan_id"] != default_selected_plan_id

        return {
            "weights": normalized_weights,
            "simulation_mode": simulation_mode,
            "plans": plans,
            "selected_plan_id": selected_plan["plan"]["plan_id"],
            "default_selected_plan_id": default_selected_plan_id,
            "selection_changed_from_default": selection_changed_from_default,
            "decision_summary": self._build_decision_summary(
                selected_plan=selected_plan,
                runner_up=runner_up,
                normalized_weights=normalized_weights,
                simulation_mode=simulation_mode,
                selection_changed_from_default=selection_changed_from_default,
            ),
            "why_selected": self._build_selected_reasoning(
                selected_plan=selected_plan,
                runner_up=runner_up,
                normalized_weights=normalized_weights,
                simulation_mode=simulation_mode,
            ),
            "why_not_selected": self._build_runner_up_reasoning(
                selected_plan=selected_plan,
                runner_up=runner_up,
                normalized_weights=normalized_weights,
                simulation_mode=simulation_mode,
            ),
        }

    def _default_decision_explorer_selected_plan_id(self) -> str:
        default_result = [
            self._evaluate_decision_plan(plan_definition, DECISION_EXPLORER_DEFAULT_WEIGHTS, "include")
            for plan_definition in DECISION_EXPLORER_PLANS.values()
        ]
        default_result.sort(
            key=lambda item: (-item["score"]["total"], item["plan"]["label"]),
        )
        return default_result[0]["plan"]["plan_id"]

    def _normalize_decision_explorer_weights(self, weights: Dict[str, Any]) -> Dict[str, int]:
        normalized = {}
        for weight_id, default_value in DECISION_EXPLORER_DEFAULT_WEIGHTS.items():
            raw_value = weights.get(weight_id, default_value)
            try:
                numeric_value = int(raw_value)
            except (TypeError, ValueError):
                numeric_value = default_value
            normalized[weight_id] = max(0, min(100, numeric_value))
        return normalized

    def _normalize_simulation_mode(self, simulation_mode: Any) -> str:
        return "mute" if simulation_mode == "mute" else "include"

    def _evaluate_decision_plan(
        self,
        plan_definition: Dict[str, Any],
        normalized_weights: Dict[str, int],
        simulation_mode: str,
    ) -> Dict[str, Any]:
        policy_report = self.policy_engine.evaluate_policies(
            [self._load_default_policy()],
            self._build_decision_plan_proposal(plan_definition),
        ).as_dict()
        policy_surface = self._build_policy_surface(
            policy_report,
            approval=None,
            preview=True,
        )
        breakdown = []
        total_weight = sum(normalized_weights.values()) or 1
        weighted_total = 0.0
        for weight_id, weight_value in normalized_weights.items():
            score = plan_definition["dimension_scores"][weight_id]
            contribution = round((weight_value / total_weight) * score, 2)
            weighted_total += contribution
            breakdown.append(
                {
                    "dimension_id": weight_id,
                    "label": DECISION_EXPLORER_WEIGHT_LABELS[weight_id],
                    "weight": weight_value,
                    "score": score,
                    "contribution": contribution,
                }
            )

        total_score = round(weighted_total, 2)
        if simulation_mode == "include":
            total_score = round((weighted_total * 0.85) + (plan_definition["simulation_confidence"] * 0.15), 2)

        return {
            "plan": {
                "plan_id": plan_definition["plan_id"],
                "label": plan_definition["label"],
                "headline": plan_definition["headline"],
                "summary": plan_definition["summary"],
                "proposal_ids": plan_definition["proposal_ids"],
                "metrics": {
                    "reallocation_units": plan_definition["reallocation_units"],
                    "late_units_after_action": plan_definition["late_units_after_action"],
                    "projected_fill_rate_percent": plan_definition["projected_fill_rate_percent"],
                    "projected_post_action_inventory_days": plan_definition["projected_post_action_inventory_days"],
                    "expedite_cost_delta_percent": plan_definition["expedite_cost_delta_percent"],
                    "projected_margin_delta_percent": plan_definition["projected_margin_delta_percent"],
                    "simulation_confidence": plan_definition["simulation_confidence"],
                },
            },
            "policy_surface": policy_surface,
            "score": {
                "total": total_score,
                "simulation_mode": simulation_mode,
                "breakdown": breakdown,
            },
        }

    def _build_decision_plan_proposal(self, plan_definition: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "proposal_id": f"{plan_definition['plan_id']}.concept",
            "proposal_type": "commitment_recovery",
            "status": "lab_preview",
            "target_entities": [
                {
                    "entity_id": DECISION_EXPLORER_COMMITMENT["commitment_id"],
                    "entity_type": "order_commitment",
                },
                {
                    "entity_id": "inventory.dallas.dc.widget-alpha",
                    "entity_type": "inventory_position",
                },
                {
                    "entity_id": "capacity.dallas.packout.2026-03-23",
                    "entity_type": "capacity_bucket",
                },
                {
                    "entity_id": plan_definition["target_lane_id"],
                    "entity_type": "fulfillment_lane",
                },
            ],
            "proposed_action": {
                "action_type": "rebalance_inventory_and_expedite_commitment",
                "parameters": {
                    "commitment_id": DECISION_EXPLORER_COMMITMENT["commitment_id"],
                    "source_inventory_id": "inventory.dallas.dc.widget-alpha",
                    "reserve_capacity_id": "capacity.dallas.packout.2026-03-23",
                    "lane_id": plan_definition["target_lane_id"],
                    "reallocation_units": plan_definition["reallocation_units"],
                    "projected_fill_rate_percent": plan_definition["projected_fill_rate_percent"],
                    "projected_post_action_inventory_days": plan_definition["projected_post_action_inventory_days"],
                    "expedite_cost_delta_percent": plan_definition["expedite_cost_delta_percent"],
                    "simulation_completed": True,
                    "simulation_id": "sim.supply-ops.decision-explorer",
                },
            },
            "justification": plan_definition["summary"],
        }

    def _build_decision_summary(
        self,
        *,
        selected_plan: Dict[str, Any],
        runner_up: Dict[str, Any],
        normalized_weights: Dict[str, int],
        simulation_mode: str,
        selection_changed_from_default: bool,
    ) -> Dict[str, Any]:
        emphasis = self._weight_emphasis(normalized_weights)
        selected_policy = selected_plan["policy_surface"]["final_outcome"]
        runner_up_policy = runner_up["policy_surface"]["final_outcome"]
        policy_shift = selected_policy != runner_up_policy
        headline = (
            f"{selected_plan['plan']['label']} is selected under the current weighting profile."
        )
        if selection_changed_from_default:
            headline = (
                f"{selected_plan['plan']['label']} overtakes the default recommendation when service weighting is raised."
            )
        return {
            "headline": headline,
            "selected_plan_label": selected_plan["plan"]["label"],
            "runner_up_label": runner_up["plan"]["label"],
            "selected_policy_outcome": selected_policy,
            "runner_up_policy_outcome": runner_up_policy,
            "policy_shift": policy_shift,
            "policy_shift_copy": (
                f"Decision posture shifts from {runner_up_policy.replace('_', ' ')} to {selected_policy.replace('_', ' ')}."
                if policy_shift
                else "Decision posture stays on the same policy class under the current weighting."
            ),
            "score_gap": round(
                selected_plan["score"]["total"] - runner_up["score"]["total"],
                2,
            ),
            "top_weight_label": DECISION_EXPLORER_WEIGHT_LABELS[emphasis[0]],
            "simulation_mode": simulation_mode,
        }

    def _build_selected_reasoning(
        self,
        *,
        selected_plan: Dict[str, Any],
        runner_up: Dict[str, Any],
        normalized_weights: Dict[str, int],
        simulation_mode: str,
    ) -> List[str]:
        emphasis = self._weight_emphasis(normalized_weights)
        primary_weight = emphasis[0]
        secondary_weight = emphasis[1]
        return [
            (
                f"{selected_plan['plan']['label']} leads on {DECISION_EXPLORER_WEIGHT_LABELS[primary_weight].lower()} "
                f"({self._dimension_score(selected_plan, primary_weight)} vs {self._dimension_score(runner_up, primary_weight)})."
            ),
            (
                f"Its combined score stays ahead once {DECISION_EXPLORER_WEIGHT_LABELS[secondary_weight].lower()} "
                f"is layered in ({selected_plan['score']['total']} vs {runner_up['score']['total']})."
            ),
            (
                "Bounded simulation evidence is blended into the comparison."
                if simulation_mode == "include"
                else "Simulation evidence is muted, so the decision is driven only by the visible policy weights."
            ),
            (
                f"Current policy posture: {selected_plan['policy_surface']['final_outcome'].replace('_', ' ')}. "
                f"{selected_plan['policy_surface']['approval_copy']}"
            ),
        ]

    def _build_runner_up_reasoning(
        self,
        *,
        selected_plan: Dict[str, Any],
        runner_up: Dict[str, Any],
        normalized_weights: Dict[str, int],
        simulation_mode: str,
    ) -> List[str]:
        emphasis = self._weight_emphasis(normalized_weights)
        primary_weight = emphasis[0]
        return [
            (
                f"{runner_up['plan']['label']} is not selected because its {DECISION_EXPLORER_WEIGHT_LABELS[primary_weight].lower()} "
                f"advantage is not strong enough under the current mix."
                if self._dimension_score(runner_up, primary_weight) > self._dimension_score(selected_plan, primary_weight)
                else f"{runner_up['plan']['label']} gives up too much on {DECISION_EXPLORER_WEIGHT_LABELS[primary_weight].lower()} for this weighting profile."
            ),
            (
                f"Its policy posture is {runner_up['policy_surface']['final_outcome'].replace('_', ' ')}, "
                f"compared with {selected_plan['policy_surface']['final_outcome'].replace('_', ' ')} for the selected plan."
            ),
            (
                f"It would move late units to {runner_up['plan']['metrics']['late_units_after_action']} "
                f"instead of {selected_plan['plan']['metrics']['late_units_after_action']}."
            ),
            (
                "Muted simulation evidence keeps the comparison narrower than the reviewed scenario analog."
                if simulation_mode == "mute"
                else "Even with simulation evidence included, it finishes behind the selected plan."
            ),
        ]

    def _weight_emphasis(self, normalized_weights: Dict[str, int]) -> List[str]:
        return sorted(
            normalized_weights,
            key=lambda weight_id: (-normalized_weights[weight_id], weight_id),
        )

    def _dimension_score(self, plan: Dict[str, Any], weight_id: str) -> int:
        for item in plan["score"]["breakdown"]:
            if item["dimension_id"] == weight_id:
                return item["score"]
        raise KeyError(weight_id)

    def _build_proposal_overview(
        self,
        *,
        preset: Dict[str, Any],
        bundle: Dict[str, Any],
        proposal: Dict[str, Any],
    ) -> Dict[str, Any]:
        order_signal = bundle["order_signal"]
        lane_signal = bundle["lane_signal"]
        parameters = proposal["proposed_action"]["parameters"]
        projected_late_units = max(
            order_signal["at_risk_units"] - parameters["reallocation_units"],
            0,
        )
        return {
            "headline": preset["headline"],
            "operator_goal": preset["operator_goal"],
            "tradeoff": preset["tradeoff"],
            "justification": proposal["justification"],
            "metrics": [
                ["Commitment", parameters["commitment_id"]],
                ["Lane", parameters["lane_id"]],
                ["Service Level", lane_signal["service_level"]],
                ["Requested Units", order_signal["requested_units"]],
                ["At-Risk Units", order_signal["at_risk_units"]],
                ["Recovery Units", parameters["reallocation_units"]],
                ["Projected Late Units", projected_late_units],
                [
                    "Inventory Cover After Action",
                    f'{parameters["projected_post_action_inventory_days"]} days',
                ],
            ],
        }

    def _build_replay_summary(
        self,
        *,
        fixture_bundle: Dict[str, Any],
        proposal: Dict[str, Any],
    ) -> Dict[str, Any]:
        expected_projection = _load_json(SCENARIO_DIR / "projection.json")
        store = InMemoryEventStore()
        store.append(
            "adapter-supply-ops.%s" % proposal["proposal_id"],
            build_commitment_risk_event(fixture_bundle),
        )

        replay = ReplayEngine(store, SimpleProjector)
        rebuilt = replay.rebuild("supply_ops_state", use_snapshot=False)
        commitment_id = proposal["proposed_action"]["parameters"]["commitment_id"]

        return {
            "projection_name": rebuilt.projection_name,
            "source_event_offset": rebuilt.source_event_offset,
            "events_processed": rebuilt.events_processed,
            "baseline_event_id": rebuilt.state["last_event_id"],
            "commitment_state": rebuilt.state["commitments"][commitment_id],
            "reviewed_example_projection_name": expected_projection["projection_name"],
            "reviewed_example_offset": expected_projection["source_event_offset"],
        }

    def _build_simulation_summary(
        self,
        *,
        fixture_bundle: Dict[str, Any],
        proposal: Dict[str, Any],
        simulation_example: Dict[str, Any],
    ) -> Dict[str, Any]:
        order_signal = fixture_bundle["order_signal"]
        parameters = proposal["proposed_action"]["parameters"]
        store = InMemoryEventStore()
        store.append(
            "adapter-supply-ops.%s" % proposal["proposal_id"],
            build_commitment_risk_event(fixture_bundle),
        )
        replay = ReplayEngine(store, SimpleProjector)
        simulation = SimulationEngine(replay, SimpleProjector)
        simulation_id = parameters["simulation_id"]
        branch = simulation.create_branch(
            simulation_id=simulation_id,
            projection_name="supply_ops_state",
            scenario_name=simulation_example["scenario_name"],
            assumptions=simulation_example.get("assumptions", []),
            inputs={
                "commitment_id": parameters["commitment_id"],
                "recovery_units": parameters["reallocation_units"],
            },
        )

        for event in build_recovery_hypothetical_events(proposal):
            simulation.apply_hypothetical_event(branch.simulation_id, event)

        result = simulation.run(branch.simulation_id).as_dict()
        commitment_id = proposal["target_entities"][0]["entity_id"]
        baseline_late_units = order_signal["at_risk_units"]
        projected_late_units_after_action = max(
            baseline_late_units - parameters["reallocation_units"],
            0,
        )

        return {
            "simulation_id": result["simulation_id"],
            "status": result["status"],
            "hypothetical_events_applied": result["hypothetical_events_applied"],
            "changed_paths": result["comparison_summary"]["changed_paths"],
            "changed_path_count": result["comparison_summary"]["changed_path_count"],
            "base_commitment": result["base_state"]["commitments"][commitment_id],
            "simulated_commitment": result["simulated_state"]["commitments"][commitment_id],
            "state_diff": result["state_diff"],
            "baseline_late_units": baseline_late_units,
            "projected_late_units_after_action": projected_late_units_after_action,
            "projected_post_action_inventory_days": parameters["projected_post_action_inventory_days"],
            "expedite_cost_delta_percent": parameters["expedite_cost_delta_percent"],
            "assumptions": simulation_example.get("assumptions", []),
        }

    def _build_scenario_evidence(
        self,
        *,
        fixture_name: str,
        scenario: Dict[str, Dict[str, Any]],
        proposal: Dict[str, Any],
    ) -> Dict[str, Any]:
        reviewed_proposal = scenario["proposal"]
        simulation = scenario["simulation"]
        decision = scenario["decision"]
        projection = scenario["projection"]
        reviewed_fixture = fixture_name == REVIEWED_FIXTURE_NAME
        artifact_paths = [
            f"adapters/supply_ops/fixtures/ingress/{fixture_name}.json",
            f"adapters/supply_ops/fixtures/inbound/{fixture_name}.json",
            f"adapters/supply_ops/fixtures/translated/{fixture_name}.json",
            "examples/scenarios/supply-ops-mini/proposal.json",
            "examples/scenarios/supply-ops-mini/simulation.json",
            "examples/scenarios/supply-ops-mini/decision.json",
            "examples/scenarios/supply-ops-mini/projection.json",
            "examples/scenarios/supply-ops-mini/execution_evidence.json",
        ]

        return {
            "scenario_id": "supply-ops-mini",
            "reviewed_example_match": reviewed_fixture,
            "artifact_paths": artifact_paths,
            "proposal": {
                "proposal_id": proposal["proposal_id"],
                "reviewed_example_proposal_id": reviewed_proposal["proposal_id"],
                "action_type": proposal["proposed_action"]["action_type"],
                "reallocation_units": proposal["proposed_action"]["parameters"]["reallocation_units"],
                "lane_id": proposal["proposed_action"]["parameters"]["lane_id"],
            },
            "simulation": {
                "simulation_id": simulation["simulation_id"],
                "status": simulation["status"],
                "recommended_proposal_id": simulation["outcomes"]["recommended_proposal_id"],
                "baseline_late_units": simulation["outcomes"]["baseline_late_units"],
                "projected_late_units_after_action": simulation["outcomes"]["projected_late_units_after_action"],
            },
            "decision": {
                "decision_id": decision["decision_id"],
                "status": decision["status"],
                "approval_status": decision["approval_status"],
                "policy_outcomes": [item["outcome"] for item in decision["policy_results"]],
            },
            "projection": {
                "projection_name": projection["projection_name"],
                "source_event_offset": projection["source_event_offset"],
                "status": projection["status"],
            },
            "notes": [
                (
                    "This preset matches the reviewed package example exactly."
                    if reviewed_fixture
                    else "This preset reuses the same documented SO-M3 adapter path, while the reviewed package scenario artifacts remain rooted in the require-approval example."
                ),
                "Execution evidence remains a referenced package artifact rather than a required SO-P2 UI surface.",
            ],
        }

    def _build_policy_surface(
        self,
        policy_report: Dict[str, Any],
        *,
        approval: Optional[Dict[str, Any]],
        preview: bool,
    ) -> Dict[str, Any]:
        final_outcome = policy_report.get("final_outcome", "allow")
        matched_evaluations = [
            item for item in policy_report.get("evaluations", []) if item.get("matched")
        ]
        default_evaluation = policy_report.get("evaluations", [{}])[0]
        if matched_evaluations:
            headline = matched_evaluations[-1].get("message") or "Policy matched."
        elif default_evaluation.get("rule_id") == "default_outcome":
            headline = "No Supply Ops policy rule blocked or escalated the proposal."
        else:
            headline = "Policy completed without rule detail."
        detail_lines = []
        for item in matched_evaluations:
            message = item.get("message")
            severity = item.get("severity")
            evidence = item.get("evidence", {})
            evidence_copy = ""
            if isinstance(evidence, dict) and evidence.get("field"):
                evidence_copy = (
                    " (%s %s %s -> actual %s)"
                    % (
                        evidence.get("field"),
                        evidence.get("operator"),
                        evidence.get("expected"),
                        evidence.get("actual"),
                    )
                )
            label = f"{item.get('outcome', 'info')}"
            if severity:
                label = f"{label} / {severity}"
            detail_lines.append(f"{label}: {message or 'matched rule'}{evidence_copy}")
        if not detail_lines:
            detail_lines.append("allow: default outcome because no policy rule matched.")
        approval_copy = (
            "Approval is pending upstream review."
            if approval and approval.get("status") == "pending"
            else (
                f"Approval status: {approval.get('status')}."
                if approval
                else ("Preview only: no approval request has been created yet." if preview else "No approval request was required.")
            )
        )
        return {
            "final_outcome": final_outcome,
            "headline": headline,
            "details": detail_lines,
            "approval_copy": approval_copy,
            "mode": "preview" if preview else "executed",
        }

    def _build_timeline(
        self,
        *,
        preset: Dict[str, Any],
        ingress: Dict[str, Any],
        proposal: Dict[str, Any],
        policy_surface: Dict[str, Any],
        replay_summary: Dict[str, Any],
        simulation_summary: Dict[str, Any],
        scenario_evidence: Dict[str, Any],
        session_id: Optional[str] = None,
        executed: bool = False,
        approval: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        parameters = proposal["proposed_action"]["parameters"]
        timeline = [
            {
                "stage": "preset",
                "status": "selected",
                "title": preset["label"],
                "detail": preset["tradeoff"],
            },
            {
                "stage": "ingress",
                "status": "complete",
                "title": "Connector envelope stays translation-only",
                "detail": (
                    "%s from %s arrived through %s with boundary %s."
                    % (
                        ingress["envelope_id"],
                        ingress["provider"],
                        ingress["connector_id"],
                        ingress["governance"]["translation_boundary"],
                    )
                ),
            },
            {
                "stage": "proposal",
                "status": "complete",
                "title": "Proposal translated into a runnable recovery option",
                "detail": (
                    "%s moves %s units through %s."
                    % (
                        proposal["proposal_id"],
                        parameters["reallocation_units"],
                        parameters["lane_id"],
                    )
                ),
            },
        ]
        if executed and session_id:
            timeline.append(
                {
                    "stage": "api",
                    "status": "complete",
                    "title": "Stable public API session opened",
                    "detail": "Session %s was created before the proposal hit the upstream policy path." % session_id,
                }
            )
        timeline.append(
            {
                "stage": "policy",
                "status": policy_surface["final_outcome"],
                "title": "Policy gate evaluated the proposal",
                "detail": policy_surface["headline"],
            }
        )
        if approval:
            timeline.append(
                {
                    "stage": "approval",
                    "status": approval.get("status", "pending"),
                    "title": "Approval remains explicit",
                    "detail": "Approval %s is %s." % (
                        approval.get("approval_id", "unknown"),
                        approval.get("status", "pending"),
                    ),
                }
            )
        timeline.extend(
            [
                {
                    "stage": "replay",
                    "status": "reference",
                    "title": "Risk baseline replay stays server-backed",
                    "detail": (
                        "%s rebuilt %s event into commitment status %s."
                        % (
                            replay_summary["projection_name"],
                            replay_summary["events_processed"],
                            replay_summary["commitment_state"]["status"],
                        )
                    ),
                },
                {
                    "stage": "simulation",
                    "status": simulation_summary["status"],
                    "title": "Simulation summarizes the recovery tradeoff",
                    "detail": (
                        "Late units move from %s to %s across %s changed paths."
                        % (
                            simulation_summary["baseline_late_units"],
                            simulation_summary["projected_late_units_after_action"],
                            simulation_summary["changed_path_count"],
                        )
                    ),
                },
                {
                    "stage": "evidence",
                    "status": "reference",
                    "title": "Package-backed evidence remains visible",
                    "detail": scenario_evidence["notes"][0],
                },
            ]
        )
        return timeline

    def _preset_details(self, fixture_name: str) -> Dict[str, Any]:
        details = PRESET_DETAILS.get(fixture_name)
        if details is None:
            raise ValueError("unsupported preset fixture: %s" % fixture_name)
        return {
            "fixture_name": fixture_name,
            **details,
        }

    def _load_scenario_artifacts(self) -> Dict[str, Dict[str, Any]]:
        return {
            "proposal": _load_json(SCENARIO_DIR / "proposal.json"),
            "simulation": _load_json(SCENARIO_DIR / "simulation.json"),
            "decision": _load_json(SCENARIO_DIR / "decision.json"),
            "projection": _load_json(SCENARIO_DIR / "projection.json"),
        }

    def _load_default_policy(self) -> Dict[str, Any]:
        return _load_json(
            self.repo_root / "adapters" / "supply_ops" / "policies" / "default_policy.json"
        )

    def _stable_api_wiring(self) -> List[Dict[str, str]]:
        return [
            {
                "label": "Create session",
                "method": "POST",
                "path": PUBLIC_ENDPOINTS["session_create"],
            },
            {
                "label": "Submit proposal",
                "method": "POST",
                "path": PUBLIC_ENDPOINTS["proposal_submit"],
            },
            {
                "label": "Run simulation",
                "method": "POST",
                "path": PUBLIC_ENDPOINTS["simulation_run"],
            },
        ]

    def _startup_guide(self) -> Dict[str, Any]:
        return {
            "commands": [
                {
                    "label": "Start upstream public HTTP API",
                    "command": "python3 -m api.http_server --host 127.0.0.1 --port 8080",
                },
                {
                    "label": "Start Supply Ops lab server",
                    "command": (
                        "python3 labs/supply_ops_lab/server.py --host 127.0.0.1 "
                        "--port 8094 --upstream http://127.0.0.1:8080"
                    ),
                },
                {
                    "label": "Check lab health",
                    "command": "curl -sS http://127.0.0.1:8094/health",
                },
            ],
            "demo_steps": [
                "Load the lab, confirm the boundary notes, and keep the browser in render-only mode.",
                "Review a preset before running it so the translated proposal, policy preview, replay summary, and simulation summary are understandable without raw JSON first.",
                "Run the selected preset through the upstream session and proposal endpoints, then compare the executed policy posture to the previewed summary.",
                "Use the reviewed scenario artifact references as evidence only; connector-ingress UI and execution-evidence UI stay out of the supported lab scope.",
            ],
            "smoke_checks": [
                {
                    "label": "Compile the standalone server",
                    "command": (
                        "env PYTHONPYCACHEPREFIX=/tmp/world-runtime-pycache "
                        "python3 -m py_compile labs/supply_ops_lab/server.py"
                    ),
                },
                {
                    "label": "Run targeted lab pytest coverage",
                    "command": "python3 -m pytest -q tests/labs/test_supply_ops_lab.py",
                },
                {
                    "label": "Check milestone doc consistency",
                    "command": (
                        "rg -n \"SO-P[0-4]\" labs/supply_ops_lab/ROADMAP.md "
                        "labs/supply_ops_lab/STATUS.md "
                        "labs/supply_ops_lab/README.md "
                        "labs/supply_ops_lab/NEW_THREAD_KICKOFF_PROMPT.md "
                        "labs/supply_ops_lab/NEW_THREAD_SO_P0.md "
                        "labs/supply_ops_lab/NEW_THREAD_SO_P1.md "
                        "labs/supply_ops_lab/NEW_THREAD_SO_P2.md "
                        "labs/supply_ops_lab/NEW_THREAD_SO_P3.md "
                        "labs/supply_ops_lab/NEW_THREAD_SO_P4.md"
                    ),
                },
            ],
        }

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        target_url = self.upstream_base + path
        request = urllib.request.Request(
            target_url,
            data=_json_bytes(payload),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                parsed = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ValueError("upstream request failed for %s: %s" % (path, detail)) from exc
        except urllib.error.URLError as exc:
            raise ValueError("upstream unreachable for %s: %s" % (path, exc.reason)) from exc

        if not parsed.get("ok"):
            error = parsed.get("error", {})
            if isinstance(error, dict):
                message = error.get("message", "upstream returned an error")
            else:
                message = str(error)
            raise ValueError("upstream request failed for %s: %s" % (path, message))
        return parsed["result"]


class SupplyOpsLabHandler(BaseHTTPRequestHandler):
    upstream_base: str = "http://127.0.0.1:8080"
    service: Optional[SupplyOpsLabService] = None

    def do_GET(self) -> None:  # noqa: N802
        requested = self.path.split("?", 1)[0]
        if requested == "/health":
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "lab": "supply_ops_lab",
                    "milestone": LAB_MILESTONE,
                    "supported_path": "preserved SO-P3 operator/reference route plus SO-P4 Decision Explorer concept route",
                },
            )
            return

        if requested.startswith("/api/v1/"):
            self._proxy("GET")
            return

        if requested == "/api/supply-ops/bootstrap":
            assert self.service is not None
            self._send_json(HTTPStatus.OK, {"ok": True, "result": self.service.build_bootstrap_payload()})
            return

        if requested == DECISION_EXPLORER_BOOTSTRAP_ENDPOINT:
            assert self.service is not None
            self._send_json(
                HTTPStatus.OK,
                {"ok": True, "result": self.service.build_decision_explorer_bootstrap_payload()},
            )
            return

        if requested == DECISION_EXPLORER_ROUTE:
            self._serve_decision_explorer()
            return

        if requested in {"/", ""}:
            self._serve_index()
            return

        if self._serve_static(requested):
            return

        self._serve_index()

    def do_POST(self) -> None:  # noqa: N802
        requested = self.path.split("?", 1)[0]
        if requested.startswith("/api/v1/"):
            self._proxy("POST")
            return

        if requested == "/api/supply-ops/run":
            assert self.service is not None
            try:
                request_body = self._read_json_body()
            except ValueError as exc:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": {"code": "bad_request", "message": str(exc)}},
                )
                return
            try:
                payload = self.service.run_preset_flow(
                    request_body.get("fixture_name", REVIEWED_FIXTURE_NAME)
                )
            except ValueError as exc:
                status = (
                    HTTPStatus.BAD_REQUEST
                    if str(exc).startswith("unsupported preset fixture")
                    else HTTPStatus.BAD_GATEWAY
                )
                self._send_json(
                    status,
                    {
                        "ok": False,
                        "error": {
                            "code": (
                                "bad_request"
                                if status == HTTPStatus.BAD_REQUEST
                                else "upstream_error"
                            ),
                            "message": str(exc),
                        },
                    },
                )
                return
            self._send_json(HTTPStatus.OK, {"ok": True, "result": payload})
            return

        if requested == DECISION_EXPLORER_EVALUATE_ENDPOINT:
            assert self.service is not None
            try:
                request_body = self._read_json_body()
            except ValueError as exc:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": {"code": "bad_request", "message": str(exc)}},
                )
                return
            payload = self.service.evaluate_decision_explorer(
                weights=request_body.get("weights", {}),
                simulation_mode=request_body.get("simulation_mode", "include"),
            )
            self._send_json(HTTPStatus.OK, {"ok": True, "result": payload})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": {"code": "not_found", "message": "unknown endpoint"}})

    def _asset_root(self) -> Path:
        return ROOT

    def _serve_index(self) -> None:
        self._serve_file(self._asset_root() / "index.html", "text/html; charset=utf-8")

    def _serve_decision_explorer(self) -> None:
        self._serve_file(self._asset_root() / "decision-explorer.html", "text/html; charset=utf-8")

    def _serve_static(self, requested_path: str) -> bool:
        if requested_path.startswith("/"):
            requested_path = requested_path[1:]
        if not requested_path:
            return False
        candidate = (self._asset_root() / requested_path).resolve()
        root = self._asset_root().resolve()
        if root not in candidate.parents and candidate != root:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "error": {"code": "invalid_path", "message": "invalid asset path"}},
            )
            return True
        if not candidate.exists() or not candidate.is_file():
            return False

        guessed, _ = mimetypes.guess_type(candidate.name)
        content_type = guessed or "application/octet-stream"
        if content_type.startswith("text/"):
            content_type = f"{content_type}; charset=utf-8"
        self._serve_file(candidate, content_type)
        return True

    def _serve_file(self, path: Path, content_type: str) -> None:
        payload = path.read_bytes()
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _proxy(self, method: str) -> None:
        target_url = self.upstream_base.rstrip("/") + self.path[len("/api") :]
        body: Optional[bytes] = None
        if method == "POST":
            try:
                body = self._read_body_bytes()
            except ValueError as exc:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": {"code": "bad_length", "message": str(exc)}},
                )
                return

        headers = {"Accept": "application/json"}
        auth = self.headers.get("Authorization")
        if auth:
            headers["Authorization"] = auth
        if body is not None:
            headers["Content-Type"] = self.headers.get("Content-Type", "application/json")

        request = urllib.request.Request(target_url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type", "application/json")
                self.send_response(response.status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as exc:
            payload = exc.read() or _json_bytes(
                {"ok": False, "error": {"code": "upstream_http_error", "message": "upstream returned an error"}}
            )
            self.send_response(exc.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except urllib.error.URLError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {
                    "ok": False,
                    "error": {
                        "code": "upstream_unreachable",
                        "message": str(exc.reason),
                    },
                },
            )

    def _read_body_bytes(self) -> bytes:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            content_length = int(raw_length)
        except ValueError:
            raise ValueError("invalid content length")
        return self.rfile.read(max(content_length, 0)) if content_length > 0 else b""

    def _read_json_body(self) -> Dict[str, Any]:
        body = self._read_body_bytes()
        if not body:
            return {}
        try:
            parsed = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("request body must be valid JSON") from exc
        if not isinstance(parsed, dict):
            raise ValueError("request body must be a JSON object")
        return parsed

    def _send_json(self, status: HTTPStatus, payload: Dict[str, Any]) -> None:
        blob = _json_bytes(payload)
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def log_message(self, fmt: str, *args: object) -> None:  # noqa: A003
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Supply Ops Lab standalone server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8094)
    parser.add_argument("--upstream", default="http://127.0.0.1:8080")
    args = parser.parse_args()

    handler = type("ConfiguredSupplyOpsLabHandler", (SupplyOpsLabHandler,), {})
    handler.upstream_base = args.upstream
    handler.service = SupplyOpsLabService(REPO_ROOT, args.upstream)

    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(
        "Supply Ops Lab serving at http://%s:%s (upstream=%s)"
        % (args.host, args.port, args.upstream),
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
