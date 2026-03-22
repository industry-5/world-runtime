export const STUDIO_ROUTES = ["onboard", "plan", "simulate", "compare", "replay", "facilitate"];

export const STUDIO_STATE_DOMAINS = [
  "route",
  "experience",
  "scenario",
  "session",
  "branch",
  "selection",
  "layers",
  "canvas",
  "planning",
  "compare",
  "replay",
  "provenance",
  "facilitation",
  "accessibility",
  "notifications",
  "runtime",
];

export function createDefaultStudioState() {
  return {
    route: "onboard",
    experience: {
      densityMode: "default",
      workspaceRole: "facilitator",
    },
    scenario: {
      list: [],
      activeScenarioId: null,
      loadedScenario: null,
      loading: false,
      error: null,
    },
    session: {
      sessionId: null,
      sessionState: null,
      loading: false,
      error: null,
    },
    branch: {
      activeBranchId: null,
      branches: {},
      compareBranchIds: [],
      loading: false,
      error: null,
    },
    selection: {
      regionId: null,
      hoverRegionId: null,
      proposalRegionIds: [],
      proposalId: null,
      annotationId: null,
    },
    layers: {
      visibleLayerIds: [
        "base.boundaries",
        "base.labels",
        "interaction.selection",
        "interaction.proposal_preview",
      ],
      dominantLayerId: "state.water_security",
      manifest: {
        availableLayerIds: [],
        defaultDominantLayerId: "state.water_security",
      },
    },
    canvas: {
      viewport: {
        zoom: 1,
        x: 0,
        y: 0,
      },
    },
    planning: {
      proposalTitle: "",
      proposalActorId: "actor.facilitator",
      activeProposalId: null,
      proposals: [],
      activeInterventionId: null,
      activeShockId: null,
      lastTurnResult: null,
      networkSnapshot: null,
      annotations: [],
    },
    compare: {
      baselineBranchId: null,
      targetBranchIds: [],
      visualizationMode: "delta",
      hotspotThreshold: 0.25,
      selectedHotspotRegionId: null,
      result: null,
      loading: false,
      error: null,
    },
    replay: {
      branchId: null,
      cursorIndex: 0,
      selectedCheckpointTurn: null,
      result: null,
      frames: [],
      loading: false,
      error: null,
    },
    provenance: {
      artifactType: null,
      artifactId: null,
      contextLabel: null,
      result: null,
      loading: false,
      error: null,
    },
    facilitation: {
      queueFilter: "all",
      spotlightRegionId: null,
      presentationMode: false,
      persistenceSummary: null,
      presenterActorId: "actor.facilitator",
      followPresenter: false,
      sharedAttentionStatus: "local-only",
    },
    accessibility: {
      reducedMotion: false,
    },
    notifications: {
      items: [],
      nextId: 1,
    },
    runtime: {
      pendingRequests: 0,
      lastMethod: null,
      lastError: null,
    },
  };
}

function mergeDomain(currentDomain, patch) {
  return { ...currentDomain, ...patch };
}

export function createStudioStore(initialState = null) {
  let state = initialState || createDefaultStudioState();
  const subscribers = new Set();

  function getState() {
    return state;
  }

  function setState(nextStateOrUpdater) {
    const nextState =
      typeof nextStateOrUpdater === "function"
        ? nextStateOrUpdater(state)
        : { ...state, ...nextStateOrUpdater };
    state = nextState;
    for (const subscriber of subscribers) {
      subscriber(state);
    }
    return state;
  }

  function setRoute(route) {
    if (!STUDIO_ROUTES.includes(route)) {
      return state;
    }
    return setState((current) => ({ ...current, route }));
  }

  function patchDomain(domain, patch) {
    return setState((current) => ({
      ...current,
      [domain]: mergeDomain(current[domain], patch),
    }));
  }

  function addNotification(level, message) {
    return setState((current) => {
      const nextId = current.notifications.nextId;
      const item = {
        id: nextId,
        level,
        message,
        createdAt: new Date().toISOString(),
      };
      return {
        ...current,
        notifications: {
          nextId: nextId + 1,
          items: [item, ...current.notifications.items].slice(0, 10),
        },
      };
    });
  }

  function beginRequest(method) {
    return setState((current) => ({
      ...current,
      runtime: {
        ...current.runtime,
        pendingRequests: current.runtime.pendingRequests + 1,
        lastMethod: method,
        lastError: null,
      },
    }));
  }

  function endRequest() {
    return setState((current) => ({
      ...current,
      runtime: {
        ...current.runtime,
        pendingRequests: Math.max(0, current.runtime.pendingRequests - 1),
      },
    }));
  }

  function failRequest(error) {
    return patchDomain("runtime", {
      lastError: error?.message || String(error),
    });
  }

  function subscribe(listener) {
    subscribers.add(listener);
    return () => subscribers.delete(listener);
  }

  return {
    getState,
    setState,
    setRoute,
    patchDomain,
    addNotification,
    beginRequest,
    endRequest,
    failRequest,
    subscribe,
  };
}
