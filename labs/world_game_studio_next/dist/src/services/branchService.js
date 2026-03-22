export function createBranchService(runtimeClient) {
  return {
    create(sessionId, sourceBranchId, branchId) {
      return runtimeClient.callRuntimeMethod("world_game.branch.create", {
        session_id: sessionId,
        source_branch_id: sourceBranchId,
        branch_id: branchId,
      });
    },
    compare(sessionId, branchIds, includeAnnotationSummary = false) {
      return runtimeClient.callRuntimeMethod("world_game.branch.compare", {
        session_id: sessionId,
        branch_ids: branchIds,
        include_annotation_summary: Boolean(includeAnnotationSummary),
      });
    },
  };
}
