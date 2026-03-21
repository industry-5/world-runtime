from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.policy_engine import DeterministicPolicyEngine

from adapters.world_game.authoring import (
    create_world_game_template_bundle_draft,
    instantiate_world_game_template_bundle,
    list_world_game_template_bundles,
    load_world_game_template_bundle,
    publish_world_game_template_bundle,
    validate_world_game_template_bundle_workflow,
)
from adapters.world_game.collaboration import (
    add_actor_record,
    advance_stage,
    archive_annotation,
    assert_stage_allows_action,
    build_annotation_provenance,
    build_annotation_record,
    build_branch_provenance,
    build_facilitation_state,
    build_proposal_provenance,
    build_proposal_record,
    build_scenario_provenance,
    build_timeline_event,
    ensure_collaboration_state,
    get_actor_record,
    inspect_provenance,
    list_actor_records,
    list_annotations,
    reject_proposal_record,
    remove_actor_record,
    session_snapshot,
    set_stage,
    submit_proposal_record,
    update_annotation_record,
    update_proposal_record,
    upsert_provenance_record,
)
from adapters.world_game.reporting import (
    build_equity_report,
    inspect_network_state,
    scenario_equity_summary,
    scenario_network_summary,
)
from adapters.world_game.runtime import (
    compare_branches,
    create_branch,
    initialize_baseline_state,
    list_world_game_scenarios,
    load_world_game_scenario,
    replay_world_game,
    run_turn,
)


