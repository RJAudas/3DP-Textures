# Contract: Deliverable Document Outline

**Feature**: Texture-to-Geometry Approaches Research

This contract defines the **required structure** of the deliverable document set. The
implement phase MUST produce these files with at least these H2 (`##`) sections. The
validation checker (see `validation-contract.md`) enforces presence of the **Required
sections** marked below.

> Paths are relative to `specs/001-texture-geometry-research/`.

## `deliverables/00-overview.md`

- `## Purpose & Scope` *(Required)* — what this document set decides; geometry-first framing.
- `## Glossary` *(Required)* — displacement, modifier, subdivision, manifold, height-map, etc.
- `## How to Read This Set` — map of the other files.
- `## Out of Scope` *(Required)* — material/shader-only methods explicitly excluded (FR-011).

## `deliverables/approaches.md`

- `## Approaches Overview` *(Required)* — one-paragraph orientation + the comparison table.
- `## Comparison Matrix` *(Required)* — rows = approaches, columns = the Approach fields
  (mechanism, texture sources, inputs, strengths, limitations, print-readiness, export).
- One `## Approach: <name>` section **per approach** *(Required, ≥2)* — full Approach record
  per `data-model.md`, each with ≥1 citation tag.
- `## Recommendation` *(Required)* — exactly one primary + ≥1 fallback, justified (FR-004).
- `## Subdivision & Print-Scale Guidance` *(Required)* — base-mesh density vs. fidelity vs.
  performance; default density guidance in mm (FR-009).

## `deliverables/prior-art.md`

- `## Community Workflows` *(Required)* — how others texture for 3D printing (≥1).
- `## Existing Add-ons / Plugins` *(Required)* — prior-art tooling survey (≥1).
- Combined total ≥2 PriorArtEntry records (FR-014, SC-007), each with a web source.
- `## Gaps & Opportunities` — what is missing that our add-on would address.

## `deliverables/addon-workflow.md`

- `## Proposed User Journey` *(Required)* — ordered WorkflowSteps covering the full example
  (cylinder → panel → preset → place/size → preview → apply-or-defer → export) (FR-005).
- `## Controls` *(Required)* — table of Controls incl. the six required, each with purpose +
  default; texture-pick documented as preset **and** advanced (FR-006, clarification Q3).
- `## Texture Presets` *(Required)* — Wood (full) + Brick + Rock named (TexturePreset).
- `## Apply Now vs. Defer to Export` *(Required)* — both branches; non-destructive default
  recommended; clarify that export realizes un-applied modifiers via `apply_modifiers=True`
  (FR-007).
- `## Generalization to Other Shapes` *(Required)* — beyond cylinders; placement caveats
  (FR-008).

## `deliverables/references.md`

- `## References` *(Required)* — every Reference tag (`[S]`/`[M]`/`[T]`/`[W]`) with type,
  location, and the claim it supports (FR-010).

## `deliverables/summary.md`

- `## Recommendation at a Glance` *(Required)* — primary approach + top reason (SC-001).
- `## Approaches (Short)` *(Required)* — condensed comparison for non-technical review.
- `## Proposed Workflow (Short)` *(Required)* — the journey + key controls, plainly.
- `## Open Questions & Next Step` *(Required)* — risks + the single recommended next step
  feeding `/speckit.plan` follow-on or `/speckit.tasks` (FR-012, SC-006).

> `summary.md` is the **only** input rendered into `docs/index.html`; it must be
> self-contained and readable by a non-technical reviewer.
