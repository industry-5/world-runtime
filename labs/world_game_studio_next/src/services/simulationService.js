export function createSimulationService(runtimeClient) {
  return {
    runTurn(
      sessionId,
      branchId,
      interventionIds = [],
      shockIds = [],
      approvalStatus = "approved",
      actorId = null,
      proposalId = null,
    ) {
      return runtimeClient.callRuntimeMethod("world_game.turn.run", {
        session_id: sessionId,
        branch_id: branchId,
        intervention_ids: interventionIds,
        shock_ids: shockIds,
        approval_status: approvalStatus,
        ...(actorId ? { actor_id: actorId } : {}),
        ...(proposalId ? { proposal_id: proposalId } : {}),
      });
    },
    inspectNetwork(sessionId, branchId) {
      return runtimeClient.callRuntimeMethod("world_game.network.inspect", {
        session_id: sessionId,
        branch_id: branchId,
      });
    },
    equityReport(sessionId, branchId = null, branchIds = null) {
      return runtimeClient.callRuntimeMethod("world_game.equity.report", {
        session_id: sessionId,
        ...(branchId ? { branch_id: branchId } : {}),
        ...(Array.isArray(branchIds) && branchIds.length ? { branch_ids: branchIds } : {}),
      });
    },
  };
}
