# Implementation Plan: Texture-to-Geometry Approaches Research

**Branch**: `001-texture-geometry-research` | **Date**: 2026-06-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-texture-geometry-research/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

This feature is **research and documentation only — no add-on code is written**. The goal is
to investigate the ways Blender can turn a surface texture (wood grain, brick, rock, …) into
real, printable mesh geometry for STL export, and to propose how a future add-on could
streamline that workflow.

The deliverable is a **two-surface document set**:

1. **Detailed, agent-friendly Markdown docs** (source of truth) — a small set of focused
   `.md` files an implementing agent can reference directly during later phases.
2. **A high-level, user-friendly HTML page** (review surface) — generated from a curated
   summary so the project owner can review options/recommendations in a browser.

Technical approach: author the Markdown deliverables by mining the local Blender source,
manual, and reference TOC (authoritative), supplemented by targeted web research into how
others texture objects for 3D printing and what add-ons already exist (prior art). A small
Python build step (`python-markdown`) renders the HTML review page from a summary Markdown
file. No Blender APIs are exercised in this feature.

## Technical Context

**Language/Version**: Markdown (CommonMark) for all deliverables; Python 3.12 for the
Markdown→HTML build step. **No Blender/product runtime code in this feature.**

**Primary Dependencies**: `python-markdown` (with `toc`, `tables`, `fenced_code`, `sane_lists`
extensions) for HTML generation. Research *inputs*: local Blender source
(`D:\dev\blender\blender`), manual (`D:\dev\blender\blender-manual`), reference TOC
(`D:\dev\blender\blender-plugin-reference-toc.md`), and cited web sources.

**Storage**: Files only — Markdown deliverables + generated static HTML. No database.

**Testing**: Document validation rather than software tests — (1) a section/citation
completeness check (Python script asserting required sections exist and every approach has a
citation), (2) an HTML build smoke check (file generated, non-empty, no build errors),
(3) a human review pass against `quickstart.md` and the spec's Success Criteria. **No
headless Blender tests** (Constitution Principle V applies to future code, not this doc).

**Target Platform**: Static HTML viewable in any browser on Windows; Markdown readable in
any editor / by agents.

**Project Type**: Research / documentation deliverable in a single repository.

**Performance Goals**: N/A for content; the HTML build SHOULD complete in < 5 seconds.

**Constraints**: No product/add-on code. Geometry-first scope (material/shader-only methods
are explicitly out of scope as deliverables). Local references are authoritative; web is
supplemental and always cited. The build step MUST be re-runnable and dependency-light.

**Scale/Scope**: One deliverable set — ~5 focused Markdown docs covering ≥2 (target 3+)
geometry approaches, a prior-art survey, and a proposed add-on workflow — plus one generated
HTML review page.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution v1.0.1. This feature produces **no executable code**, so the engineering
principles are evaluated as *content guidance the document must uphold* rather than build
gates:

| Principle | Applies here as | Status |
|-----------|-----------------|--------|
| I. Geometry-First, Print-Ready Output | Document MUST center exportable geometry and mark shader-only methods non-deliverable (spec FR-011). | ✅ PASS |
| II. Native Blender Integration & API Discipline | Document MUST describe documented `bpy`/modifier approaches only; no invented APIs (spec FR-010, SC-005). | ✅ PASS |
| III. Non-Destructive by Default | Document MUST cover live-modifier (defer-to-export) vs. bake, recommending non-destructive default (spec FR-007). | ✅ PASS |
| IV. Multiple Strategies Behind One Interface | Document MUST compare ≥2 approaches behind one proposed UI (spec FR-002, FR-004, FR-005). | ✅ PASS |
| V. Headless, Automated Validation (NON-NEGOTIABLE) | No geometry code is produced; validation here = section/citation checks + review. Principle V re-applies when the add-on is built. | ✅ PASS (N/A to doc) |
| Reference Materials | Plan and deliverables cite the local source/manual/TOC (spec FR-010, constitution §Reference Materials). | ✅ PASS |

**Gate result**: PASS. No principle violations. The single notable deviation — using a Python
build dependency (`python-markdown`) — is authoring tooling, not a runtime add-on dependency,
so the constitution's "no third-party runtime dependencies" rule does not apply. Recorded in
Complexity Tracking for transparency.

## Project Structure

### Documentation (this feature)

```text
specs/001-texture-geometry-research/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output — planning decisions (how we research & build)
├── data-model.md        # Phase 1 output — the document's information schema
├── quickstart.md        # Phase 1 output — how to build & validate the deliverable
├── contracts/           # Phase 1 output — deliverable structure & HTML build contracts
│   ├── document-outline.md
│   ├── validation-contract.md
│   └── html-build-contract.md
├── checklists/
│   └── requirements.md  # Spec quality checklist (from /speckit.specify)
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created by /speckit.plan)
```

### Deliverables & tooling (produced later, during /speckit.implement)

This feature ships **documents, not source code**. The Markdown set is the source of truth;
the HTML page is generated from a curated summary.

```text
specs/001-texture-geometry-research/deliverables/
├── 00-overview.md          # Scope, glossary, how to read, geometry-first framing
├── approaches.md           # Catalog + comparison of geometry approaches + recommendation
├── prior-art.md            # Community 3D-print texturing workflows + existing add-ons survey
├── addon-workflow.md       # Proposed streamlined add-on: journey, presets+advanced controls,
│                           #   apply-now vs. defer-to-export
├── references.md           # Consolidated citations (source / manual / TOC / web)
└── summary.md              # Curated high-level summary -> input for the HTML review page

tools/
└── build_docs.py           # Python: renders summary.md (+ optional full set) -> docs/*.html
                            #   Authoring tooling only; NOT part of any future add-on

docs/                        # Generated, user-facing review surface (open in a browser)
└── index.html              # High-level, styled review page built from summary.md
```

**Structure Decision**: Single-repo documentation deliverable. There is **no `src/` or
`tests/` product tree** because nothing is coded in this feature. The detailed Markdown lives
under the feature's `deliverables/` folder (agent-referenceable, version-controlled, single
source of truth). A dependency-light Python build script in `tools/` generates the
user-facing HTML into a repo-root `docs/` folder for easy browser review. Keeping Markdown as
the authored source and HTML as a generated artifact avoids content drift between the two
surfaces the user requested.

## Complexity Tracking

> Only deviations from the constitution are recorded here.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| Python `markdown` build dependency for HTML | User explicitly requested a high-level HTML review surface in addition to agent-friendly Markdown; a reproducible build avoids hand-maintained HTML drifting from the Markdown source of truth. | Hand-writing HTML rejected (drift + maintenance); pandoc rejected (not installed; heavier external dependency than a single pip package). The dependency is authoring-only and never ships in the future add-on, so Constitution §Platform "no third-party runtime dependencies" is not triggered. |
