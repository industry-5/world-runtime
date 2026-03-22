export function createProposalService(runtimeClient) {
  return {
    create(sessionId, payload = {}) {
      return runtimeClient.callRuntimeMethod("world_game.proposal.create", {
        session_id: sessionId,
        ...payload,
      });
    },
    list(sessionId, status = null) {
      return runtimeClient.callRuntimeMethod("world_game.proposal.list", {
        session_id: sessionId,
        ...(status ? { status } : {}),
      });
    },
    submit(sessionId, proposalId, actorId) {
      return runtimeClient.callRuntimeMethod("world_game.proposal.submit", {
        session_id: sessionId,
        proposal_id: proposalId,
        actor_id: actorId,
      });
    },
    adopt(sessionId, proposalId, actorId, branchId = null, sourceBranchId = "baseline") {
      return runtimeClient.callRuntimeMethod("world_game.proposal.adopt", {
        session_id: sessionId,
        proposal_id: proposalId,
        actor_id: actorId,
        ...(branchId ? { branch_id: branchId } : {}),
        source_branch_id: sourceBranchId,
      });
    },
    reject(sessionId, proposalId, actorId, reason = null) {
      return runtimeClient.callRuntimeMethod("world_game.proposal.reject", {
        session_id: sessionId,
        proposal_id: proposalId,
        actor_id: actorId,
        ...(reason ? { reason } : {}),
      });
    },
  };
}
