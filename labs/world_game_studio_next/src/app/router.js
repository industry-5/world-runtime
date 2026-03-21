import { STUDIO_ROUTES } from "../state/store.js";

function normalizeHash(hash) {
  if (!hash) {
    return "onboard";
  }

  const cleaned = hash.replace(/^#\/?/, "").trim();
  if (STUDIO_ROUTES.includes(cleaned)) {
    return cleaned;
  }
  return "onboard";
}

export function createHashRouter(onRouteChange) {
  function applyRouteFromHash() {
    const route = normalizeHash(window.location.hash);
    onRouteChange(route);
  }

  function start() {
    window.addEventListener("hashchange", applyRouteFromHash);
    applyRouteFromHash();
  }

  function navigate(route) {
    const next = STUDIO_ROUTES.includes(route) ? route : "onboard";
    const desiredHash = `#/${next}`;
    if (window.location.hash === desiredHash) {
      onRouteChange(next);
      return;
    }
    window.location.hash = desiredHash;
  }

  return {
    start,
    navigate,
  };
}
