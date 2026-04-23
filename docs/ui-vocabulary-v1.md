# UI Vocabulary v1

_Last updated: 2026-03-28 (America/Chicago)_

This document defines the private shared UI glossary for World Runtime labs and downstream adopters.

Its purpose is to keep one stable language for:

- shared shell and layout parts
- stage and scene framing
- generic visualization and media-display states
- the boundary between upstream private UI contracts, downstream adoption modes, and downstream domain-specific UI semantics

Use this page together with:

- [docs/controlled-vocabulary-v1.md](./controlled-vocabulary-v1.md) for core runtime truth nouns
- [docs/ui-visual-design.md](./ui-visual-design.md) for visual defaults and layout guidance
- [labs/shared_ui/STAGE_AND_MEDIA_CONTRACT.md](../labs/shared_ui/STAGE_AND_MEDIA_CONTRACT.md) for the promoted generic stage and media-display contract
- [labs/shared_ui/CROSS_REPO_ALIGNMENT.md](../labs/shared_ui/CROSS_REPO_ALIGNMENT.md) for the upstream/downstream ownership split
- [labs/shared_ui/DOWNSTREAM_ADOPTION_GUIDE.md](../labs/shared_ui/DOWNSTREAM_ADOPTION_GUIDE.md) for mirror-versus-import decisions and second-consumer readiness guidance

This document is private UI guidance only. It does not rename schemas, APIs, protocol methods, or public runtime contracts.

## Vocabulary Method

- glossary: the front door for shared private UI terms
- taxonomy: the organizing frame by UI layer and display role
- ontology: deferred; this track does not define a machine-formal UI ontology

## Taxonomy By UI Layer

| UI layer | Role | Representative terms |
| --- | --- | --- |
| shared shell structure | reusable browser layout and shell state | lab shell, header, rail, tray, dock, panel, stage |
| stage and scene framing | render-only stage composition and camera/viewport vocabulary | scene catalog, active scene, safe zone, focus frame, placeholder scene |
| visualization and media display | generic display mode and preview language | visualization kind, media type, media preview |
| cross-cutting state labels | generic display-state contracts that downstream UIs may inherit | asset source state, provenance state, readiness state |
| promotion and ownership language | terms for deciding what becomes shared versus what stays local | route-owned pattern, shared pattern, promotion candidate, mirrored adoption, pinned-upstream import |

## Term Registry

### Shared Shell Structure

#### Lab Shell

- Display label: `Lab Shell`
- Machine label / class anchor: `.lab-shell`
- Concise definition: the shared browser shell that arranges header, rails, stage, trays, docks, and panels for a lab or downstream-adopted surface
- Boundary statement: this is a private UI layout term, not a runtime state family or public contract

#### Stage

- Display label: `Stage`
- Machine label / class anchor: `.lab-stage`
- Concise definition: the center render host for visual analysis, scene playback, comparison, or media display
- Boundary statement: the stage is a render surface only; it does not own authoritative runtime logic

#### Rail

- Display label: `Rail`
- Machine label / class anchor: `.lab-left-rail`, `.lab-right-rail`
- Concise definition: a persistent edge column for navigation, context, controls, or detail panes
- Boundary statement: rail terms describe shell composition, not domain workflow stages

#### Tray

- Display label: `Tray`
- Machine label / class anchor: `.lab-top-tray`
- Concise definition: a top-edge control region associated with the current stage or route
- Boundary statement: trays are stage-control chrome, not separate pages

#### Dock

- Display label: `Dock`
- Machine label / class anchor: `.lab-bottom-dock`
- Concise definition: a bottom-edge strip for secondary controls, summaries, or supporting context
- Boundary statement: docks remain shell vocabulary even when a route uses them for domain-specific actions

#### Panel

- Display label: `Panel`
- Machine label / class anchor: `.lab-panel`
- Concise definition: a bounded shell container for grouped UI content inside rails, trays, docks, or stage-adjacent regions
- Boundary statement: panel is a generic UI container term and does not imply a domain record family

### Stage And Scene Framing

#### Scene Catalog

- Display label: `Scene Catalog`
- Machine label: `scene_catalog`
- Concise definition: the authored list of scenes available for the current stage host
- Boundary statement: scene catalogs are private UI composition data, not public runtime APIs unless a later milestone explicitly promotes them

#### Active Scene

- Display label: `Active Scene`
- Machine label: `active_scene`
- Concise definition: the currently selected scene inside a scene catalog
- Boundary statement: active-scene state is a private UI selection concept, not authoritative domain truth

#### Safe Zone

- Display label: `Safe Zone`
- Machine label: `safe_zone`
- Concise definition: the authored region a scene should preserve from overlay collisions with shell chrome
- Boundary statement: safe zones guide render-only placement and do not define domain geometry semantics

#### Focus Frame

