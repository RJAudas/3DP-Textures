# Phase 1 Data Model: Document Information Schema

**Feature**: Texture-to-Geometry Approaches Research | **Date**: 2026-06-28

Because the deliverable is a document (not software), the "data model" is the **information
schema of the document** — the structured records the deliverable must capture. Each entity
below maps to repeated, comparable blocks in the Markdown so content stays consistent and the
HTML summary can be generated mechanically. Entities derive from the spec's Key Entities.

---

## Entity: Approach

A candidate Blender-native method for turning a texture into exportable geometry.

| Field | Type | Required | Notes / Validation |
|-------|------|----------|--------------------|
| `id` | slug | yes | e.g. `displace-procedural`, `displace-image`, `geometry-nodes` |
| `name` | text | yes | Human title |
| `mechanism` | prose | yes | How it deforms real geometry (must cite ≥1 reference) |
| `texture_sources` | enum[] | yes | Any of: `procedural`, `image-heightmap` |
| `required_inputs` | list | yes | Texture datablock/image, modifiers (e.g. Subdivision Surface), coordinate space |
| `controls` | ref→Control[] | yes | Controls this approach exposes |
| `strengths` | list | yes | ≥1 |
| `limitations` | list | yes | ≥1 |
| `print_readiness_risk` | enum + note | yes | `low` / `medium` / `high` + why (manifold, self-intersection, zero-area) |
| `export_behavior` | prose | yes | Whether it survives STL export with `apply_modifiers=True` (cite) |
| `recommended_role` | enum | yes | `primary` / `fallback` / `secondary` / `stretch` |
| `references` | ref→Reference[] | yes | ≥1 |

**Rules**: At least 2 Approach records (target ≥3). Exactly one record has
`recommended_role = primary`; at least one has `fallback`. Every Approach cites ≥1 Reference.

## Entity: Control

A user-facing setting the proposed add-on would expose.

| Field | Type | Required | Notes / Validation |
|-------|------|----------|--------------------|
| `id` | slug | yes | e.g. `strength`, `scale`, `coord-mode`, `direction`, `mid-level`, `texture-pick` |
| `name` | text | yes | UI label |
| `purpose` | prose | yes | What it changes for the user |
| `value_type` | text | yes | e.g. float (mm), enum, datablock/image picker |
| `default` | value | yes | Reasonable default; length values in mm for print scale |
| `applies_to` | ref→Approach[] | yes | Which approaches use it |
| `mode` | enum | yes | `preset` (quick) / `advanced` (raw) / `both` |

**Rules**: Must include at least: `texture-pick`, `strength`, `scale`, `coord-mode`,
`direction`, `mid-level` (spec FR-006). `texture-pick` must document both a curated-preset
form and an advanced raw form (clarification Q3).

## Entity: TexturePreset

A curated, named quick-start option mapping to a preconfigured setup.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | slug | yes | e.g. `wood`, `brick`, `rock` |
| `name` | text | yes | Display name |
| `maps_to` | prose | yes | Underlying texture type/params + approach it configures |
| `default_controls` | map | yes | Preset values for the shared Controls |

**Rules**: At least the example `wood` preset is fully specified; `brick` and `rock` named at
minimum. Each preset states which Approach it drives.

## Entity: WorkflowStep

One stage in the proposed end-to-end user journey.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `order` | int | yes | Sequence position |
| `user_action` | prose | yes | What the user does |
| `tool_response` | prose | yes | What the add-on does |
| `result_state` | enum | yes | `live-modifier` / `baked-geometry` / `exported` |

**Rules**: The sequence must cover the full example journey: add cylinder → open panel →
pick texture (preset) → place/size → preview → apply-now **or** defer-to-export → STL export
(spec FR-005). Must include both the apply-now and defer-to-export branches (FR-007).

## Entity: PriorArtEntry

An existing community workflow or add-on/plugin that already performs part of this task.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | slug | yes | |
| `name` | text | yes | Add-on / tutorial / workflow name |
| `kind` | enum | yes | `addon` / `workflow` / `tutorial` |
| `what_it_does` | prose | yes | Capability relevant to this project |
| `gaps` | list | yes | What it lacks vs. our geometry-first/STL goals |
| `source` | ref→Reference (web) | yes | Re-findable URL |

**Rules**: ≥2 entries total across workflows and/or add-ons (spec FR-014, SC-007).

## Entity: Reference

A citation supporting a claim.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `tag` | id | yes | `[S]`/`[M]`/`[T]`/`[W]` + number |
| `type` | enum | yes | `source` / `manual` / `toc` / `web` |
| `location` | path-or-url | yes | Local path or URL |
| `supports` | prose | yes | Which claim it backs |

**Rules**: Every major claim (approach mechanism, control behavior, export behavior) links to
≥1 Reference (spec FR-010, SC-003 = 100%).

---

## Relationships

```text
Approach 1—* Control          (an approach exposes many controls)
Approach 1—* Reference        (each approach cites sources)
Control  *—* Approach         (shared controls reused across approaches)
TexturePreset *—1 Approach    (a preset configures one approach)
WorkflowStep (ordered list)   (forms the proposed journey)
PriorArtEntry *—1 Reference   (web source)
```

## Mapping to deliverable files

| Entity | Lives primarily in |
|--------|--------------------|
| Approach, Reference (per-approach) | `deliverables/approaches.md` |
| Control, TexturePreset, WorkflowStep | `deliverables/addon-workflow.md` |
| PriorArtEntry | `deliverables/prior-art.md` |
| Reference (consolidated) | `deliverables/references.md` |
| Curated subset of all of the above | `deliverables/summary.md` → `docs/index.html` |
