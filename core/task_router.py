from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from core.observability import ObservabilityStore
from core.provider_registry import ProviderBinding, ProviderRegistry
from core.routing_policy import RoutingPolicyInput
from core.routing_trace import CandidateRoutingTrace, FallbackTrace, RoutingDecisionTrace
from core.task_profiles import TaskProfile, TaskProfileCatalog


QUALITY_ORDER = {"economy": 0, "balanced": 1, "high": 2, "premium": 3}
LATENCY_ORDER = {"batch": 0, "interactive": 1, "realtime": 2}
COST_ORDER = {"low": 0, "medium": 1, "high": 2}
DETERMINISM_ORDER = {"low": 0, "bounded": 1, "high": 2}


class TaskRouter:
    def __init__(
        self,
        provider_registry: ProviderRegistry,
        task_catalog: TaskProfileCatalog,
        observability: Optional[ObservabilityStore] = None,
    ) -> None:
        self.provider_registry = provider_registry
        self.task_catalog = task_catalog
        self.observability = observability

    def route(
        self,
        task_profile: str | TaskProfile,
        *,
        service_states: Optional[Mapping[str, Mapping[str, Any]]] = None,
        policy_input: Optional[RoutingPolicyInput] = None,
    ) -> RoutingDecisionTrace:
        profile = task_profile if isinstance(task_profile, TaskProfile) else self.task_catalog.get(task_profile)
        policy = policy_input or RoutingPolicyInput()
        trace_id = None
        if self.observability is not None:
            trace_id = self.observability.start_trace(
                name="task_router.route",
                component="task_router",
                context={
                    "task_profile_id": profile.task_profile_id,
                    "task_category": profile.task_category,
                    "policy_input": policy.as_dict(),
                },
            )

        decision = RoutingDecisionTrace(
            task_profile_id=profile.task_profile_id,
            task_category=profile.task_category,
            status="no_route",
            policy_inputs=policy.as_dict(),
        )

        eligible: list[Tuple[Tuple[Any, ...], CandidateRoutingTrace]] = []
        preferred_viable_candidates = 0

        for binding in self.provider_registry.bindings():
            candidate = self._evaluate_candidate(profile, binding, service_states=service_states, policy=policy)
            decision.candidates.append(candidate)
            if trace_id is not None and self.observability is not None:
                self.observability.trace_event(
                    trace_id,
                    "candidate.%s" % candidate.status,
                    {
                        "provider_id": binding.provider_id,
                        "stage": candidate.considered_stage,
                        "reasons": list(candidate.reasons),
                    },
                )

            if candidate.status == "rejected":
                continue

            if candidate.considered_stage == "preferred":
                preferred_viable_candidates += 1

            score_key = self._score_candidate(profile, binding, candidate, policy)
            candidate.score = {
                "preferred_provider_penalty": score_key[0],
                "stage_penalty": score_key[1],
                "preferred_capability_gap": score_key[2],
                "latency_distance": score_key[3],
                "cost_distance": score_key[4],
                "quality_distance": score_key[5],
                "provider_id": score_key[6],
            }
            eligible.append((score_key, candidate))

        if eligible:
            eligible.sort(key=lambda item: item[0])
            selected = eligible[0][1]
            selected.status = "selected"
            selected.selected = True
            selected.reasons.append("selected as the highest-ranked eligible provider")

            for _, candidate in eligible[1:]:
                candidate.reasons.append("ranked below the selected provider after deterministic sorting")

            decision.status = "selected"
            decision.selected_provider_id = selected.provider_id
            decision.selected_stage = selected.considered_stage
            decision.fallback = FallbackTrace(
                invoked=selected.considered_stage == "fallback",
                reason=(
                    "no preferred-tier providers satisfied the task profile and routing policy"
                    if selected.considered_stage == "fallback"
                    else None
                ),
                from_stage="preferred" if selected.considered_stage == "fallback" else None,
                to_stage="fallback" if selected.considered_stage == "fallback" else None,
            )
        else:
            decision.no_route_reason = "no eligible providers remained after capability, scope, health, and quality checks"
            if preferred_viable_candidates == 0 and self._fallback_possible(profile):
                decision.fallback = FallbackTrace(
                    invoked=True,
                    reason="fallback was considered but no provider satisfied the bounded fallback floor",
                    from_stage="preferred",
                    to_stage="fallback",
                )

        if trace_id is not None and self.observability is not None:
            if decision.status == "selected":
                self.observability.emit(
                    component="task_router",
                    event_type="route.selected",
                    trace_id=trace_id,
                    attributes={
                        "task_profile_id": decision.task_profile_id,
                        "selected_provider_id": decision.selected_provider_id,
                        "selected_stage": decision.selected_stage,
                        "fallback_invoked": decision.fallback.invoked,
                    },
                )
            else:
                self.observability.emit(
                    component="task_router",
                    event_type="route.no_route",
                    severity="error",
                    trace_id=trace_id,
                    attributes={
                        "task_profile_id": decision.task_profile_id,
                        "reason": decision.no_route_reason,
                        "fallback_invoked": decision.fallback.invoked,
                    },
                )
            self.observability.finish_trace(
                trace_id,
                status="passed" if decision.status == "selected" else "failed",
                extra={
                    "selected_provider_id": decision.selected_provider_id,
                    "fallback_invoked": decision.fallback.invoked,
                },
            )

        return decision

    def _evaluate_candidate(
        self,
        profile: TaskProfile,
        binding: ProviderBinding,
        *,
        service_states: Optional[Mapping[str, Mapping[str, Any]]],
        policy: RoutingPolicyInput,
    ) -> CandidateRoutingTrace:
        required_caps = set(profile.required_capability_tags)
        provider_caps = set(binding.capability_tags)
        missing_caps = sorted(required_caps - provider_caps)
        forbidden_caps = sorted(set(profile.forbidden_capability_tags) & provider_caps)

        required_scope_tags = sorted(
            set(profile.required_policy_scope_tags).union(set(policy.required_policy_scope_tags))
        )
        provider_scope = set(binding.policy_scope_tags)
        missing_scope_tags = sorted(set(required_scope_tags) - provider_scope)

        dependency_states = self._dependency_states(binding.service_dependency_ids, service_states)
        reasons: list[str] = []

        if policy.allowed_provider_ids and binding.provider_id not in policy.allowed_provider_ids:
            reasons.append("provider is outside the routing allowlist")
        if binding.provider_id in policy.denied_provider_ids:
            reasons.append("provider is explicitly denied by routing policy input")
        if policy.required_provider_kinds and binding.provider_kind not in policy.required_provider_kinds:
            reasons.append("provider kind %s is not allowed for this route" % binding.provider_kind)
        if missing_caps:
            reasons.append("missing required capability tags: %s" % ", ".join(missing_caps))
        if forbidden_caps:
            reasons.append("contains forbidden capability tags: %s" % ", ".join(forbidden_caps))
        if missing_scope_tags:
            reasons.append("missing required policy scope tags: %s" % ", ".join(missing_scope_tags))
        if profile.output_contract.structured_output_required and binding.structured_output.mode == "none":
            reasons.append("structured output is required but unsupported")

        minimum_determinism_rank = _rank(DETERMINISM_ORDER, profile.routing_preferences.minimum_determinism_tier)
        provider_determinism_rank = _rank(DETERMINISM_ORDER, binding.determinism_tier)
        if provider_determinism_rank < minimum_determinism_rank:
            reasons.append(
                "determinism tier %s is below required minimum %s"
                % (binding.determinism_tier, profile.routing_preferences.minimum_determinism_tier)
            )

        if service_states is not None:
            unavailable = [
                "%s=%s" % (service_id, state)
                for service_id, state in dependency_states.items()
                if state != "ready"
            ]
            if unavailable:
                reasons.append("service dependencies not ready: %s" % ", ".join(unavailable))

        provider_quality_rank = _rank(QUALITY_ORDER, binding.quality_tier)
        preferred_quality_rank = _rank(QUALITY_ORDER, profile.routing_preferences.preferred_quality_tier)
        minimum_quality_rank = _rank(QUALITY_ORDER, profile.routing_preferences.minimum_quality_tier)

        considered_stage = "preferred"
        if provider_quality_rank < minimum_quality_rank:
            reasons.append(
                "quality tier %s is below minimum floor %s"
                % (binding.quality_tier, profile.routing_preferences.minimum_quality_tier)
            )
        elif provider_quality_rank < preferred_quality_rank:
            considered_stage = "fallback"

        if considered_stage == "fallback" and not self._fallback_allowed(profile, preferred_quality_rank, provider_quality_rank):
            reasons.append("bounded fallback policy does not allow this quality downgrade")

        return CandidateRoutingTrace(
            provider_id=binding.provider_id,
            provider_kind=binding.provider_kind,
            status="rejected" if reasons else "eligible",
            considered_stage=considered_stage,
            reasons=reasons,
            matched_capability_tags=sorted(required_caps & provider_caps),
            missing_capability_tags=missing_caps,
            matched_policy_scope_tags=sorted(set(required_scope_tags) & provider_scope),
            missing_policy_scope_tags=missing_scope_tags,
            service_dependency_states=dependency_states,
        )

    def _dependency_states(
        self,
        dependency_ids: Iterable[str],
        service_states: Optional[Mapping[str, Mapping[str, Any]]],
    ) -> Dict[str, str]:
        if not dependency_ids:
            return {}
        if service_states is None:
            return {service_id: "unknown" for service_id in sorted(set(dependency_ids))}

        states: Dict[str, str] = {}
        for service_id in sorted(set(dependency_ids)):
            snapshot = dict(service_states.get(service_id, {}))
            states[service_id] = str(snapshot.get("lifecycle_state", "missing"))
        return states

    def _score_candidate(
        self,
        profile: TaskProfile,
        binding: ProviderBinding,
        candidate: CandidateRoutingTrace,
        policy: RoutingPolicyInput,
    ) -> Tuple[Any, ...]:
        preferred_capability_gap = len(set(profile.preferred_capability_tags) - set(binding.capability_tags))
        preferred_provider_penalty = 0 if binding.provider_id in policy.preferred_provider_ids else 1
        stage_penalty = 0 if candidate.considered_stage == "preferred" else 1
        latency_distance = abs(
            _rank(LATENCY_ORDER, binding.latency_tier) - _rank(LATENCY_ORDER, profile.routing_preferences.preferred_latency_tier)
        )
        cost_distance = abs(
            _rank(COST_ORDER, binding.cost_tier) - _rank(COST_ORDER, profile.routing_preferences.preferred_cost_tier)
        )
        quality_distance = abs(
            _rank(QUALITY_ORDER, binding.quality_tier) - _rank(QUALITY_ORDER, profile.routing_preferences.preferred_quality_tier)
        )
        return (
            preferred_provider_penalty,
            stage_penalty,
            preferred_capability_gap,
            latency_distance,
            cost_distance,
            quality_distance,
            binding.provider_id,
        )

    def _fallback_possible(self, profile: TaskProfile) -> bool:
        preferred = _rank(QUALITY_ORDER, profile.routing_preferences.preferred_quality_tier)
        minimum = _rank(QUALITY_ORDER, profile.routing_preferences.minimum_quality_tier)
        return minimum < preferred and profile.fallback_policy.mode != "none"

    def _fallback_allowed(self, profile: TaskProfile, preferred_quality_rank: int, provider_quality_rank: int) -> bool:
        if provider_quality_rank >= preferred_quality_rank:
            return True
        if profile.fallback_policy.mode == "none":
            return False
        downgrade = preferred_quality_rank - provider_quality_rank
        return downgrade <= max(profile.fallback_policy.max_quality_tier_downgrade, 0)


def _rank(order: Mapping[str, int], value: str) -> int:
    return order.get(value, -1)
