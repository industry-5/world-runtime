export function createReplayService(runtimeClient) {
  return {
    run(sessionId, branchId) {
      return runtimeClient.callRuntimeMethod("world_game.replay.run", {
        session_id: sessionId,
        branch_id: branchId,
      });
    },
  };
}
