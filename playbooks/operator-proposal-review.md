# Playbook: Operator Proposal Review

## Goal

Review proposal, apply policy checks, handle approvals, and produce a decision.

## Command

```bash
make workflow-proposal
```

## Procedure

1. Load scenario proposal and adapter default policy.
2. Submit proposal through App Server task flow.
3. If approval is required, respond with an attributable actor identity:
   - include `actor_id`, `actor_type`, and operator `capabilities` (`approval.respond`, `proposal.approve`)
   - use `decision=escalated` to request escalation, or `decision=overridden` only with override capability
4. Retrieve approval history (`approval.history`) to confirm who acted and when.
5. Create decision record from policy report, approval status, and approval chain provenance.
