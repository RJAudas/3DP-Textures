# Feature Specification: Texture-to-Geometry Approaches Research

**Feature Branch**: `001-texture-geometry-research`

**Created**: 2026-06-28

**Status**: Draft

**Input**: User description: "Create a blender addon that will help users apply textures to objects that can then be exported as an STL. The purpose of this specification/feature is to research the options to make this happen, then figure out a way to build an addon that will streamline that workflow (e.g. a Displace modifier with a texture modifying the geometry of an object that has a Subdivision Surface modifier, plus node-editing or other workflows). Search the source and the web to see our options. The end product is a document describing possible approaches inside Blender to do this, and possible ways to streamline this process with an addon. Example workflow: add a cylinder, open the addon window, select a texture (e.g. wood), give controls to place and size the texture on the object, then either apply the modifications or leave it as a modifier that only applies on export. The outcome for this specification is a document to review our options/approaches — we aren't coding anything yet."

## Clarifications

### Session 2026-06-28

- Q: What texture *source* should the research cover for driving geometry? → A: Both
  procedural Blender textures and user-supplied image/height-maps — recommend
  procedural-first for the MVP, with image height-maps documented as a secondary source.
- Q: How should the research weigh local references vs. web sources? → A: Local
  source/manual/TOC are authoritative; use the web to supplement, focused on discovering
  how others apply textures for 3D printing (approaches/workflows) and any existing
  add-ons/plugins that already do part of this (prior art) — not code-level detail.
- Q: How should the user pick a "texture" in the proposed add-on workflow? → A: Both —
  curated named presets (Wood, Brick, Rock…) for a quick one-click start, plus an advanced
  mode exposing raw controls for power users.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Decide on a primary texture-to-geometry approach (Priority: P1)

As the project owner, I want a written, evidence-backed comparison of the ways Blender can
turn a surface texture (wood grain, brick, rock, etc.) into real, printable mesh geometry,
so that I can confidently choose the primary approach the future add-on will be built on
before any code is written.

**Why this priority**: Every later planning and implementation decision depends on choosing
the right core technique. Without a clear, justified recommendation the project cannot
proceed past planning. This story alone (a comparison that yields a recommendation) is the
minimum that delivers value.

**Independent Test**: Can be fully tested by having a reviewer read the document's
comparison section and confirm it lists at least two concrete Blender-native approaches,
states the trade-offs of each, and ends with a single clearly-justified recommended primary
approach plus at least one fallback — all without needing any code to exist.

**Acceptance Scenarios**:

1. **Given** the research document, **When** a reviewer reads the approach-comparison
   section, **Then** they find each candidate approach described with how it produces real
   geometry, its inputs (texture type, required modifiers, coordinate space), its strengths,
   its limitations, and whether it survives STL export with applied modifiers.
2. **Given** the research document, **When** a reviewer reaches the recommendation, **Then**
   exactly one primary approach is recommended with stated reasons, and at least one
   alternative/fallback approach is named for cases the primary does not handle well.
3. **Given** the example workflow (cylinder + wood texture), **When** the reviewer follows
   the document's walkthrough for the recommended approach, **Then** the steps map cleanly
   onto Blender features that exist today (no invented capabilities).

---

### User Story 2 - Understand the streamlined add-on workflow and UX (Priority: P2)

As the project owner, I want the document to translate the chosen technique(s) into a
proposed add-on workflow and UI controls, so that I understand what the tool will ask the
user to do and what knobs it exposes before committing to a design.

**Why this priority**: Choosing a technique is necessary but not sufficient; the project's
goal is a *streamlined* workflow. This story turns research into a concrete UX proposal that
the `plan` phase can build on, but it depends on Story 1's recommendation.

**Independent Test**: Can be tested by reading the proposed-workflow section and confirming
it describes the end-to-end user journey (e.g., add cylinder → open panel → pick texture →
place/size → preview → apply-or-defer-to-export) and enumerates the specific user controls
with sensible default behavior, without requiring an implementation.

**Acceptance Scenarios**:

1. **Given** the document, **When** a reviewer reads the proposed-workflow section, **Then**
   it presents at least one concrete end-to-end user journey from object creation to STL
   export, matching the example (cylinder, wood texture, placement/sizing controls).
2. **Given** the document, **When** a reviewer reads the controls list, **Then** each
   exposed control (e.g., texture choice, strength, scale, placement/coordinate mode,
   direction, mid-level) is named with its purpose and a reasonable default, and texture
   choice is presented as both a curated preset picker and an advanced raw-control mode.
3. **Given** the document, **When** a reviewer reads the apply-vs-defer discussion, **Then**
   it explains both keeping the effect as a live (export-time) modifier and baking it into
   permanent geometry, including when each is appropriate.