class WorldGameService:
    def __init__(self, repo_root: Path, policy_engine: DeterministicPolicyEngine) -> None:
        self.repo_root = repo_root
        self.policy_engine = policy_engine
        self.context_by_session: Dict[str, Dict[str, Any]] = {}

    def clear_session(self, session_id: str) -> None:
        self.context_by_session.pop(session_id, None)

    def scenario_list(self, examples_root: Optional[str] = None) -> Dict[str, Any]:
        root = Path(examples_root) if examples_root else (self.repo_root / "examples")
        scenarios = list_world_game_scenarios(root)
        return {
            "scenarios": scenarios,
            "count": len(scenarios),
        }

    def scenario_load(
        self,
        session_id: str,
        scenario_id: Optional[str] = None,
        scenario_path: Optional[str] = None,
        branch_id: str = "baseline",
        policy_pack_path: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        scenario_file = self._resolve_scenario_path(scenario_id=scenario_id, scenario_path=scenario_path)
        scenario = load_world_game_scenario(scenario_file)
        policies = self._load_policies(
            explicit_policy_pack_path=policy_pack_path,
            scenario_policy_ref=scenario.get("policy_pack_ref"),
        )
        baseline = initialize_baseline_state(scenario=scenario, branch_id=branch_id, parent_branch_id=None)
        context = self.ensure_session_context(session_id)
        collaboration_enabled = bool(context.get("session_meta", {}).get("collaboration_enabled"))
        ensure_collaboration_state(context, session_id=session_id, collaboration_enabled=collaboration_enabled)
        context["scenario"] = scenario
        context["policies"] = policies
        context["branches"] = {branch_id: baseline}
        context["facilitation_state"] = context.get("facilitation_state") or build_facilitation_state(
            enforce_stage_gates=collaboration_enabled
        )
        self._upsert_branch_provenance(context, branch_id=branch_id, source_branch_id=None, proposal_id=None)
        upsert_provenance_record(
            context["provenance"],
            artifact_type="scenario",
            artifact_id=scenario["scenario_id"],
            record=build_scenario_provenance(scenario=scenario, scenario_path=str(scenario_file), session_id=session_id),
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.scenario.loaded",
            payload={"scenario_id": scenario["scenario_id"], "branch_id": branch_id},
            actor_id=actor_id,
        )
        result = {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "label": scenario["label"],
            "description": scenario["description"],
            "policy_count": len(policies),
            "regions": [region["region_id"] for region in scenario["regions"]],
            "intervention_ids": [item["intervention_id"] for item in scenario["interventions"]],
            "shock_ids": [item["shock_id"] for item in scenario["shocks"]],
            "strategies": [item["strategy_id"] for item in scenario.get("strategies", [])],
            "branch": self.branch_summary(baseline),
            "session": session_snapshot(context),
        }
        if scenario.get("has_network_contract"):
            result["network_summary"] = scenario_network_summary(scenario)
        if scenario.get("has_equity_contract"):
            result["equity_summary"] = scenario_equity_summary(scenario)
        return result

    def turn_run(
        self,
        session_id: str,
        branch_id: str = "baseline",
        intervention_ids: Optional[List[str]] = None,
        shock_ids: Optional[List[str]] = None,
        approval_status: str = "approved",
        actor_id: Optional[str] = None,
        proposal_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        self._assert_capability(context, actor_id, "simulation.run")
        assert_stage_allows_action(context["facilitation_state"], "turn.run")
        branch = self.require_branch(session_id, branch_id)
        result = run_turn(
            state=branch,
            scenario=context["scenario"],
            intervention_ids=intervention_ids or [],
            shock_ids=shock_ids or [],
            policy_evaluator=self.policy_engine,
            policies=context["policies"],
            approval_status=approval_status,
        )
        if result["turn_result"]["committed"]:
            context["branches"][branch_id] = result["state"]
            self._upsert_branch_provenance(
                context,
                branch_id=branch_id,
                source_branch_id=branch.get("parent_branch_id"),
                proposal_id=proposal_id,
                turn_result=result["turn_result"],
            )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.turn.run",
            payload={
                "branch_id": branch_id,
                "proposal_id": proposal_id,
                "intervention_ids": deepcopy(intervention_ids or []),
                "shock_ids": deepcopy(shock_ids or []),
                "policy_outcome": result["turn_result"]["policy_outcome"],
                "committed": result["turn_result"]["committed"],
            },
            actor_id=actor_id,
        )

        updated_branch = context["branches"][branch_id]
        return {
            "session_id": session_id,
            "scenario_id": context["scenario"]["scenario_id"],
            "branch_id": branch_id,
            "turn_result": result["turn_result"],
            "policy_report": result["policy_report"],
            "branch": self.branch_summary(updated_branch),
            "timeline_event": deepcopy(context["timeline"][-1]),
        }

    def branch_create(
        self,
        session_id: str,
        source_branch_id: str,
        branch_id: str,
        actor_id: Optional[str] = None,
        proposal_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        self._assert_capability(context, actor_id, "branch.create")
        assert_stage_allows_action(context["facilitation_state"], "branch.create")
        if branch_id in context["branches"]:
            raise ValueError("branch_id already exists: %s" % branch_id)

        source_branch = self.require_branch(session_id, source_branch_id)
        branch = create_branch(
            base_state=source_branch,
            branch_id=branch_id,
            parent_branch_id=source_branch_id,
        )
        context["branches"][branch_id] = branch
        self._upsert_branch_provenance(
            context,
            branch_id=branch_id,
            source_branch_id=source_branch_id,
            proposal_id=proposal_id,
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.branch.created",
            payload={"source_branch_id": source_branch_id, "branch_id": branch_id, "proposal_id": proposal_id},
            actor_id=actor_id,
        )
        return {
            "session_id": session_id,
            "scenario_id": context["scenario"]["scenario_id"],
            "branch": self.branch_summary(branch),
        }

    def branch_compare(
        self,
        session_id: str,
        branch_ids: Optional[List[str]] = None,
        include_annotation_summary: bool = False,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        selected_ids = branch_ids or sorted(context["branches"].keys())
        branches = [self.require_branch(session_id, branch_id) for branch_id in selected_ids]
        compared = compare_branches(context["scenario"], branches)
        if include_annotation_summary:
            compared["annotation_summary"] = {
                branch_id: list_annotations(context["annotations"], target_type="branch", target_id=branch_id)
                for branch_id in selected_ids
            }
        return compared

    def replay_run(self, session_id: str, branch_id: str = "baseline") -> Dict[str, Any]:
        context = self.require_context(session_id)
        branch = self.require_branch(session_id, branch_id)
        replay = replay_world_game(
            scenario=context["scenario"],
            events=branch.get("event_log", []),
            policy_evaluator=self.policy_engine,
            policies=context["policies"],
        )
        live_score = float(branch.get("scorecard", {}).get("composite_score", 0.0))
        replay_score = float(replay["state"].get("scorecard", {}).get("composite_score", 0.0))
        baseline_state = initialize_baseline_state(
            scenario=context["scenario"],
            branch_id=branch_id,
            parent_branch_id=branch.get("parent_branch_id"),
        )

        replay_frames: List[Dict[str, Any]] = [
            {
                "turn_index": 0,
                "policy_outcome": None,
                "approval_status": None,
                "applied_intervention_ids": [],
                "applied_shock_ids": [],
                "committed": True,
                "scorecard": deepcopy(baseline_state.get("scorecard", {})),
                "network_diagnostics": inspect_network_state(scenario=context["scenario"], state=baseline_state),
                "equity_report": deepcopy(
                    baseline_state.get("latest_equity_report") or build_equity_report(baseline_state, context["scenario"])
                ),
            }
        ]
        replay_frames.extend(deepcopy(replay.get("turn_results", [])))

        return {
            "session_id": session_id,
            "scenario_id": context["scenario"]["scenario_id"],
            "branch_id": branch_id,
            "replay_turn_count": len(replay["turn_results"]),
            "live_composite_score": live_score,
            "replay_composite_score": replay_score,
            "replay_matches_live": round(live_score, 6) == round(replay_score, 6),
            "replay_frames": replay_frames,
            "replay_frame_count": len(replay_frames),
        }

    def network_inspect(self, session_id: str, branch_id: str = "baseline") -> Dict[str, Any]:
        context = self.require_context(session_id)
        branch = self.require_branch(session_id, branch_id)
        return inspect_network_state(scenario=context["scenario"], state=branch)

    def equity_report(
        self,
        session_id: str,
        branch_id: str = "baseline",
        branch_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        selected_ids = branch_ids or [branch_id]
        reports = []
        for selected_branch_id in sorted(set(selected_ids)):
            branch = self.require_branch(session_id, selected_branch_id)
            report = branch.get("latest_equity_report") or build_equity_report(branch, context["scenario"])
            reports.append(
                {
                    "branch_id": selected_branch_id,
                    "turn": int(branch.get("turn", 0)),
                    "equity_report": deepcopy(report),
                }
            )

        if len(reports) == 1:
            return {
                "session_id": session_id,
                "scenario_id": context["scenario"]["scenario_id"],
                "branch_id": reports[0]["branch_id"],
                "turn": reports[0]["turn"],
                "equity_report": reports[0]["equity_report"],
            }

        return {
            "session_id": session_id,
            "scenario_id": context["scenario"]["scenario_id"],
            "reports": reports,
            "count": len(reports),
        }

    def collaboration_session_create(
        self,
        session_id: str,
        label: Optional[str] = None,
        description: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_type: str = "human",
        roles: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        display_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.ensure_session_context(session_id)
        ensure_collaboration_state(
            context,
            session_id=session_id,
            label=label,
            description=description,
            actor_id=actor_id,
            collaboration_enabled=True,
        )
        context["facilitation_state"] = build_facilitation_state(enforce_stage_gates=True)
        actor = None
        if actor_id:
            actor = add_actor_record(
                context,
                actor_id=actor_id,
                actor_type=actor_type,
                roles=roles or ["facilitator"],
                capabilities=capabilities,
                display_name=display_name,
            )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.session.created",
            payload={"label": context["session_meta"]["label"], "actor_id": actor_id},
            actor_id=actor_id,
        )
        return {
            "session_id": session_id,
            "session": session_snapshot(context),
            "actor": actor,
        }

    def collaboration_session_get(self, session_id: str) -> Dict[str, Any]:
        context = self.ensure_session_context(session_id)
        ensure_collaboration_state(
            context,
            session_id=session_id,
            collaboration_enabled=bool(context.get("session_meta", {}).get("collaboration_enabled")),
        )
        snapshot = session_snapshot(context)
        snapshot["timeline"] = deepcopy(context.get("timeline", []))
        return {
            "session_id": session_id,
            "session": snapshot,
        }

    def collaboration_session_export(
        self,
        session_id: str,
        output_path: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.ensure_session_context(session_id)
        ensure_collaboration_state(
            context,
            session_id=session_id,
            collaboration_enabled=bool(context.get("session_meta", {}).get("collaboration_enabled")),
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.session.exported",
            payload={"output_path": output_path},
            actor_id=actor_id,
        )
        bundle = {
            "bundle_type": "world_game.collaboration.session",
            "bundle_version": "1.0",
            "exported_at": self._now(),
            "session_id": session_id,
            "context": deepcopy(context),
        }
        serializable_bundle = self._json_safe(bundle)
        resolved_output_path = None
        if output_path:
            resolved_output_path = self.resolve_repo_relative_path(output_path)
            self._write_json(resolved_output_path, serializable_bundle)

        return {
            "session_id": session_id,
            "bundle": serializable_bundle,
            "output_path": str(resolved_output_path) if resolved_output_path else None,
            "summary": self._collaboration_summary(context),
        }

    def collaboration_session_import(
        self,
        session_id: str,
        bundle: Optional[Dict[str, Any]] = None,
        bundle_path: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if bundle is None and not bundle_path:
            raise ValueError("bundle or bundle_path is required")

        resolved_bundle_path = None
        loaded = deepcopy(bundle) if bundle is not None else None
        if loaded is None:
            resolved_bundle_path = self.resolve_repo_relative_path(bundle_path)
            with resolved_bundle_path.open("r", encoding="utf-8") as handle:
                loaded = json.load(handle)

        if not isinstance(loaded, dict):
            raise ValueError("collaboration bundle must be a JSON object")
        imported_context = deepcopy(loaded.get("context") if "context" in loaded else loaded)
        if not isinstance(imported_context, dict):
            raise ValueError("collaboration bundle context must be an object")

        imported_meta = imported_context.get("session_meta")
        imported_label = imported_meta.get("label") if isinstance(imported_meta, dict) else None
        imported_description = imported_meta.get("description") if isinstance(imported_meta, dict) else None

        ensure_collaboration_state(
            imported_context,
            session_id=session_id,
            label=imported_label,
            description=imported_description,
            collaboration_enabled=True,
        )
        imported_context["session_meta"]["session_id"] = session_id
        imported_context["session_meta"]["collaboration_enabled"] = True
        imported_context["facilitation_state"] = imported_context.get("facilitation_state") or build_facilitation_state(
            enforce_stage_gates=True
        )
        imported_context["facilitation_state"]["enforce_stage_gates"] = True
        imported_context["branches"] = imported_context.get("branches") if isinstance(imported_context.get("branches"), dict) else {}
        imported_context["proposals"] = imported_context.get("proposals") if isinstance(imported_context.get("proposals"), dict) else {}
        imported_context["annotations"] = imported_context.get("annotations") if isinstance(imported_context.get("annotations"), dict) else {}
        imported_context["timeline"] = imported_context.get("timeline") if isinstance(imported_context.get("timeline"), list) else []
        imported_context["provenance"] = imported_context.get("provenance") if isinstance(imported_context.get("provenance"), dict) else {"artifacts": {}}
        imported_context["_counters"] = imported_context.get("_counters") if isinstance(imported_context.get("_counters"), dict) else {}
        imported_context["_counters"]["proposal"] = max(
            int(imported_context["_counters"].get("proposal", 0) or 0),
            len(imported_context["proposals"]),
        )
        imported_context["_counters"]["annotation"] = max(
            int(imported_context["_counters"].get("annotation", 0) or 0),
            len(imported_context["annotations"]),
        )

        self.context_by_session[session_id] = imported_context
        self._append_timeline_event(
            imported_context,
            session_id=session_id,
            event_type="world_game.session.imported",
            payload={
                "bundle_type": loaded.get("bundle_type"),
                "bundle_version": loaded.get("bundle_version"),
                "source_session_id": loaded.get("session_id"),
            },
            actor_id=actor_id,
        )

        scenario = imported_context.get("scenario") if isinstance(imported_context.get("scenario"), dict) else None
        scenario_payload = None
        if scenario is not None:
            scenario_payload = {
                "scenario_id": scenario.get("scenario_id"),
                "label": scenario.get("label"),
                "description": scenario.get("description"),
                "intervention_ids": [
                    item.get("intervention_id")
                    for item in scenario.get("interventions", [])
                    if isinstance(item, dict) and item.get("intervention_id")
                ],
                "shock_ids": [
                    item.get("shock_id")
                    for item in scenario.get("shocks", [])
                    if isinstance(item, dict) and item.get("shock_id")
                ],
            }

        branches = {}
        for branch_id in sorted(imported_context.get("branches", {}).keys()):
            branch = imported_context["branches"][branch_id]
            if not isinstance(branch, dict):
                continue
            branches[branch_id] = self.branch_summary(branch)

        proposals = []
        for proposal_id in sorted(imported_context.get("proposals", {}).keys()):
            proposals.append(deepcopy(imported_context["proposals"][proposal_id]))

        annotations = list_annotations(imported_context.get("annotations", {}), include_archived=True)
        snapshot = session_snapshot(imported_context)
        snapshot["timeline"] = deepcopy(imported_context.get("timeline", []))

        return {
            "session_id": session_id,
            "session": snapshot,
            "scenario": scenario_payload,
            "branches": branches,
            "proposals": proposals,
            "annotations": annotations,
            "summary": self._collaboration_summary(imported_context),
            "import_source": {
                "bundle_path": str(resolved_bundle_path) if resolved_bundle_path else None,
                "bundle_type": loaded.get("bundle_type"),
                "bundle_version": loaded.get("bundle_version"),
                "source_session_id": loaded.get("session_id"),
            },
        }

    def collaboration_actor_add(
        self,
        session_id: str,
        actor_id: str,
        actor_type: str = "human",
        roles: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        display_name: Optional[str] = None,
        requested_by_actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.ensure_session_context(session_id)
        ensure_collaboration_state(context, session_id=session_id, collaboration_enabled=True)
        self._assert_capability(context, requested_by_actor_id, "session.manage")
        actor = add_actor_record(
            context,
            actor_id=actor_id,
            actor_type=actor_type,
            roles=roles,
            capabilities=capabilities,
            display_name=display_name,
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.session.actor.added",
            payload={"actor_id": actor["actor_id"], "roles": actor["roles"]},
            actor_id=requested_by_actor_id or actor_id,
        )
        return {"session_id": session_id, "actor": actor, "actors": list_actor_records(context)}

    def collaboration_actor_remove(
        self,
        session_id: str,
        actor_id: str,
        requested_by_actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.ensure_session_context(session_id)
        ensure_collaboration_state(context, session_id=session_id, collaboration_enabled=True)
        self._assert_capability(context, requested_by_actor_id, "session.manage")
        actor = remove_actor_record(context, actor_id)
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.session.actor.removed",
            payload={"actor_id": actor_id},
            actor_id=requested_by_actor_id,
        )
        return {"session_id": session_id, "removed_actor": actor, "actors": list_actor_records(context)}

    def collaboration_actor_list(self, session_id: str) -> Dict[str, Any]:
        context = self.ensure_session_context(session_id)
        ensure_collaboration_state(
            context,
            session_id=session_id,
            collaboration_enabled=bool(context.get("session_meta", {}).get("collaboration_enabled")),
        )
        actors = list_actor_records(context)
        return {"session_id": session_id, "actors": actors, "count": len(actors)}

    def proposal_create(
        self,
        session_id: str,
        proposal_id: Optional[str] = None,
        title: str = "",
        rationale: str = "",
        assumptions: Optional[List[str]] = None,
        intended_interventions: Optional[List[str]] = None,
        expected_outcomes: Optional[List[str]] = None,
        evidence_refs: Optional[List[Dict[str, Any]]] = None,
        planned_turn_sequence: Optional[List[Dict[str, Any]]] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        self._assert_capability(context, actor_id, "proposal.create")
        assert_stage_allows_action(context["facilitation_state"], "proposal.create")
        proposal_key = proposal_id or self._next_id(context, prefix="proposal")
        proposal = build_proposal_record(
            proposal_id=proposal_key,
            title=title or proposal_key,
            author_actor_id=actor_id,
            rationale=rationale,
            assumptions=assumptions,
            intended_interventions=intended_interventions,
            expected_outcomes=expected_outcomes,
            evidence_refs=evidence_refs,
            planned_turn_sequence=planned_turn_sequence,
        )
        context["proposals"][proposal_key] = proposal
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.proposal.created",
            payload={"proposal_id": proposal_key},
            actor_id=actor_id,
        )
        upsert_provenance_record(
            context["provenance"],
            artifact_type="proposal",
            artifact_id=proposal_key,
            record=build_proposal_provenance(proposal, scenario_id=context["scenario"]["scenario_id"]),
        )
        return {"session_id": session_id, "proposal": deepcopy(proposal)}

    def proposal_update(
        self,
        session_id: str,
        proposal_id: str,
        updates: Optional[Dict[str, Any]] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        self._assert_capability(context, actor_id, "proposal.create")
        assert_stage_allows_action(context["facilitation_state"], "proposal.update")
        proposal = self._require_proposal(context, proposal_id)
        updated = update_proposal_record(proposal, updates or {})
        context["proposals"][proposal_id] = updated
        upsert_provenance_record(
            context["provenance"],
            artifact_type="proposal",
            artifact_id=proposal_id,
            record=build_proposal_provenance(updated, scenario_id=context["scenario"]["scenario_id"]),
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.proposal.updated",
            payload={"proposal_id": proposal_id},
            actor_id=actor_id,
        )
        return {"session_id": session_id, "proposal": deepcopy(updated)}

    def proposal_get(self, session_id: str, proposal_id: str) -> Dict[str, Any]:
        context = self.require_context(session_id)
        proposal = self._require_proposal(context, proposal_id)
        return {"session_id": session_id, "proposal": deepcopy(proposal)}

    def proposal_list(self, session_id: str, status: Optional[str] = None) -> Dict[str, Any]:
        context = self.require_context(session_id)
        proposals = []
        for proposal_id in sorted(context["proposals"].keys()):
            record = context["proposals"][proposal_id]
            if status and record.get("status") != status:
                continue
            proposals.append(deepcopy(record))
        return {"session_id": session_id, "proposals": proposals, "count": len(proposals)}

    def proposal_submit(self, session_id: str, proposal_id: str, actor_id: Optional[str] = None) -> Dict[str, Any]:
        context = self.require_context(session_id)
        self._assert_capability(context, actor_id, "proposal.submit")
        assert_stage_allows_action(context["facilitation_state"], "proposal.submit")
        proposal = self._require_proposal(context, proposal_id)
        submitted = submit_proposal_record(proposal, actor_id=actor_id)
        context["proposals"][proposal_id] = submitted
        upsert_provenance_record(
            context["provenance"],
            artifact_type="proposal",
            artifact_id=proposal_id,
            record=build_proposal_provenance(submitted, scenario_id=context["scenario"]["scenario_id"]),
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.proposal.submitted",
            payload={"proposal_id": proposal_id},
            actor_id=actor_id,
        )
        return {"session_id": session_id, "proposal": deepcopy(submitted)}

    def proposal_adopt(
        self,
        session_id: str,
        proposal_id: str,
        branch_id: Optional[str] = None,
        source_branch_id: str = "baseline",
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        self._assert_capability(context, actor_id, "proposal.adopt")
        assert_stage_allows_action(context["facilitation_state"], "proposal.adopt")
        proposal = self._require_proposal(context, proposal_id)
        if proposal.get("status") not in {"submitted", "under_review", "draft"}:
            raise ValueError("proposal %s cannot be adopted from status %s" % (proposal_id, proposal.get("status")))
        adopted_branch_id = branch_id or ("%s.branch" % proposal_id.replace(".", "-"))
        if adopted_branch_id not in context["branches"]:
            source_branch = self.require_branch(session_id, source_branch_id)
            branch = create_branch(
                base_state=source_branch,
                branch_id=adopted_branch_id,
                parent_branch_id=source_branch_id,
            )
            context["branches"][adopted_branch_id] = branch
            self._upsert_branch_provenance(
                context,
                branch_id=adopted_branch_id,
                source_branch_id=source_branch_id,
                proposal_id=proposal_id,
            )
            self._append_timeline_event(
                context,
                session_id=session_id,
                event_type="world_game.branch.created",
                payload={
                    "source_branch_id": source_branch_id,
                    "branch_id": adopted_branch_id,
                    "proposal_id": proposal_id,
                    "created_via": "proposal.adopt",
                },
                actor_id=actor_id,
            )
            branch_summary = self.branch_summary(branch)
        else:
            branch_summary = self.branch_summary(context["branches"][adopted_branch_id])
        proposal["status"] = "adopted"
        proposal["adopted_branch_id"] = adopted_branch_id
        proposal.setdefault("review_history", []).append(
            {"action": "adopted", "actor_id": actor_id, "branch_id": adopted_branch_id, "at": self._now()}
        )
        proposal["updated_at"] = self._now()
        context["proposals"][proposal_id] = proposal
        upsert_provenance_record(
            context["provenance"],
            artifact_type="proposal",
            artifact_id=proposal_id,
            record=build_proposal_provenance(proposal, scenario_id=context["scenario"]["scenario_id"]),
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.proposal.adopted",
            payload={"proposal_id": proposal_id, "branch_id": adopted_branch_id},
            actor_id=actor_id,
        )
        return {
            "session_id": session_id,
            "proposal": deepcopy(proposal),
            "branch": deepcopy(branch_summary),
        }

    def proposal_reject(
        self,
        session_id: str,
        proposal_id: str,
        actor_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        self._assert_capability(context, actor_id, "proposal.reject")
        assert_stage_allows_action(context["facilitation_state"], "proposal.reject")
        proposal = self._require_proposal(context, proposal_id)
        rejected = reject_proposal_record(proposal, actor_id=actor_id, reason=reason)
        context["proposals"][proposal_id] = rejected
        upsert_provenance_record(
            context["provenance"],
            artifact_type="proposal",
            artifact_id=proposal_id,
            record=build_proposal_provenance(rejected, scenario_id=context["scenario"]["scenario_id"]),
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.proposal.rejected",
            payload={"proposal_id": proposal_id, "reason": reason},
            actor_id=actor_id,
        )
        return {"session_id": session_id, "proposal": deepcopy(rejected)}

    def session_stage_get(self, session_id: str) -> Dict[str, Any]:
        context = self.ensure_session_context(session_id)
        ensure_collaboration_state(
            context,
            session_id=session_id,
            collaboration_enabled=bool(context.get("session_meta", {}).get("collaboration_enabled")),
        )
        return {"session_id": session_id, "facilitation_state": deepcopy(context["facilitation_state"])}

    def session_stage_set(
        self,
        session_id: str,
        stage: str,
        actor_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.ensure_session_context(session_id)
        ensure_collaboration_state(context, session_id=session_id, collaboration_enabled=True)
        self._assert_capability(context, actor_id, "session.stage.set")
        updated = set_stage(context["facilitation_state"], stage=stage, actor_id=actor_id, reason=reason)
        context["facilitation_state"] = updated
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.session.stage.set",
            payload={"stage": updated["stage"], "reason": reason},
            actor_id=actor_id,
        )
        return {"session_id": session_id, "facilitation_state": deepcopy(updated)}

    def session_stage_advance(
        self,
        session_id: str,
        actor_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.ensure_session_context(session_id)
        ensure_collaboration_state(context, session_id=session_id, collaboration_enabled=True)
        self._assert_capability(context, actor_id, "session.stage.advance")
        updated = advance_stage(context["facilitation_state"], actor_id=actor_id, reason=reason)
        context["facilitation_state"] = updated
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.session.stage.advanced",
            payload={"stage": updated["stage"], "reason": reason},
            actor_id=actor_id,
        )
        return {"session_id": session_id, "facilitation_state": deepcopy(updated)}

    def annotation_create(
        self,
        session_id: str,
        annotation_id: Optional[str] = None,
        annotation_type: str = "",
        target_type: str = "",
        target_id: str = "",
        body: str = "",
        evidence_refs: Optional[List[Dict[str, Any]]] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        self._assert_capability(context, actor_id, "annotation.author")
        assert_stage_allows_action(context["facilitation_state"], "annotation.create")
        if not target_type or not target_id:
            raise ValueError("target_type and target_id are required")
        record = build_annotation_record(
            annotation_id=annotation_id or self._next_id(context, prefix="annotation"),
            annotation_type=annotation_type,
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            body=body,
            evidence_refs=evidence_refs,
        )
        context["annotations"][record["annotation_id"]] = record
        upsert_provenance_record(
            context["provenance"],
            artifact_type="annotation",
            artifact_id=record["annotation_id"],
            record=build_annotation_provenance(record),
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.annotation.created",
            payload={"annotation_id": record["annotation_id"], "target_type": target_type, "target_id": target_id},
            actor_id=actor_id,
        )
        return {"session_id": session_id, "annotation": deepcopy(record)}

    def annotation_list(
        self,
        session_id: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        include_archived: bool = False,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        annotations = list_annotations(
            context["annotations"],
            target_type=target_type,
            target_id=target_id,
            include_archived=include_archived,
        )
        return {"session_id": session_id, "annotations": annotations, "count": len(annotations)}

    def annotation_update(
        self,
        session_id: str,
        annotation_id: str,
        body: Optional[str] = None,
        evidence_refs: Optional[List[Dict[str, Any]]] = None,
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.require_context(session_id)
        self._assert_capability(context, actor_id, "annotation.author")
        assert_stage_allows_action(context["facilitation_state"], "annotation.update")
        annotation = self._require_annotation(context, annotation_id)
        updated = update_annotation_record(annotation, body=body, evidence_refs=evidence_refs)
        context["annotations"][annotation_id] = updated
        upsert_provenance_record(
            context["provenance"],
            artifact_type="annotation",
            artifact_id=annotation_id,
            record=build_annotation_provenance(updated),
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.annotation.updated",
            payload={"annotation_id": annotation_id},
            actor_id=actor_id,
        )
        return {"session_id": session_id, "annotation": deepcopy(updated)}

    def annotation_archive(self, session_id: str, annotation_id: str, actor_id: Optional[str] = None) -> Dict[str, Any]:
        context = self.require_context(session_id)
        self._assert_capability(context, actor_id, "annotation.author")
        annotation = self._require_annotation(context, annotation_id)
        archived = archive_annotation(annotation, actor_id=actor_id)
        context["annotations"][annotation_id] = archived
        upsert_provenance_record(
            context["provenance"],
            artifact_type="annotation",
            artifact_id=annotation_id,
            record=build_annotation_provenance(archived),
        )
        self._append_timeline_event(
            context,
            session_id=session_id,
            event_type="world_game.annotation.archived",
            payload={"annotation_id": annotation_id},
            actor_id=actor_id,
        )
        return {"session_id": session_id, "annotation": deepcopy(archived)}

    def provenance_inspect(
        self,
        session_id: str,
        artifact_type: Optional[str] = None,
        artifact_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.ensure_session_context(session_id)
        ensure_collaboration_state(
            context,
            session_id=session_id,
            collaboration_enabled=bool(context.get("session_meta", {}).get("collaboration_enabled")),
        )
        result = inspect_provenance(context["provenance"], artifact_type=artifact_type, artifact_id=artifact_id)
        result["session_id"] = session_id
        return result

    def authoring_template_list(self, authoring_root: Optional[str] = None) -> Dict[str, Any]:
        root = self.resolve_repo_relative_path(authoring_root) if authoring_root else None
        bundles = list_world_game_template_bundles(authoring_root=root)
        return {
            "authoring_root": str(root or (self.repo_root / "examples" / "world-game-authoring")),
            "bundles": bundles,
            "count": len(bundles),
        }

    def authoring_draft_create(
        self,
        source_bundle_path: Optional[str] = None,
        source_bundle: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None,
        bundle_id: Optional[str] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        content_version: Optional[str] = None,
        deterministic_version_seed: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        if source_bundle is not None:
            source = deepcopy(source_bundle)
            resolved_source_path = None
        else:
            default_path = self.repo_root / "examples" / "world-game-authoring" / "template_bundle.multi-region.v1.json"
            resolved_source_path = (
                self.resolve_repo_relative_path(source_bundle_path) if source_bundle_path else default_path
            )
            source = resolved_source_path

        draft_bundle = create_world_game_template_bundle_draft(
            source_bundle=source,
            bundle_id=bundle_id,
            label=label,
            description=description,
            content_version=content_version,
            deterministic_version_seed=deterministic_version_seed,
            tags=tags,
            created_at=created_at,
            updated_at=updated_at,
        )
        resolved_output_path = None
        if output_path:
            resolved_output_path = self.resolve_repo_relative_path(output_path)
            self._write_json(resolved_output_path, draft_bundle)

        return {
            "source_bundle_path": str(resolved_source_path) if resolved_source_path else None,
            "output_path": str(resolved_output_path) if resolved_output_path else None,
            "bundle_metadata": deepcopy(draft_bundle.get("bundle_metadata", {})),
            "bundle": draft_bundle,
        }

    def authoring_draft_validate(
        self,
        draft_path: Optional[str] = None,
        draft_bundle: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if draft_bundle is not None:
            source = deepcopy(draft_bundle)
            resolved_draft_path = None
        else:
            if not draft_path:
                raise ValueError("draft_path or draft_bundle is required")
            resolved_draft_path = self.resolve_repo_relative_path(draft_path)
            source = resolved_draft_path
        report = validate_world_game_template_bundle_workflow(source)
        report["draft_path"] = str(resolved_draft_path) if resolved_draft_path else None
        return report

    def authoring_bundle_publish(
        self,
        draft_path: Optional[str] = None,
        draft_bundle: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None,
        published_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        if draft_bundle is not None:
            source = deepcopy(draft_bundle)
            resolved_draft_path = None
        else:
            if not draft_path:
                raise ValueError("draft_path or draft_bundle is required")
            resolved_draft_path = self.resolve_repo_relative_path(draft_path)
            source = resolved_draft_path

        published = publish_world_game_template_bundle(
            source,
            published_at=published_at,
            updated_at=updated_at,
        )
        resolved_output_path = None
        if output_path:
            resolved_output_path = self.resolve_repo_relative_path(output_path)
            self._write_json(resolved_output_path, published["bundle"])

        return {
            "draft_path": str(resolved_draft_path) if resolved_draft_path else None,
            "output_path": str(resolved_output_path) if resolved_output_path else None,
            "publication": published["publication"],
            "bundle_metadata": deepcopy(published["bundle"]["bundle_metadata"]),
            "bundle": published["bundle"],
            "validation": published["validation"],
        }

    def authoring_bundle_instantiate(
        self,
        bundle_path: Optional[str] = None,
        bundle: Optional[Dict[str, Any]] = None,
        template_id: str = "",
        parameter_values: Optional[Dict[str, Any]] = None,
        scenario_output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not template_id:
            raise ValueError("template_id is required")

        if bundle is not None:
            source = deepcopy(bundle)
            resolved_bundle_path = None
        else:
            if not bundle_path:
                raise ValueError("bundle_path or bundle is required")
            resolved_bundle_path = self.resolve_repo_relative_path(bundle_path)
            source = load_world_game_template_bundle(resolved_bundle_path)

        instantiated = instantiate_world_game_template_bundle(
            source,
            template_id=template_id,
            parameter_values=deepcopy(parameter_values or {}),
        )
        resolved_output_path = None
        if scenario_output_path:
            resolved_output_path = self.resolve_repo_relative_path(scenario_output_path)
            scenario_to_write = instantiated.get("scenario_payload", instantiated["scenario"])
            self._write_json(resolved_output_path, scenario_to_write)

        return {
            "bundle_path": str(resolved_bundle_path) if resolved_bundle_path else None,
            "scenario_output_path": str(resolved_output_path) if resolved_output_path else None,
            "instantiation_id": instantiated["instantiation_id"],
            "template_id": instantiated["template_id"],
            "scenario_id": instantiated["scenario"]["scenario_id"],
            "parameters": deepcopy(instantiated["parameters"]),
            "scenario": instantiated["scenario"],
            "bundle_metadata": deepcopy(instantiated["bundle_metadata"]),
        }

    def require_context(self, session_id: str) -> Dict[str, Any]:
        context = self.context_by_session.get(session_id)
        if context is None or "scenario" not in context:
            raise ValueError("world_game scenario not loaded for session")
        return context

    def require_branch(self, session_id: str, branch_id: str) -> Dict[str, Any]:
        context = self.require_context(session_id)
        branch = context["branches"].get(branch_id)
        if branch is None:
            raise ValueError("unknown world_game branch_id: %s" % branch_id)
        return branch

    def branch_summary(self, branch: Dict[str, Any]) -> Dict[str, Any]:
        equity = branch.get("latest_equity_report", {})
        return {
            "branch_id": branch["branch_id"],
            "parent_branch_id": branch.get("parent_branch_id"),
            "turn": branch.get("turn", 0),
            "composite_score": float(branch.get("scorecard", {}).get("composite_score", 0.0)),
            "equity_trend_vs_baseline": float(equity.get("equity_trend_vs_baseline", 0.0)),
            "disparity_spread": float(equity.get("disparity_index", {}).get("spread", 0.0)),
            "event_count": len(branch.get("event_log", [])),
        }

    def ensure_session_context(self, session_id: str) -> Dict[str, Any]:
        context = self.context_by_session.get(session_id)
        if context is None:
            context = {}
            self.context_by_session[session_id] = context
        return context

    def resolve_repo_relative_path(self, value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return self.repo_root / path

    def _resolve_scenario_path(self, scenario_id: Optional[str], scenario_path: Optional[str]) -> Path:
        if scenario_path:
            path = Path(scenario_path)
            if not path.exists():
                raise ValueError("scenario_path not found: %s" % scenario_path)
            return path

        if not scenario_id:
            raise ValueError("scenario_id or scenario_path is required")

        path = self.repo_root / "examples" / "scenarios" / scenario_id / "scenario.json"
        if not path.exists():
            raise ValueError("unknown scenario_id: %s" % scenario_id)
        return path

    def _load_policies(
        self,
        explicit_policy_pack_path: Optional[str],
        scenario_policy_ref: Optional[str],
    ) -> List[Dict[str, Any]]:
        if explicit_policy_pack_path:
            policy_path = Path(explicit_policy_pack_path)
        elif scenario_policy_ref:
            policy_path = self.repo_root / scenario_policy_ref
        else:
            policy_path = self.repo_root / "adapters" / "world_game" / "policies" / "world_game_policy_pack.json"

        if not policy_path.exists():
            policy_path = self.repo_root / "adapters" / "world_game" / "policies" / "default_policy.json"

        with policy_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, dict) and isinstance(payload.get("policies"), list):
            return deepcopy(payload["policies"])
        if isinstance(payload, dict) and isinstance(payload.get("rules"), list):
            return [deepcopy(payload)]
        raise ValueError("world game policy file must be a policy or policy pack")

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True)
            handle.write("\n")

    def _assert_capability(self, context: Dict[str, Any], actor_id: Optional[str], capability: str) -> None:
        if not actor_id:
            return
        actor = get_actor_record(context, actor_id)
        if actor is None:
            raise ValueError("unknown actor_id: %s" % actor_id)
        if capability not in actor.get("capabilities", []):
            raise ValueError("actor %s lacks required capability %s" % (actor_id, capability))

    def _append_timeline_event(
        self,
        context: Dict[str, Any],
        session_id: str,
        event_type: str,
        payload: Dict[str, Any],
        actor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        event = build_timeline_event(
            context=context,
            session_id=session_id,
            event_type=event_type,
            payload=payload,
            actor_id=actor_id,
        )
        context.setdefault("timeline", []).append(event)
        if isinstance(context.get("session_meta"), dict):
            context["session_meta"]["updated_at"] = self._now()
        return event

    def _next_id(self, context: Dict[str, Any], prefix: str) -> str:
        counter = context.setdefault("_counters", {}).get(prefix, 0) + 1
        context["_counters"][prefix] = counter
        scenario_id = context.get("scenario", {}).get("scenario_id", "session")
        return "%s.%s.%03d" % (prefix, scenario_id, counter)

    def _require_proposal(self, context: Dict[str, Any], proposal_id: str) -> Dict[str, Any]:
        proposal = context.get("proposals", {}).get(proposal_id)
        if proposal is None:
            raise ValueError("unknown proposal_id: %s" % proposal_id)
        return proposal

    def _require_annotation(self, context: Dict[str, Any], annotation_id: str) -> Dict[str, Any]:
        annotation = context.get("annotations", {}).get(annotation_id)
        if annotation is None:
            raise ValueError("unknown annotation_id: %s" % annotation_id)
        return annotation

    def _upsert_branch_provenance(
        self,
        context: Dict[str, Any],
        branch_id: str,
        source_branch_id: Optional[str],
        proposal_id: Optional[str],
        turn_result: Optional[Dict[str, Any]] = None,
    ) -> None:
        scenario_id = context.get("scenario", {}).get("scenario_id")
        upsert_provenance_record(
            context["provenance"],
            artifact_type="branch",
            artifact_id=branch_id,
            record=build_branch_provenance(
                branch_id=branch_id,
                source_branch_id=source_branch_id,
                scenario_id=scenario_id,
                proposal_id=proposal_id,
                turn_result=turn_result,
            ),
        )

    def _collaboration_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "stage": context.get("facilitation_state", {}).get("stage"),
            "actor_count": len(context.get("actors", {})),
            "proposal_count": len(context.get("proposals", {})),
            "annotation_count": len(context.get("annotations", {})),
            "timeline_count": len(context.get("timeline", [])),
            "branch_count": len(context.get("branches", {})),
            "has_scenario": bool(context.get("scenario")),
        }

    def _json_safe(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {str(key): self._json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._json_safe(item) for item in value]
        if isinstance(value, tuple):
            return [self._json_safe(item) for item in value]
        if isinstance(value, set):
            return [self._json_safe(item) for item in sorted(value, key=lambda item: repr(item))]
        return value

    def _now(self) -> str:
        return build_timeline_event(
            context={"timeline": []},
            session_id="clock",
            event_type="clock.tick",
            payload={},
            actor_id=None,
        )["timestamp"]
