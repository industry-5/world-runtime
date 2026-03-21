export function createAnnotationService(runtimeClient) {
  return {
    create(sessionId, annotationType, targetType, targetId, body, actorId) {
      return runtimeClient.callRuntimeMethod("world_game.annotation.create", {
        session_id: sessionId,
        annotation_type: annotationType,
        target_type: targetType,
        target_id: targetId,
        body,
        actor_id: actorId,
      });
    },
    list(sessionId, targetType = null, targetId = null) {
      return runtimeClient.callRuntimeMethod("world_game.annotation.list", {
        session_id: sessionId,
        ...(targetType ? { target_type: targetType } : {}),
        ...(targetId ? { target_id: targetId } : {}),
      });
    },
  };
}
