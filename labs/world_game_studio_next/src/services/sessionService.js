export function createSessionService(runtimeClient) {
  return {
    create(label, actorId, roles = ["facilitator"]) {
      return runtimeClient.callRuntimeMethod("world_game.session.create", {
        label,
        actor_id: actorId,
        roles,
      });
    },
    get(sessionId) {
      return runtimeClient.callRuntimeMethod("world_game.session.get", {
        session_id: sessionId,
      });
    },
    addActor(sessionId, actorId, roles = ["observer"], requestedByActorId = null, displayName = null) {
      return runtimeClient.callRuntimeMethod("world_game.session.actor.add", {
        session_id: sessionId,
        actor_id: actorId,
        roles,
        ...(requestedByActorId ? { requested_by_actor_id: requestedByActorId } : {}),
        ...(displayName ? { display_name: displayName } : {}),
      });
    },
    listActors(sessionId) {
      return runtimeClient.callRuntimeMethod("world_game.session.actor.list", {
        session_id: sessionId,
      });
    },
    advanceStage(sessionId, actorId) {
      return runtimeClient.callRuntimeMethod("world_game.session.stage.advance", {
        session_id: sessionId,
        actor_id: actorId,
      });
    },
    setStage(sessionId, stage, actorId) {
      return runtimeClient.callRuntimeMethod("world_game.session.stage.set", {
        session_id: sessionId,
        stage,
        actor_id: actorId,
      });
    },
    exportSession(sessionId, outputPath = null, actorId = null) {
      return runtimeClient.callRuntimeMethod("world_game.session.export", {
        session_id: sessionId,
        ...(outputPath ? { output_path: outputPath } : {}),
        ...(actorId ? { actor_id: actorId } : {}),
      });
    },
    importSession(sessionId, bundle = null, bundlePath = null, actorId = null) {
      return runtimeClient.callRuntimeMethod("world_game.session.import", {
        session_id: sessionId,
        ...(bundle ? { bundle } : {}),
        ...(bundlePath ? { bundle_path: bundlePath } : {}),
        ...(actorId ? { actor_id: actorId } : {}),
      });
    },
  };
}
