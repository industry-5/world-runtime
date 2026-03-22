export function createAuthoringService(runtimeClient) {
  return {
    listTemplates() {
      return runtimeClient.callRuntimeMethod("world_game.authoring.template.list", {});
    },
  };
}
