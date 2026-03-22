const GEOMETRY_FILE_MAP = {
  faces: "dymaxion_faces.json",
  land: "dymaxion_land.json",
  regions: "dymaxion_regions.json",
  labels: "dymaxion_region_labels.json",
  flowAnchors: "dymaxion_flow_anchors.json",
  projectionMeta: "dymaxion_projection_meta.json",
};

let geometryCache = null;

async function fetchJson(url) {
  const response = await fetch(url, { method: "GET" });
  if (!response.ok) {
    throw new Error(`Failed to load geometry file: ${url} (${response.status})`);
  }
  return response.json();
}

function withDefaults(payload) {
  const projectionMeta = payload.projectionMeta || {};
  const viewport = projectionMeta.viewport || {};
  return {
    ...payload,
    projectionMeta: {
      ...projectionMeta,
      viewport: {
        width: viewport.width || 1000,
        height: viewport.height || 620,
        default: {
          zoom: viewport.default?.zoom || 1,
          x: viewport.default?.x || 0,
          y: viewport.default?.y || 0,
        },
        min_zoom: viewport.min_zoom || 1,
        max_zoom: viewport.max_zoom || 4,
      },
    },
  };
}

export async function loadGeometryPackage(basePath = "/assets/world_game_map/v1") {
  if (geometryCache) {
    return geometryCache;
  }

  const entries = await Promise.all(
    Object.entries(GEOMETRY_FILE_MAP).map(async ([key, fileName]) => {
      const payload = await fetchJson(`${basePath}/${fileName}`);
      return [key, payload];
    }),
  );

  const next = withDefaults(Object.fromEntries(entries));
  if (!Array.isArray(next.regions?.regions) || next.regions.regions.length === 0) {
    throw new Error("Geometry package missing regions");
  }
  geometryCache = next;
  return geometryCache;
}