---

### User Story 3 - Trace every claim to an authoritative reference (Priority: P3)

As a future implementer, I want each technical claim in the document linked to a Blender
source file, manual page, or reputable web source, so that I can verify behavior and jump
straight to the relevant API when implementation begins.

**Why this priority**: Citations turn the document from an opinion into a reusable map for
the `plan` and `implement` phases. It is valuable but the document is already actionable
without exhaustive references, so it ranks lowest.

**Independent Test**: Can be tested by spot-checking the document's references and confirming
that each major approach, control, and export claim points to a real local source/manual
path (per the reference TOC) or a cited web resource that supports the claim.

**Acceptance Scenarios**:

1. **Given** the document, **When** a reviewer checks any approach's "how it works" claim,
   **Then** it cites a concrete reference (local source path, manual page, or web URL).
2. **Given** the document, **When** a reviewer checks the STL-export claims, **Then** they
   are backed by references to the export documentation/operator and the apply-modifiers
   behavior.
3. **Given** the document, **When** a reviewer checks a web-sourced claim, **Then** the
   source is identified well enough to be re-found and judged for reliability.

---

### Edge Cases

- **Texture has no real geometric effect**: The document MUST flag approaches that only
  change shading/material (no exportable geometry) and explicitly mark them out of scope as
  deliverables, per the geometry-first principle.
- **Insufficient base geometry**: The document MUST address what happens when the target
  mesh has too few faces for displacement to show (e.g., a raw cylinder) and how
  subdivision (Subdivision Surface modifier or pre-subdivided mesh) interacts with the
  chosen approach and with modifier ordering.
- **Coordinate/placement mismatch**: The document MUST address how texture placement and
  sizing behave on non-flat shapes (e.g., cylindrical wrap vs. local/global/UV/object
  coordinates) and where seams or stretching can occur.
- **Non-printable output**: The document MUST address cases where a chosen approach can
  yield non-manifold, self-intersecting, or zero-area geometry, and note how each approach
  fares for print-readiness.
- **Performance on dense meshes**: The document MUST note approaches that become slow or
  memory-heavy when subdivision is high enough to capture fine texture detail.
- **Conflicting Blender versions / deprecated APIs**: The document SHOULD note where an
  approach depends on features tied to a specific Blender baseline (e.g., the legacy STL
  exporter vs. the current one) so the plan targets the right version.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The deliverable MUST be a single reviewable research document stored in this
  feature directory (e.g., `research.md`) that surveys Blender-native ways to convert a
  surface texture into real, exportable mesh geometry for 3D printing.
- **FR-002**: The document MUST describe at least two distinct geometry-producing approaches,
  including at minimum (a) a Displace-modifier-with-texture approach over a subdivided mesh
  (Subdivision Surface modifier or pre-subdivided geometry), and (b) a Geometry Nodes /
  node-based approach; it MAY include other found options. It MUST cover both texture
  *sources* — procedural Blender textures (e.g., Wood/Noise/Voronoi datablocks) and
  user-supplied image/height-map textures — and MUST recommend procedural-first for the
  initial MVP while documenting image height-maps as a supported secondary source.
- **FR-003**: For each approach, the document MUST record: how it produces geometry, its
  required inputs (texture type/datablock, modifiers, coordinate space), its controls, its
  strengths, its limitations, its print-readiness risks, and whether it survives STL export
  with modifiers applied.
- **FR-004**: The document MUST include a comparison and a single recommended primary
  approach with explicit justification, plus at least one named fallback approach.
- **FR-005**: The document MUST propose at least one streamlined add-on workflow that maps
  the recommended approach to an end-to-end user journey matching the example (add a
  cylinder → open the add-on panel → choose a texture such as wood → place and size the
  texture on the object → preview → either apply/bake the geometry or leave it as a
  modifier that only applies on export).
- **FR-006**: The proposed workflow MUST enumerate the user-facing controls it would expose
  (at minimum: texture selection, strength, scale/size, placement/coordinate mode,
  direction, and mid-level) with each control's purpose and a reasonable default. Texture
  selection MUST be described as both a curated preset picker (named presets such as Wood,
  Brick, Rock that map to preconfigured setups) and an advanced mode exposing the raw
  controls for power users; for image/height-map sources it MUST note image-loading and
  UV/coordinate placement controls.
- **FR-007**: The document MUST describe the "apply now" (bake to permanent geometry) versus
  "defer to export" (live modifier applied at STL export) options and when each is
  appropriate, consistent with non-destructive-by-default behavior.
- **FR-008**: The document MUST address the example object types beyond cylinders at least
  briefly (how the approach generalizes to other primitives/meshes) and call out
  shape-specific placement concerns.
