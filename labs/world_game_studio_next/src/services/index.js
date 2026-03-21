import { createAnnotationService } from "./annotationService.js";
import { createAuthoringService } from "./authoringService.js";
import { createBranchService } from "./branchService.js";
import { createProposalService } from "./proposalService.js";
import { createProvenanceService } from "./provenanceService.js";
import { createReplayService } from "./replayService.js";
import { createScenarioService } from "./scenarioService.js";
import { createSessionService } from "./sessionService.js";
import { createSimulationService } from "./simulationService.js";

export function createStudioServices(runtimeClient) {
  return {
    scenario: createScenarioService(runtimeClient),
    session: createSessionService(runtimeClient),
    simulation: createSimulationService(runtimeClient),
    proposal: createProposalService(runtimeClient),
    branch: createBranchService(runtimeClient),
    replay: createReplayService(runtimeClient),
    annotation: createAnnotationService(runtimeClient),
    provenance: createProvenanceService(runtimeClient),
    authoring: createAuthoringService(runtimeClient),
  };
}
