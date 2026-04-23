# UI Visual Design

_Last updated: 2026-03-28 (America/Chicago)_

This document is the private design-system source of truth for World Runtime labs.

Use [docs/ui-vocabulary-v1.md](./ui-vocabulary-v1.md) for the naming boundary of private UI terms, [labs/shared_ui/STAGE_AND_MEDIA_CONTRACT.md](../labs/shared_ui/STAGE_AND_MEDIA_CONTRACT.md) for the promoted generic stage/media contract, [labs/shared_ui/DOWNSTREAM_ADOPTION_GUIDE.md](../labs/shared_ui/DOWNSTREAM_ADOPTION_GUIDE.md) for mirror-versus-import rules, and [docs/controlled-vocabulary-v1.md](./controlled-vocabulary-v1.md) for core runtime truth nouns. This document defines visual defaults and layout guidance, not core runtime vocabulary.

## Intent

- keep lab UIs visually coherent without forcing a single application shell on every lab
- bias toward canvas-first composition for analysis, simulation, and comparison workflows
- keep the browser thin and runtime-authoritative
- make major layout behavior configurable through CSS custom properties and data attributes

## Shared Visual Defaults

- typography:
  - `IBM Plex Sans` for primary UI
  - `IBM Plex Mono` for ids, labels, chips, breadcrumbs, code, and control metadata
- palette:
  - grayscale-first neutrals
  - anchor accent family centered on `#6AAFB3`
  - reserve true black and true white for high-emphasis cases only
  - use semantic success/warn/error colors sparingly
- motion:
  - subtle shell, panel, focus, and selection transitions only
  - support reduced motion through tokenized timing values

## Canonical Shell Vocabulary

- `.lab-shell`
- `.lab-header`
- `.lab-left-rail`
- `.lab-stage`
- `.lab-right-rail`
- `.lab-top-tray`
- `.lab-bottom-dock`
- `.lab-panel`

Canonical state attributes:

- `data-theme="light|dark"`
- `data-density="default|analysis|presentation"`
- `data-shell-mode="default|full-bleed"`
- `data-rail-state="expanded|compact|collapsed"`
- `data-tray-state="expanded|compact|collapsed"`
- `data-visualization-kind="comparison-table|node-arc|sankey|geographic|isometric-grid|metric-card-grid|generated-media"`

## Layout Guidance

- ideal desktop composition is designed around a `1920x1080` class viewport
- side rails should feel persistent, not modal
- full-bleed canvas routes may pin the left and right rails directly to the viewport edges with no outer radius
- top trays and bottom docks should read as stage controls, not separate pages
- on full-bleed routes, trays, docks, and rails may use translucent overlay chrome so the deeper canvas remains visible behind them
- rails may become compact or collapsed later without breaking the center stage contract
- on narrower screens, preserve the stage first and stack the right rail below it before collapsing the left rail
- plain wheel over the center stage may synchronize rail scroll, but canvas zoom should use a separate gesture such as Cmd/Ctrl + wheel plus explicit HUD controls

## Shared Stage And Media Guidance

- fit authored scenes to the visible lane left after actual rails, trays, docks, and utility chrome are measured rather than relying only on raw viewport size
- prefer authored focus frames and safe zones so the browser applies framing instead of inventing layout authority
- scene catalogs and preview placeholders should label placeholder or blocked states honestly rather than implying a runtime-native surface already exists
- `data-visualization-kind` should describe display posture only and may stay broader than a consumer-local scene kind
- provenance and readiness badges or chips should remain compact advisory UI elements rather than hidden workflow authority
- shared media preview guidance should be image/audio-friendly while keeping `video` first-class but deeper player semantics downstream
- media-heavy downstreams may inherit preview, provenance, readiness, safe-zone, and focus-frame display language without moving player, editorial, or publication semantics upstream
- scene pickers, mode switches, zoom HUD placement, and pan/zoom gesture choreography remain route-owned unless later promotion evidence appears

## Dense Copy Guidance

- move long explanatory text into tooltip affordances where the default read path becomes too noisy
- prefer info icons beside headings, chips, and proposal labels instead of always-expanded paragraphs
- keep one sentence visible by default; put additional rationale into hover/focus tooltips or expandable details
- use Remix Icon for small informational, navigation, and utility affordances

## Visualization Taxonomy

Use the center stage as a polymorphic host. Current and planned kinds:

- `comparison-table`: best for side-by-side plan or policy deltas with exact values
- generated SVG comparison scenes can still count as `comparison-table` when the underlying semantic job remains exact side-by-side comparison, even if the browser is no longer rendering a literal HTML table
- `node-arc`: best for entity relationships and proposal-to-plan assembly
- `sankey`: best for directional flow, allocation, or quantity movement
- `geographic`: best for place-based movement, facilities, or regional comparison
- `isometric-grid`: best for capacity, inventory, parcel, or spatial block layouts
- `metric-card-grid`: best for quick KPI sweeps and stage summaries
- `generated-media`: best for snapshots, image evidence, or generated artifacts

## Reusable Conventions Landed In SO-P6 And SO-P7

- full-bleed shell mode is now a shared private convention for labs that need the canvas to span behind rails and control chrome
- dropdown navigation in the header should stay local in scope: upstream anchor first, then lab/route/in-route navigation
- zoom and pan affordances belong in a small stage HUD rather than in the side rails
- authored scene layout can stay server-authored when a route needs future-ready wide comparison canvases without widening runtime/public API commitments
- native per-rail scrolling should stay the baseline; JS should only intervene for center-stage synchronized rail scroll or stage-specific gestures
- if overlay chrome floats above the canvas, authored scene payloads may include safe-zone and default-focus metadata so the browser can remain render-only while avoiding collisions

## Shared UI Implementation Boundary

- `labs/shared_ui/` is the private implementation layer for the shared lab visual system
- `labs/shared_ui/BACKLOG.md` is the append-only capture point for reusable primitives discovered during real lab work
- `labs/shared_ui/ROADMAP.md`, `labs/shared_ui/STATUS.md`, and `labs/shared_ui/DOWNSTREAM_ADOPTION_GUIDE.md` now carry the detailed planning, current-state, and downstream adoption ledger for the private shared UI track
- it is not a public-runtime surface
- labs may adopt the shared tokens and primitives incrementally through mirrored or pinned-upstream use, but neither mode creates a public API or compatibility commitment
- `supply_ops_lab` is the first full adopter; `world_game_studio_next` is the current second-consumer candidate used to validate adoption guidance, but it still keeps its shell styling and dymaxion viewport controls local unless a later milestone says otherwise
