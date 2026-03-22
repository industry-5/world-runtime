export function createScenarioService(runtimeClient) {
  return {
    list() {
      return runtimeClient.callRuntimeMethod("world_game.scenario.list", {});
    },
    load(sessionId, scenarioId) {
      return runtimeClient.callRuntimeMethod("world_game.scenario.load", {
        session_id: sessionId,
        scenario_id: scenarioId,
      });
    },
  };
}
