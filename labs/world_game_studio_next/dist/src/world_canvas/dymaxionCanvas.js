function createSvgElement(name, attributes = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attributes)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

function pointsToPath(points) {
  if (!Array.isArray(points) || points.length < 2) {
    return "";
  }
  return points
    .map((point, index) => {
      const prefix = index === 0 ? "M" : "L";
      return `${prefix}${point[0]},${point[1]}`;
    })
    .join(" ")
    .concat(" Z");
}

function polylinePath(points) {
  if (!Array.isArray(points) || points.length < 2) {
    return "";
  }
  return points
    .map((point, index) => {
      const prefix = index === 0 ? "M" : "L";
      return `${prefix}${point[0]},${point[1]}`;
    })
    .join(" ");
}

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function sequentialValueColor(value, minimum, maximum) {
  if (!Number.isFinite(value) || !Number.isFinite(minimum) || !Number.isFinite(maximum)) {
    return "rgb(40, 67, 89)";
  }
  if (Math.abs(maximum - minimum) < 1e-9) {
    return "rgb(97, 176, 130)";
  }
  const t = clamp((value - minimum) / (maximum - minimum), 0, 1);
  const start = { r: 38, g: 72, b: 104 };
  const end = { r: 129, g: 229, b: 170 };
  const r = Math.round(start.r + (end.r - start.r) * t);
  const g = Math.round(start.g + (end.g - start.g) * t);
  const b = Math.round(start.b + (end.b - start.b) * t);
  return `rgb(${r}, ${g}, ${b})`;
}

function divergingValueColor(value, minimum, maximum) {
  if (!Number.isFinite(value) || !Number.isFinite(minimum) || !Number.isFinite(maximum)) {
    return "rgb(40, 67, 89)";
  }
  const negativeBound = Math.min(0, minimum);
  const positiveBound = Math.max(0, maximum);
  if (Math.abs(positiveBound - negativeBound) < 1e-9) {
    return "rgb(40, 67, 89)";
  }

  if (value <= 0) {
    const t = clamp((value - negativeBound) / (0 - negativeBound || 1), 0, 1);
    const start = { r: 172, g: 72, b: 72 };
    const end = { r: 232, g: 220, b: 205 };
    const r = Math.round(start.r + (end.r - start.r) * t);
    const g = Math.round(start.g + (end.g - start.g) * t);
    const b = Math.round(start.b + (end.b - start.b) * t);
    return `rgb(${r}, ${g}, ${b})`;
  }

  const t = clamp((value - 0) / (positiveBound || 1), 0, 1);
  const start = { r: 232, g: 220, b: 205 };
  const end = { r: 80, g: 166, b: 124 };
  const r = Math.round(start.r + (end.r - start.r) * t);
  const g = Math.round(start.g + (end.g - start.g) * t);
  const b = Math.round(start.b + (end.b - start.b) * t);
  return `rgb(${r}, ${g}, ${b})`;
}

function valueColor(value, minimum, maximum, colorMode = "sequential") {
  if (colorMode === "diverging") {
    return divergingValueColor(value, minimum, maximum);
  }
  return sequentialValueColor(value, minimum, maximum);
}

function polygonBounds(polygons) {
  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;

  for (const polygon of polygons) {
    for (const point of polygon || []) {
      const [x, y] = point;
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
    }
  }

  if (!Number.isFinite(minX) || !Number.isFinite(minY) || !Number.isFinite(maxX) || !Number.isFinite(maxY)) {
    return null;
  }
  return { minX, minY, maxX, maxY };
}

