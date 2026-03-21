export function createProvenanceService(runtimeClient) {
  return {
    inspect(sessionId, artifactType, artifactId) {
      return runtimeClient.callRuntimeMethod("world_game.provenance.inspect", {
        session_id: sessionId,
        artifact_type: artifactType,
        artifact_id: artifactId,
      });
    },
  };
}
