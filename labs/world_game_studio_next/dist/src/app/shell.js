import { STUDIO_ROUTES } from "../state/store.js";

function routeLabel(route) {
  const labels = {
    onboard: "Onboard",
    plan: "Plan",
    simulate: "Simulate",
    compare: "Compare",
    replay: "Replay",
    facilitate: "Facilitate",
  };
  return labels[route] || route;
}

export function createStudioShell(root) {
  root.innerHTML = "";

  const app = document.createElement("div");
  app.id = "studio-shell";
  app.className = "studio-shell";
  app.innerHTML = `
    <a class="skip-link" href="#shell-center-workspace">Skip to workspace</a>
    <p id="screenreader-status" class="sr-only" aria-live="polite"></p>
  `;

  const topBar = document.createElement("header");
  topBar.id = "shell-top-bar";
  topBar.className = "shell-top-bar panel";

  const leftRail = document.createElement("aside");
  leftRail.id = "shell-left-rail";
  leftRail.className = "shell-left-rail panel";

  const center = document.createElement("main");
  center.id = "shell-center-workspace";
  center.className = "shell-center-workspace panel";

  const rightRail = document.createElement("aside");
  rightRail.id = "shell-right-inspector";
  rightRail.className = "shell-right-inspector panel";

  const bottomDock = document.createElement("footer");
  bottomDock.id = "shell-bottom-dock";
  bottomDock.className = "shell-bottom-dock panel";

  const routeButtonMarkup = STUDIO_ROUTES.map(
    (route) => `<button type="button" data-route="${route}" class="route-button">${routeLabel(route)}</button>`,
  ).join("");

  topBar.innerHTML = `
    <div class="top-row">
      <div class="brand-block">
        <p class="eyebrow">World Runtime</p>
        <h1>World Game Studio Next</h1>
      </div>
      <nav class="route-nav" aria-label="Studio modes">
        ${routeButtonMarkup}
      </nav>
      <div class="runtime-pill" id="runtime-status-pill" role="status" aria-live="polite">Idle</div>
    </div>
    <div class="stage-banner" id="stage-banner" role="status" aria-live="polite">
      <p id="stage-banner-stage">Stage: setup</p>
      <p id="stage-banner-actions">Allowed actions: (none)</p>
      <p id="stage-banner-spotlight">Spotlight: none</p>
      <p id="stage-banner-attention">Attention: local-only</p>
      <p id="stage-banner-experience">Workspace: facilitator · Density: default</p>
    </div>
    <div class="top-controls">
      <div class="top-control-group">
        <label>
          Scenario
          <select id="scenario-select"></select>
        </label>
        <button id="scenario-refresh" type="button">Refresh scenarios</button>
        <button id="scenario-load" type="button">Load scenario</button>
        <button id="session-create" type="button">Create session</button>
        <button id="session-refresh" type="button">Refresh session</button>
      </div>
      <div class="top-control-group top-control-group-experience">
        <label>
          Workspace role
          <select id="workspace-role-select">
            <option value="facilitator">Facilitator</option>
            <option value="analyst">Analyst</option>
            <option value="delegate">Delegate</option>
            <option value="observer">Observer</option>
          </select>
        </label>
        <label>
          Density
          <select id="density-mode-select">
            <option value="default">Default</option>
            <option value="analysis">Analysis</option>
            <option value="presentation">Presentation</option>
          </select>
        </label>
        <label class="planning-checkbox">
          <input id="reduced-motion-toggle" type="checkbox" />
          Reduced motion
        </label>
      </div>
    </div>
  `;

  leftRail.innerHTML = `
    <section class="panel-block">
      <h2>Session Context</h2>
      <p id="session-summary">No active session.</p>
      <p id="room-state-summary" class="muted">Room state: waiting for session.</p>
    </section>
    <section class="panel-block">
      <h2>Participants</h2>
      <p id="participant-summary">No actors in session.</p>
      <ul id="participant-list" class="service-list"></ul>
    </section>
    <section class="panel-block">
      <h2>Proposal Queue</h2>
      <p id="proposal-queue-summary">No proposals.</p>
    </section>
    <section class="panel-block">
      <h2>Branch Focus</h2>
      <p id="branch-summary">No branch loaded.</p>
    </section>
    <section class="panel-block">
      <h2>Layers</h2>
      <p id="layer-summary">Layer manifest not loaded yet.</p>
    </section>
  `;

  center.innerHTML = `
    <section class="workspace-frame">
      <header>
        <p class="eyebrow">Center Workspace</p>
        <h2 id="workspace-title">Plan</h2>
      </header>
      <p id="workspace-description" class="muted">
        WG-P6 hardens onboarding, accessibility, and cutover posture while keeping runtime logic authoritative.
      </p>
      <div id="workspace-content" class="workspace-content"></div>
    </section>
  `;

  rightRail.innerHTML = `
    <section class="panel-block inspector-card inspector-core-card">
      <h2>Inspector</h2>
      <p id="inspector-route">Mode: plan</p>
      <p id="inspector-stage">Stage: setup</p>
      <p id="inspector-branch">Branch: none</p>
      <p id="inspector-selection">Selection: none</p>
    </section>
    <section class="panel-block inspector-card">
      <h2>Region Metrics</h2>
      <ul id="inspector-region-metrics" class="service-list"></ul>
    </section>
    <section class="panel-block inspector-card">
      <h2>Compare and Provenance</h2>
      <p id="inspector-compare">Compare set: none</p>
      <p id="inspector-provenance">Provenance: none</p>
    </section>
    <section class="panel-block inspector-card service-boundary-card">
      <h2>Service Boundaries</h2>
      <ul class="service-list" id="service-list"></ul>
    </section>
  `;

  bottomDock.innerHTML = `
    <section class="panel-block">
      <h2>Replay and Notifications Dock</h2>
      <p id="dock-replay">Replay: not started</p>
      <ul id="notification-list" class="notification-list"></ul>
    </section>
  `;

  app.append(topBar, leftRail, center, rightRail, bottomDock);
  root.appendChild(app);

  return {
    root: app,
    routeButtons: Array.from(topBar.querySelectorAll(".route-button")),
    runtimeStatusPill: topBar.querySelector("#runtime-status-pill"),
    reducedMotionToggle: topBar.querySelector("#reduced-motion-toggle"),
    stageBanner: topBar.querySelector("#stage-banner"),
    stageBannerStage: topBar.querySelector("#stage-banner-stage"),
    stageBannerActions: topBar.querySelector("#stage-banner-actions"),
    stageBannerSpotlight: topBar.querySelector("#stage-banner-spotlight"),
    stageBannerAttention: topBar.querySelector("#stage-banner-attention"),
    stageBannerExperience: topBar.querySelector("#stage-banner-experience"),
    scenarioSelect: topBar.querySelector("#scenario-select"),
    scenarioRefreshButton: topBar.querySelector("#scenario-refresh"),
    scenarioLoadButton: topBar.querySelector("#scenario-load"),
    sessionCreateButton: topBar.querySelector("#session-create"),
    sessionRefreshButton: topBar.querySelector("#session-refresh"),
    workspaceRoleSelect: topBar.querySelector("#workspace-role-select"),
    densityModeSelect: topBar.querySelector("#density-mode-select"),
    sessionSummary: leftRail.querySelector("#session-summary"),
    roomStateSummary: leftRail.querySelector("#room-state-summary"),
    participantSummary: leftRail.querySelector("#participant-summary"),
    participantList: leftRail.querySelector("#participant-list"),
    proposalQueueSummary: leftRail.querySelector("#proposal-queue-summary"),
    branchSummary: leftRail.querySelector("#branch-summary"),
    layerSummary: leftRail.querySelector("#layer-summary"),
    workspaceTitle: center.querySelector("#workspace-title"),
    workspaceDescription: center.querySelector("#workspace-description"),
    workspaceContent: center.querySelector("#workspace-content"),
    inspectorRoute: rightRail.querySelector("#inspector-route"),
    inspectorStage: rightRail.querySelector("#inspector-stage"),
    inspectorBranch: rightRail.querySelector("#inspector-branch"),
    inspectorSelection: rightRail.querySelector("#inspector-selection"),
    inspectorRegionMetrics: rightRail.querySelector("#inspector-region-metrics"),
    inspectorCompare: rightRail.querySelector("#inspector-compare"),
    inspectorProvenance: rightRail.querySelector("#inspector-provenance"),
    serviceList: rightRail.querySelector("#service-list"),
    dockReplay: bottomDock.querySelector("#dock-replay"),
    notificationList: bottomDock.querySelector("#notification-list"),
    screenReaderStatus: app.querySelector("#screenreader-status"),
  };
}