export function createDymaxionCanvas(container, callbacks = {}) {
  const root = document.createElement("section");
  root.className = "dymaxion-canvas";
  root.innerHTML = `
    <header class="dymaxion-toolbar">
      <div class="dymaxion-toolbar-group">
        <button type="button" data-canvas-action="zoom-out" aria-label="Zoom out" title="Zoom out">-</button>
        <button type="button" data-canvas-action="zoom-in" aria-label="Zoom in" title="Zoom in">+</button>
        <button type="button" data-canvas-action="fit" aria-label="Fit selected regions" title="Fit to selected scope">Fit</button>
        <button type="button" data-canvas-action="reset" aria-label="Reset viewport" title="Reset view">Reset</button>
      </div>
      <p class="dymaxion-status" id="dymaxion-status" aria-live="polite">Canvas awaiting scenario data.</p>
    </header>
    <div class="dymaxion-svg-wrap">
      <svg class="dymaxion-svg" id="dymaxion-svg" role="img" aria-label="Dymaxion planning canvas" tabindex="0"></svg>
    </div>
  `;
  container.appendChild(root);

  const svg = root.querySelector("#dymaxion-svg");
  const status = root.querySelector("#dymaxion-status");

  let model = null;
  let viewport = { zoom: 1, x: 0, y: 0 };
  let dragState = null;

  function currentMeta() {
    return model?.geometry?.projectionMeta?.viewport || {
      width: 1000,
      height: 620,
      min_zoom: 1,
      max_zoom: 4,
      default: { zoom: 1, x: 0, y: 0 },
    };
  }

  function normalizeViewport(nextViewport) {
    const meta = currentMeta();
    const zoom = clamp(Number(nextViewport.zoom) || 1, meta.min_zoom || 1, meta.max_zoom || 4);
    const panLimitX = Math.max(0, (meta.width - meta.width / zoom) / 2);
    const panLimitY = Math.max(0, (meta.height - meta.height / zoom) / 2);
    return {
      zoom,
      x: clamp(Number(nextViewport.x) || 0, -panLimitX, panLimitX),
      y: clamp(Number(nextViewport.y) || 0, -panLimitY, panLimitY),
    };
  }

  function applyViewBox() {
    const meta = currentMeta();
    const normalized = normalizeViewport(viewport);
    viewport = normalized;
    const visibleWidth = meta.width / normalized.zoom;
    const visibleHeight = meta.height / normalized.zoom;
    const minX = (meta.width - visibleWidth) / 2 + normalized.x;
    const minY = (meta.height - visibleHeight) / 2 + normalized.y;
    svg.setAttribute("viewBox", `${minX} ${minY} ${visibleWidth} ${visibleHeight}`);
  }

  function pushViewportUpdate() {
    if (typeof callbacks.onViewportChange === "function") {
      callbacks.onViewportChange({ ...viewport });
    }
  }

  function setViewport(nextViewport, emit = false) {
    viewport = normalizeViewport(nextViewport);
    applyViewBox();
    if (emit) {
      pushViewportUpdate();
    }
  }

  function fitToScope(scopeRegionIds) {
    if (!model) {
      return;
    }
    const regions = model.geometry.regions || [];
    const scoped = scopeRegionIds?.length
      ? regions.filter((region) => scopeRegionIds.includes(region.region_id))
      : regions;
    const polygons = scoped.map((region) => region.polygon).filter(Boolean);
    const bounds = polygonBounds(polygons);
    if (!bounds) {
      return;
    }
    const meta = currentMeta();
    const width = bounds.maxX - bounds.minX;
    const height = bounds.maxY - bounds.minY;
    if (width <= 0 || height <= 0) {
      return;
    }
    const margin = 36;
    const targetZoom = clamp(
      Math.min(meta.width / (width + margin), meta.height / (height + margin)),
      meta.min_zoom || 1,
      meta.max_zoom || 4,
    );
    const centerX = (bounds.minX + bounds.maxX) / 2;
    const centerY = (bounds.minY + bounds.maxY) / 2;
    setViewport(
      {
        zoom: targetZoom,
        x: centerX - meta.width / 2,
        y: centerY - meta.height / 2,
      },
      true,
    );
  }

  function render(nextModel) {
    model = nextModel;
    root.classList.toggle("is-presentation", Boolean(nextModel.presentationMode));
    const meta = currentMeta();
    svg.setAttribute("width", String(meta.width));
    svg.setAttribute("height", String(meta.height));

    if (nextModel.viewport) {
      viewport = normalizeViewport(nextModel.viewport);
    }
    applyViewBox();

    svg.innerHTML = "";

    const stage = createSvgElement("g", { class: "dymaxion-stage" });
    svg.appendChild(stage);

    const backdrop = createSvgElement("rect", {
      x: 0,
      y: 0,
      width: meta.width,
      height: meta.height,
      class: "dymaxion-backdrop",
    });
    stage.appendChild(backdrop);

    const facesGroup = createSvgElement("g", { class: "dymaxion-faces" });
    stage.appendChild(facesGroup);
    for (const face of model.geometry.faces || []) {
      const path = createSvgElement("path", {
        d: pointsToPath(face.polygon),
        class: "dymaxion-face",
      });
      facesGroup.appendChild(path);
    }

    const landGroup = createSvgElement("g", { class: "dymaxion-land" });
    stage.appendChild(landGroup);
    for (const polygon of model.geometry.landPolygons || []) {
      const path = createSvgElement("path", {
        d: pointsToPath(polygon),
        class: "dymaxion-land-shape",
      });
      landGroup.appendChild(path);
    }

    const dominantGroup = createSvgElement("g", { class: "dymaxion-dominant" });
    const overlayGroup = createSvgElement("g", { class: "dymaxion-overlays" });
    const boundaryGroup = createSvgElement("g", { class: "dymaxion-boundaries" });
    const labelGroup = createSvgElement("g", { class: "dymaxion-labels" });
    const badgeGroup = createSvgElement("g", { class: "dymaxion-badges" });
    const flowGroup = createSvgElement("g", { class: "dymaxion-flows" });
    stage.append(dominantGroup, flowGroup, overlayGroup, boundaryGroup, labelGroup, badgeGroup);

    const showFlows = model.visibleLayerIds.includes("flow.resource");
    const showBoundaries = model.visibleLayerIds.includes("base.boundaries");
    const showLabels = model.visibleLayerIds.includes("base.labels");
    const showSelection = model.visibleLayerIds.includes("interaction.selection");
    const showProposal = model.visibleLayerIds.includes("interaction.proposal_preview");
    const showBadges = model.visibleLayerIds.includes("evidence.annotation_badges");
    const showCompareHighlights = model.route === "compare" || model.visibleLayerIds.includes("analysis.compare_highlights");
    const showReplayCheckpoints =
      model.route === "replay" || model.visibleLayerIds.includes("analysis.replay_checkpoints");
    const showSpotlight = Boolean(model.spotlightRegionId);
    const minimum = model.dominantScale.min;
    const maximum = model.dominantScale.max;
    const compareOverlay = model.compareOverlay || null;
    const replayOverlay = model.replayOverlay || null;

    if (showFlows) {
      for (const line of model.flowLines || []) {
        const width = Math.max(1.5, 1.2 + Number(line.transfer || 0) * 0.18);
        const path = createSvgElement("path", {
          d: polylinePath(line.path),
          class: "dymaxion-flow-line",
          "stroke-width": width.toFixed(2),
        });
        flowGroup.appendChild(path);
      }
    }

    for (const region of model.geometry.regions || []) {
      const regionId = region.region_id;
      const dominantValue = model.dominantValues[regionId];
      const fillPath = createSvgElement("path", {
        d: pointsToPath(region.polygon),
        class: "dymaxion-region-fill",
        "data-region-id": regionId,
        fill: valueColor(dominantValue, minimum, maximum, model.dominantColorMode),
      });
      dominantGroup.appendChild(fillPath);

      if (showProposal && model.proposalRegionIds.includes(regionId)) {
        const proposal = createSvgElement("path", {
          d: pointsToPath(region.polygon),
          class: "dymaxion-proposal-region",
          "data-region-id": regionId,
        });
        overlayGroup.appendChild(proposal);
      }

      if (showSelection && model.selectedRegionId === regionId) {
        const selected = createSvgElement("path", {
          d: pointsToPath(region.polygon),
          class: "dymaxion-selected-region",
          "data-region-id": regionId,
        });
        overlayGroup.appendChild(selected);
      }

      if (showSelection && model.hoveredRegionId === regionId) {
        const hovered = createSvgElement("path", {
          d: pointsToPath(region.polygon),
          class: "dymaxion-hovered-region",
          "data-region-id": regionId,
        });
        overlayGroup.appendChild(hovered);
      }

      if (showSpotlight && model.spotlightRegionId === regionId) {
        const spotlight = createSvgElement("path", {
          d: pointsToPath(region.polygon),
          class: "dymaxion-spotlight-region",
          "data-region-id": regionId,
        });
        overlayGroup.appendChild(spotlight);
      }

      if (showBoundaries) {
        const boundary = createSvgElement("path", {
          d: pointsToPath(region.polygon),
          class: "dymaxion-region-boundary",
          "data-region-id": regionId,
          tabindex: "0",
          role: "button",
          "aria-label": `Select region ${region.label || regionId}`,
        });

        boundary.addEventListener("mouseenter", () => {
          if (typeof callbacks.onRegionHover === "function") {
            callbacks.onRegionHover(regionId);
          }
        });
        boundary.addEventListener("mouseleave", () => {
          if (typeof callbacks.onRegionHover === "function") {
            callbacks.onRegionHover(null);
          }
        });
        boundary.addEventListener("click", (event) => {
          if (typeof callbacks.onRegionSelect === "function") {
            callbacks.onRegionSelect(regionId, {
              append: Boolean(event.shiftKey || event.metaKey || event.ctrlKey),
            });
          }
        });
        boundary.addEventListener("keydown", (event) => {
          if (event.key !== "Enter" && event.key !== " ") {
            return;
          }
          event.preventDefault();
          if (typeof callbacks.onRegionSelect === "function") {
            callbacks.onRegionSelect(regionId, { append: false });
          }
        });
        boundaryGroup.appendChild(boundary);
      }

      if (showBadges) {
        const count = Number(model.annotationCounts[regionId] || 0);
        if (count > 0) {
          const label = (model.geometry.labels || []).find((item) => item.region_id === regionId);
          if (label?.anchor) {
            const [x, y] = label.anchor;
            const circle = createSvgElement("circle", {
              cx: x + 12,
              cy: y - 14,
              r: 9,
              class: "dymaxion-annotation-badge",
            });
            const text = createSvgElement("text", {
              x: x + 12,
              y: y - 10.5,
              class: "dymaxion-annotation-badge-text",
              "text-anchor": "middle",
            });
            text.textContent = String(count);
            badgeGroup.append(circle, text);
          }
        }
      }

      if (showCompareHighlights && compareOverlay) {
        if (compareOverlay.topDeltaRegionIds?.includes(regionId)) {
          const comparePath = createSvgElement("path", {
            d: pointsToPath(region.polygon),
            class: "dymaxion-compare-region",
            "data-region-id": regionId,
          });
          overlayGroup.appendChild(comparePath);
        }
        if (compareOverlay.selectedHotspotRegionId === regionId) {
          const hotspotPath = createSvgElement("path", {
            d: pointsToPath(region.polygon),
            class: "dymaxion-compare-hotspot-region",
            "data-region-id": regionId,
          });
          overlayGroup.appendChild(hotspotPath);
        }
        if (compareOverlay.mode === "ghost" && compareOverlay.ghostRegionIds?.includes(regionId)) {
          const ghostPath = createSvgElement("path", {
            d: pointsToPath(region.polygon),
            class: "dymaxion-ghost-region",
            "data-region-id": regionId,
          });
          overlayGroup.appendChild(ghostPath);
        }
      }

      if (showReplayCheckpoints && replayOverlay?.checkpointRegionIds?.includes(regionId)) {
        const checkpointPath = createSvgElement("path", {
          d: pointsToPath(region.polygon),
          class: "dymaxion-replay-checkpoint-region",
          "data-region-id": regionId,
        });
        overlayGroup.appendChild(checkpointPath);
      }
    }

    if (showLabels) {
      for (const label of model.geometry.labels || []) {
        if (!label.anchor) {
          continue;
        }
        const text = createSvgElement("text", {
          x: label.anchor[0],
          y: label.anchor[1],
          class: "dymaxion-region-label",
          "text-anchor": "middle",
        });
        text.textContent = label.label || label.region_id;
        labelGroup.appendChild(text);
      }
    }

    if (compareOverlay?.mode === "split") {
      const splitLine = createSvgElement("line", {
        x1: meta.width / 2,
        x2: meta.width / 2,
        y1: 0,
        y2: meta.height,
        class: "dymaxion-compare-split-line",
      });
      stage.appendChild(splitLine);
    }

    if (replayOverlay) {
      const activeCheckpoint = replayOverlay.selectedCheckpoint;
      status.textContent =
        `Replay ${replayOverlay.branchId || "branch"} turn ${
          replayOverlay.frame?.turn_index ?? replayOverlay.cursorIndex ?? 0
        } / ${Math.max(0, (replayOverlay.frameCount || 1) - 1)}` +
        (activeCheckpoint ? ` | checkpoint ${activeCheckpoint.turnIndex}` : "");
    } else if (compareOverlay) {
      status.textContent =
        `Compare ${compareOverlay.baselineBranchId} vs ${compareOverlay.targetBranchId} (${compareOverlay.mode})` +
        (compareOverlay.selectedHotspotRegionId ? ` | hotspot ${compareOverlay.selectedHotspotRegionId}` : "");
    } else {
      status.textContent = model.selectedRegionId
        ? `Selected ${model.selectedRegionId} | Dominant layer: ${model.dominantLayerId}`
        : `Dominant layer: ${model.dominantLayerId || "state.water_security"}`;
      if (model.spotlightRegionId) {
        status.textContent = `${status.textContent} | Spotlight ${model.spotlightRegionId}`;
      }
    }
  }

  root.addEventListener("click", (event) => {
    const button = event.target.closest("[data-canvas-action]");
    if (!button) {
      return;
    }
    const action = button.getAttribute("data-canvas-action");
    if (action === "zoom-in") {
      setViewport({ ...viewport, zoom: viewport.zoom * 1.15 }, true);
    } else if (action === "zoom-out") {
      setViewport({ ...viewport, zoom: viewport.zoom / 1.15 }, true);
    } else if (action === "fit") {
      const scopedRegionIds = model?.proposalRegionIds?.length
        ? model.proposalRegionIds
        : model?.selectedRegionId
          ? [model.selectedRegionId]
          : [];
      fitToScope(scopedRegionIds);
    } else if (action === "reset") {
      const defaults = currentMeta().default || { zoom: 1, x: 0, y: 0 };
      setViewport(defaults, true);
    }
  });

  svg.addEventListener("keydown", (event) => {
    if (event.key === "+" || event.key === "=") {
      event.preventDefault();
      setViewport({ ...viewport, zoom: viewport.zoom * 1.15 }, true);
      return;
    }
    if (event.key === "-" || event.key === "_") {
      event.preventDefault();
      setViewport({ ...viewport, zoom: viewport.zoom / 1.15 }, true);
      return;
    }
    if (event.key === "0") {
      event.preventDefault();
      const defaults = currentMeta().default || { zoom: 1, x: 0, y: 0 };
      setViewport(defaults, true);
      return;
    }
    if (event.key.toLowerCase() === "f") {
      event.preventDefault();
      const scopedRegionIds = model?.proposalRegionIds?.length
        ? model.proposalRegionIds
        : model?.selectedRegionId
          ? [model.selectedRegionId]
          : [];
      fitToScope(scopedRegionIds);
    }
  });

  svg.addEventListener("pointerdown", (event) => {
    const target = event.target;
    if (target?.classList?.contains("dymaxion-region-boundary")) {
      return;
    }
    dragState = {
      startX: event.clientX,
      startY: event.clientY,
      origin: { ...viewport },
      moved: false,
    };
    if (typeof svg.setPointerCapture === "function") {
      svg.setPointerCapture(event.pointerId);
    }
  });

  svg.addEventListener("pointermove", (event) => {
    if (!dragState) {
      return;
    }
    const dx = (event.clientX - dragState.startX) / viewport.zoom;
    const dy = (event.clientY - dragState.startY) / viewport.zoom;
    dragState.moved = true;
    setViewport(
      {
        ...dragState.origin,
        x: dragState.origin.x - dx,
        y: dragState.origin.y - dy,
      },
      false,
    );
  });

  svg.addEventListener("pointerup", (event) => {
    if (dragState) {
      if (typeof svg.releasePointerCapture === "function") {
        svg.releasePointerCapture(event.pointerId);
      }
      if (dragState.moved) {
        pushViewportUpdate();
      }
      dragState = null;
    }
  });
  svg.addEventListener("pointercancel", () => {
    dragState = null;
  });

  return {
    render,
  };
}