- Display label: `Focus Frame`
- Machine label: `focus_frame`
- Concise definition: the authored default camera or viewport region that should anchor the user's first look at a scene
- Boundary statement: focus frames are UI framing metadata, not runtime authority

#### Viewport

- Display label: `Viewport`
- Machine label: `viewport`
- Concise definition: the visible window and camera-hint surface used to fit authored scene extents or focus frames inside the stage host
- Boundary statement: viewport hints guide render-only framing and do not move runtime authority into the browser

#### Placeholder Scene

- Display label: `Placeholder Scene`
- Machine label: `placeholder_scene`
- Concise definition: a scene intentionally present to reserve navigation, layout, or state vocabulary before a fully authored scene exists
- Boundary statement: placeholder scenes are honest UI planning surfaces and must not be described as already-native runtime views

### Visualization And Media Display

#### Visualization Kind

- Display label: `Visualization Kind`
- Machine label: `data-visualization-kind`
- Concise definition: the generic display category for the current stage, such as `comparison-table`, `node-arc`, `sankey`, `geographic`, `isometric-grid`, `metric-card-grid`, or `generated-media`
- Boundary statement: visualization kinds describe display posture only and do not define domain semantics

#### Media Type

- Display label: `Media Type`
- Machine label: `media_type`
- Concise definition: the generic type of media a downstream UI is presenting or requesting, currently `image`, `audio`, or `video`
- Boundary statement: this shared label does not imply MIME, codec, container, or downstream workflow parity

#### Media Preview

- Display label: `Media Preview`
- Machine label: `media_preview`
- Concise definition: a render-only preview of a media asset or asset placeholder inside a stage or panel
- Boundary statement: media preview is a generic display term and does not make the asset authoritative

#### Preview Placeholder

- Display label: `Preview Placeholder`
- Machine label: `preview_placeholder`
- Concise definition: an honest placeholder frame used when a scene or media preview is intentionally reserved, loading, blocked, or missing
- Boundary statement: a preview placeholder communicates absence or deferment and must not be presented as a ready authoritative asset

### Cross-Cutting State Labels

#### Asset Source State

- Display label: `Asset Source State`
- Machine label: private shared contract family
- Concise definition: the display-origin label for the resolved asset a UI is showing, such as `generated`, `active_line_asset`, `primary_reference`, or `missing`
- Boundary statement: upstream standardizes only the display-origin vocabulary; downstream domains still own the semantics of terms such as `active_line_asset` and `primary_reference`

#### Provenance State

- Display label: `Provenance State`
- Machine label: private shared contract family
- Concise definition: the display-state label that communicates whether supporting provenance is present, needs review, or is missing
- Boundary statement: provenance-state labels are UI-facing summaries, not a replacement for underlying evidence records

#### Readiness State

- Display label: `Readiness State`
- Machine label: private shared contract family
- Concise definition: the display-state label that communicates whether a preview is ready for review, composition, publication, or blocked by missing inputs
- Boundary statement: readiness-state labels are advisory UI labels and should not silently promote downstream artifacts into authoritative truth

### Promotion And Ownership Language

#### Route-Owned Pattern

- Display label: `Route-Owned Pattern`
- Machine label: planning term only
- Concise definition: a UI behavior or primitive that currently belongs to one route or consumer and is not yet promoted into the shared substrate
- Boundary statement: route-owned patterns may inform future promotion but should not be described as already-shared contracts

#### Shared Pattern

- Display label: `Shared Pattern`
- Machine label: planning term only
- Concise definition: a UI pattern explicitly promoted into the private shared UI substrate for reuse by more than one consumer
- Boundary statement: a shared pattern is still private UI guidance unless a later milestone promotes it further

#### Promotion Candidate

- Display label: `Promotion Candidate`
- Machine label: planning term only
- Concise definition: a route-owned pattern that now has enough reuse pressure or second-consumer evidence to justify shared treatment
- Boundary statement: promotion candidates are planning decisions, not contract changes by themselves

#### Mirrored Adoption

- Display label: `Mirrored Adoption`
- Machine label: planning term only
- Concise definition: a downstream repo copies private shared UI docs or files locally and records the upstream source revision it mirrored from
- Boundary statement: mirrored adoption preserves private UI guidance locally but does not convert that guidance into a public compatibility promise

#### Pinned-Upstream Import

- Display label: `Pinned-Upstream Import`
- Machine label: planning term only
- Concise definition: a downstream repo directly consumes a private shared UI file from an exact pinned `world-runtime` revision
- Boundary statement: a pinned-upstream import is a deliberate private dependency choice, not a guarantee that the path is a stable public surface

#### Second-Consumer Readiness

- Display label: `Second-Consumer Readiness`
- Machine label: planning term only
- Concise definition: the state where a shared UI candidate is documented clearly enough for a second consumer or explicit downstream adopter to evaluate reuse without repo archaeology
- Boundary statement: second-consumer readiness helps adoption and promotion decisions, but it does not promote a route-owned pattern by itself