- **FR-009**: The document MUST identify how subdivision level / base mesh density affects
  texture fidelity and performance, and recommend default density guidance for print scale
  (millimeters).
- **FR-010**: Every major technical claim MUST cite an authoritative reference. The local
  Blender source (`D:\dev\blender\blender`), manual (`D:\dev\blender\blender-manual`), and
  reference TOC (`D:\dev\blender\blender-plugin-reference-toc.md`) are the authoritative
  ground truth; web sources MAY supplement them to capture how others approach the problem
  and MUST be cited with a re-findable URL.
- **FR-014**: The document MUST include a brief prior-art survey of how others apply textures
  to objects for 3D printing in Blender (community workflows/approaches) and of existing
  add-ons/plugins that already perform part of this task, noting for each what it does, what
  it lacks for this project's goals, and the source/URL. This survey focuses on
  approaches/workflows and tooling, not on reproducing their code.
- **FR-011**: The document MUST explicitly mark material-only / shader-only "texture"
  techniques as non-deliverable (preview-only, non-exporting) so they are not mistaken for
  geometry solutions.
- **FR-012**: The document MUST end with a short "open questions / risks" list and a
  recommended next step that feeds directly into the `/speckit.plan` phase.
- **FR-013**: The document MUST NOT include production add-on code; illustrative snippets or
  API references are allowed only to support an approach, not as an implementation.

### Key Entities *(include if feature involves data)*

- **Approach**: A candidate Blender-native method for turning a texture into exportable
  geometry. Attributes: name, mechanism (how it deforms geometry), required inputs,
  controls, strengths, limitations, print-readiness risk, export behavior, reference(s).
- **Control**: A user-facing setting the proposed add-on would expose. Attributes: name,
  purpose, value type/range, reasonable default, which approach(es) it applies to.
- **Workflow Step**: One stage in the proposed end-to-end user journey. Attributes: order,
  user action, what the tool does, resulting state (live modifier vs. baked geometry).
- **Reference**: A citation supporting a claim. Attributes: type (source / manual / TOC /
  web), location (path or URL), what claim it supports.
- **Prior-Art Entry**: An existing community workflow or add-on/plugin that already performs
  part of this task. Attributes: name, what it does, gaps vs. this project's goals,
  source/URL.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can read the document and, within 15 minutes, name the recommended
  primary approach and its top reason, with no further explanation needed.
- **SC-002**: The document compares at least 2 (target 3+) distinct geometry-producing
  approaches, each covering all required attributes (mechanism, inputs, controls, strengths,
  limitations, print-readiness, export behavior).
- **SC-003**: 100% of major technical claims (approach mechanisms, control behaviors, and
  STL-export behavior) carry at least one authoritative citation.
- **SC-004**: The proposed workflow covers the full example journey end to end (object
  creation through STL export) and lists at least the six required controls, each with a
  default — verifiable by checklist.
- **SC-005**: A future implementer can map every recommended approach and control to a
  concrete, real Blender feature/API reference (no invented capabilities) — verifiable by
  spot-checking citations.
- **SC-006**: The document yields a clear, single recommended next step for the planning
  phase and an explicit list of open questions/risks.
- **SC-007**: The document includes a prior-art survey naming at least two community
  workflows and/or existing add-ons/plugins relevant to texture-for-3D-print, each with its
  gaps and a re-findable source — verifiable by spot-checking.

## Assumptions

- The deliverable is a research/options document only; no production add-on code is written
  in this feature (the user stated "we aren't actually coding anything yet").
- Target output is STL for 3D printing, so "texture" means real, exportable mesh geometry,
  not render-only materials — consistent with the project constitution's geometry-first
  principle.
- The future add-on targets the modern Blender extension baseline (Blender 4.2 LTS or newer)
  per the constitution; the research will note version-specific concerns where relevant.
- The local references exist and are authoritative: Blender source at
  `D:\dev\blender\blender`, the manual at `D:\dev\blender\blender-manual`, and the curated
  reference map at `D:\dev\blender\blender-plugin-reference-toc.md`.
- Wood grain is the representative example texture, but the recommended approach should
  generalize to other procedural textures (brick, rock, noise) and to other mesh shapes.
  Both procedural textures and user-supplied image/height-maps are in scope, with procedural
  recommended first for the MVP.
- The future add-on UX offers curated texture presets (Wood, Brick, Rock…) plus an advanced
  raw-control mode; the research scopes its workflow/controls proposal accordingly.
- Web sources may be consulted to supplement local references and will be cited; the focus
  of web research is discovering how others apply textures for 3D printing (workflows and
  existing add-ons/plugins), not code-level reproduction. Local source/manual/TOC remain
  authoritative.
- Real-world print scale is millimeters; displacement defaults are discussed at that scale.
