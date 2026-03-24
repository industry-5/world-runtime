from dataclasses import dataclass
from typing import Any, Dict, List, Optional


def get_nested_value(obj: Dict[str, Any], path: str):
    parts = path.split(".")
    current = obj
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


@dataclass
class PolicyResult:
    policy_name: str
    outcome: str
    message: Optional[str] = None


OUTCOME_PRIORITY = {
    "allow": 0,
    "warn": 1,
    "require_approval": 2,
    "deny": 3,
}


@dataclass
class RuleEvaluation:
    policy_id: str
    policy_name: str
    rule_id: str
    rule_name: str
    outcome: str
    matched: bool
    message: Optional[str] = None
    severity: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "policy_name": self.policy_name,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "outcome": self.outcome,
            "matched": self.matched,
            "message": self.message,
            "severity": self.severity,
            "evidence": self.evidence,
        }


@dataclass
class PolicyReport:
    proposal_id: Optional[str]
    final_outcome: str
    requires_approval: bool
    denied: bool
    evaluations: List[RuleEvaluation]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "final_outcome": self.final_outcome,
            "requires_approval": self.requires_approval,
            "denied": self.denied,
            "evaluations": [evaluation.as_dict() for evaluation in self.evaluations],
        }


class SimplePolicyEngine:
    def evaluate_rule(self, rule: dict, proposal: dict) -> Optional[PolicyResult]:
        condition = rule.get("condition", {})
        field = condition.get("field")
        operator = condition.get("operator")
        expected = condition.get("value")

        if not field or not operator:
            return None

        actual = get_nested_value(proposal, field)

        matched = False
        if operator == "equals":
            matched = actual == expected
        elif operator == ">":
            matched = actual is not None and actual > expected
        elif operator == "<":
            matched = actual is not None and actual < expected

        if not matched:
            return None

        return PolicyResult(
            policy_name=rule.get("rule_name", rule.get("rule_id", "unknown_rule")),
            outcome=rule["outcome"],
            message=rule.get("message_template"),
        )

    def evaluate_policy(self, policy: dict, proposal: dict) -> List[PolicyResult]:
        results = []
        for rule in policy.get("rules", []):
            result = self.evaluate_rule(rule, proposal)
            if result is not None:
                results.append(result)

        if not results:
            results.append(
                PolicyResult(
                    policy_name=policy["policy_name"],
                    outcome=policy["default_outcome"],
                    message=None,
                )
            )
        return results


class DeterministicPolicyEngine(SimplePolicyEngine):
    def _highest_outcome(self, outcomes: List[str]) -> str:
        if not outcomes:
            return "allow"
        return max(outcomes, key=lambda outcome: OUTCOME_PRIORITY.get(outcome, -1))

    def _validate_proposal(self, proposal: Dict[str, Any]) -> Optional[RuleEvaluation]:
        action_type = get_nested_value(proposal, "proposed_action.action_type")
        if isinstance(action_type, str) and action_type.strip():
            return None

        return RuleEvaluation(
            policy_id="policy.system.proposal-shape",
            policy_name="proposal_shape_validation",
            rule_id="rule.system.action-type-required",
            rule_name="Proposal action type is required",
            outcome="deny",
            matched=True,
            message="Proposal is missing proposed_action.action_type.",
            severity="high",
        )

    def evaluate_policy_detailed(
        self, policy: Dict[str, Any], proposal: Dict[str, Any]
    ) -> List[RuleEvaluation]:
        evaluations = []

        for rule in policy.get("rules", []):
            result = self.evaluate_rule(rule, proposal)
            if result is not None:
                evaluations.append(
                    # Rule evidence captures what field drove the matched outcome.
                    RuleEvaluation(
                        policy_id=policy.get("policy_id", "unknown_policy"),
                        policy_name=policy.get("policy_name", "unknown_policy"),
                        rule_id=rule.get("rule_id", "unknown_rule"),
                        rule_name=rule.get("rule_name", rule.get("rule_id", "unknown_rule")),
                        outcome=result.outcome,
                        matched=True,
                        message=result.message,
                        severity=rule.get("severity"),
                        evidence={
                            "field": rule.get("condition", {}).get("field"),
                            "operator": rule.get("condition", {}).get("operator"),
                            "expected": rule.get("condition", {}).get("value"),
                            "actual": get_nested_value(proposal, rule.get("condition", {}).get("field", "")),
                        },
                    )
                )

        if evaluations:
            return evaluations

        return [
            RuleEvaluation(
                policy_id=policy.get("policy_id", "unknown_policy"),
                policy_name=policy.get("policy_name", "unknown_policy"),
                rule_id="default_outcome",
                rule_name="default_outcome",
                outcome=policy.get("default_outcome", "allow"),
                matched=False,
                message=None,
                severity=None,
                evidence={"reason": "no_rules_matched"},
            )
        ]

    def _scope_matches(self, scope_values: Any, context_value: Optional[str]) -> bool:
        if not scope_values:
            return True
        if not isinstance(scope_values, list):
            return False
        if context_value is None:
            return False
        normalized = {str(item).strip() for item in scope_values if str(item).strip()}
        if "*" in normalized:
            return True
        return context_value in normalized

    def connector_policy_applies(self, policy: Dict[str, Any], connector_context: Dict[str, Any]) -> bool:
        scope = policy.get("scope")
        if not isinstance(scope, dict):
            return True

        connector_id = connector_context.get("connector_id")
        direction = connector_context.get("direction")
        provider = connector_context.get("provider")
        source = connector_context.get("source")
        action_type = connector_context.get("action_type")
        event_type = connector_context.get("event_type")

        return (
            self._scope_matches(scope.get("connector_ids"), connector_id)
            and self._scope_matches(scope.get("directions"), direction)
            and self._scope_matches(scope.get("providers"), provider)
            and self._scope_matches(scope.get("sources"), source)
            and self._scope_matches(scope.get("action_types"), action_type)
            and self._scope_matches(scope.get("event_types"), event_type)
        )

    def evaluate_connector_policies(
        self,
        policies: List[Dict[str, Any]],
        proposal: Dict[str, Any],
        connector_context: Dict[str, Any],
    ) -> PolicyReport:
        selected = [policy for policy in policies if self.connector_policy_applies(policy, connector_context)]
        if not selected:
            return PolicyReport(
                proposal_id=proposal.get("proposal_id"),
                final_outcome="allow",
                requires_approval=False,
                denied=False,
                evaluations=[
                    RuleEvaluation(
                        policy_id="policy.system.connector-default",
                        policy_name="connector_default_allow",
                        rule_id="default_outcome",
                        rule_name="default_outcome",
                        outcome="allow",
                        matched=False,
                        message="No connector policy matched scope.",
                        severity=None,
                        evidence={"connector_context": dict(connector_context)},
                    )
                ],
            )
        return self.evaluate_policies(selected, proposal)

    def evaluate_policies(
        self, policies: List[Dict[str, Any]], proposal: Dict[str, Any]
    ) -> PolicyReport:
        evaluations = []

        invalid_proposal = self._validate_proposal(proposal)
        if invalid_proposal is not None:
            evaluations.append(invalid_proposal)

        for policy in policies:
            evaluations.extend(self.evaluate_policy_detailed(policy, proposal))

        outcomes = [evaluation.outcome for evaluation in evaluations]
        final_outcome = self._highest_outcome(outcomes)

        return PolicyReport(
            proposal_id=proposal.get("proposal_id"),
            final_outcome=final_outcome,
            requires_approval=any(e.outcome == "require_approval" for e in evaluations),
            denied=final_outcome == "deny",
            evaluations=evaluations,
        )
