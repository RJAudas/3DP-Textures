---

description: "Task list for Texture-to-Geometry Approaches Research"
---

# Tasks: Texture-to-Geometry Approaches Research

**Input**: Design documents from `/specs/001-texture-geometry-research/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: This is a research/documentation feature — **no product code and no software
tests**. The spec did not request tests. "Validation" here means deliverable
completeness/citation/HTML-build checks (see `contracts/validation-contract.md`), authored as
small authoring-only tooling, not application tests.

**Organization**: Tasks are grouped by user story (US1–US3 from spec.md) so each can be
authored and reviewed independently. All paths are relative to the repository root
`D:\dev\blender\3DP-Textures\`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths are included in every task

## Path Conventions

- Deliverable Markdown (source of truth): `specs/001-texture-geometry-research/deliverables/`
- Authoring-only tooling: `tools/`
- Generated user-facing HTML: `docs/`
- There is **no `src/` or `tests/` product tree** — nothing is coded in this feature.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the deliverable/tooling structure and authoring environment.

- [ ] T001 Create the deliverable and output structure: `specs/001-texture-geometry-research/deliverables/`, `tools/`, and `docs/` directories, each with empty skeleton placeholder files (`deliverables/00-overview.md`, `approaches.md`, `prior-art.md`, `addon-workflow.md`, `references.md`, `summary.md`) containing only their top H1 title
- [ ] T002 Install and verify the HTML-build dependency: `pip install markdown`; confirm `python -c "import markdown"` succeeds and record the version in `specs/001-texture-geometry-research/quickstart.md` Prerequisites
- [ ] T003 [P] Implement `tools/build_docs.py` per `specs/001-texture-geometry-research/contracts/html-build-contract.md` (renders `deliverables/summary.md` → `docs/index.html`, embedded CSS, `--check` mode, clear error if source/markdown missing)
- [ ] T004 [P] Implement `tools/check_deliverable.py` per `specs/001-texture-geometry-research/contracts/validation-contract.md` checks C1–C6 (file presence, required sections, approach completeness, citation integrity, controls coverage, prior-art coverage)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared framing and the citation system every story writes into.

**⚠️ CRITICAL**: No user-story authoring should finalize until these exist — all stories rely
on the glossary and the citation scheme.

- [ ] T005 Author `specs/001-texture-geometry-research/deliverables/00-overview.md` with required sections `## Purpose & Scope`, `## Glossary`, `## How to Read This Set`, `## Out of Scope` (mark material/shader-only methods out of scope per FR-011), framed geometry-first per the constitution
- [ ] T006 Establish the citation scheme in `specs/001-texture-geometry-research/deliverables/references.md`: create the `## References` section and document the `[S]`/`[M]`/`[T]`/`[W]` tag convention (source/manual/TOC/web) that all stories cite into (FR-010)

**Checkpoint**: Shared framing + citation system ready — user stories can begin.

---

## Phase 3: User Story 1 - Decide on a primary texture-to-geometry approach (Priority: P1) 🎯 MVP

**Goal**: Produce `approaches.md` — an evidence-backed comparison of geometry-producing
approaches ending in one justified primary recommendation plus a fallback.

**Independent Test**: A reviewer reads `approaches.md` and can name the recommended primary
approach, its top reason, and one fallback; each approach lists mechanism, inputs, controls,
strengths, limitations, print-readiness, and export behavior, each with a citation.

- [ ] T007 [P] [US1] Research the Displace-modifier + procedural Texture approach over a subdivided mesh from local refs (`D:\dev\blender\blender-manual\manual\modeling\modifiers\deform\displace.rst`, `D:\dev\blender\blender\source\blender\modifiers\intern\MOD_displace.cc`, `rna_modifier.cc`, `DNA_texture_types.h`, `rna_texture.cc`); capture notes + candidate citation tags in `specs/001-texture-geometry-research/deliverables/approaches.md` working notes
- [ ] T008 [P] [US1] Research the image/height-map displacement approach (UV/coordinate-driven) from local refs (`displace.rst` `texture_coords='UV'`, `D:\dev\blender\blender-manual\manual\render\shader_nodes\input\texture_coordinate.rst`); capture notes for `approaches.md`
- [ ] T009 [P] [US1] Research the Geometry Nodes / node-based displacement approach (`D:\dev\blender\blender-manual\manual\modeling\modifiers\introduction.rst` GN-as-custom-modifier, plus reputable web sources for GN displacement patterns); capture notes for `approaches.md`
- [ ] T010 [P] [US1] Research STL export behavior with `apply_modifiers=True` (`D:\dev\blender\blender-manual\manual\files\import_export\stl.rst`, `D:\dev\blender\blender\source\blender\editors\io\io_stl_ops.cc`, `D:\dev\blender\blender\source\blender\io\stl\exporter\stl_export.cc`); capture export-behavior notes for each approach
- [ ] T011 [US1] Author `## Approaches Overview`, `## Comparison Matrix`, and one `## Approach: <name>` section per approach (≥2, target 3) in `specs/001-texture-geometry-research/deliverables/approaches.md` using the Approach schema from `data-model.md`, each with ≥1 citation tag (depends on T007–T010)
- [ ] T012 [US1] Author `## Recommendation` (exactly one primary + ≥1 fallback, justified — FR-004) and `## Subdivision & Print-Scale Guidance` (mm-scale density vs. fidelity vs. performance — FR-009) in `specs/001-texture-geometry-research/deliverables/approaches.md`
- [ ] T013 [US1] Add all approach/mechanism/export citation tags used in `approaches.md` to `## References` in `specs/001-texture-geometry-research/deliverables/references.md`

**Checkpoint**: `approaches.md` is complete and independently reviewable (MVP).

---

## Phase 4: User Story 2 - Understand the streamlined add-on workflow and UX (Priority: P2)

**Goal**: Produce `addon-workflow.md` (proposed journey, controls, presets, apply-vs-defer)
and `prior-art.md` (how others do it + existing add-ons informing the design).

**Independent Test**: A reviewer reads `addon-workflow.md` and can recount the
cylinder→wood→place/size→apply-or-defer→export journey and list the six controls with
defaults; `prior-art.md` names ≥2 community workflows/add-ons with gaps and sources.

- [ ] T014 [P] [US2] Web research (local-primary, web-supplemental per spec clarification): how others apply textures to objects for 3D printing in Blender (workflows) and existing add-ons/plugins that do part of this; capture entries + `[W]` sources in `specs/001-texture-geometry-research/deliverables/prior-art.md` working notes
- [ ] T015 [US2] Author `specs/001-texture-geometry-research/deliverables/prior-art.md` with `## Community Workflows`, `## Existing Add-ons / Plugins`, and `## Gaps & Opportunities` — ≥2 PriorArtEntry records total, each with a `[W]` web citation (FR-014, SC-007) (depends on T014)
- [ ] T016 [US2] Author `## Proposed User Journey` in `specs/001-texture-geometry-research/deliverables/addon-workflow.md` as ordered WorkflowSteps covering add cylinder → open panel → pick texture preset → place/size → preview → apply-or-defer → STL export (FR-005)
- [ ] T017 [US2] Author `## Controls` (the six required controls — texture selection, strength, scale, coordinate mode, direction, mid-level — each with purpose + default; texture-pick documented as preset **and** advanced) and `## Texture Presets` (Wood fully specified, Brick + Rock named) in `specs/001-texture-geometry-research/deliverables/addon-workflow.md` (FR-006, clarification Q3)
- [ ] T018 [US2] Author `## Apply Now vs. Defer to Export` (both branches; non-destructive default; note un-applied modifiers are realized at export via `apply_modifiers=True`) and `## Generalization to Other Shapes` (beyond cylinders; placement/seam caveats) in `specs/001-texture-geometry-research/deliverables/addon-workflow.md` (FR-007, FR-008)
- [ ] T019 [US2] Add all workflow/control/export/prior-art citation tags used in `addon-workflow.md` and `prior-art.md` to `## References` in `specs/001-texture-geometry-research/deliverables/references.md`

**Checkpoint**: Workflow + prior-art deliverables complete and independently reviewable.

---

## Phase 5: User Story 3 - Trace every claim to an authoritative reference (Priority: P3)

**Goal**: Make `references.md` complete and ensure every major claim across the set resolves
to a real source/manual/TOC path or web URL.

**Independent Test**: Pick any 3 claims at random across the deliverables — each has a
citation tag that resolves to a real local path or URL in `references.md`.

- [ ] T020 [US3] Consolidate and complete `specs/001-texture-geometry-research/deliverables/references.md`: every `[S]`/`[M]`/`[T]`/`[W]` tag defined with its `type`, `location` (real path or URL), and the claim it supports (FR-010)
- [ ] T021 [US3] Audit all `specs/001-texture-geometry-research/deliverables/*.md`: confirm every major claim (approach mechanism, control behavior, STL export behavior) carries ≥1 resolvable citation tag; add missing tags/sources (SC-003 = 100%, SC-005 no invented APIs)
- [ ] T022 [US3] Run `python tools/check_deliverable.py` citation-integrity check (C4) and fix any undefined or dangling tags until it passes

**Checkpoint**: All claims traceable; citation integrity check passes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Build the user-facing HTML review surface and run final validation.

- [ ] T023 Author `specs/001-texture-geometry-research/deliverables/summary.md` (curated, non-technical) with `## Recommendation at a Glance`, `## Approaches (Short)`, `## Proposed Workflow (Short)`, and `## Open Questions & Next Step` (FR-012, SC-001, SC-006)
- [ ] T024 Generate the review page: run `python tools/build_docs.py` to produce `docs/index.html`; open it in a browser and confirm it renders offline with a table of contents and the recommendation up top (C7)
- [ ] T025 [P] Run full automated validation: `python tools/check_deliverable.py` (C1–C6) and `python tools/build_docs.py --check` (C7); fix any failures until both exit 0
- [ ] T026 [P] Manual review sign-off: walk `specs/001-texture-geometry-research/quickstart.md` and confirm spec Success Criteria SC-001…SC-007 (C8)
- [ ] T027 Final consistency pass across the deliverable set in `specs/001-texture-geometry-research/deliverables/` (cross-links from `00-overview.md`, consistent terminology/glossary, recommendation matches between `approaches.md` and `summary.md`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup — provides shared glossary + citation system; blocks finalizing any story.
- **User Stories (Phase 3–5)**: Depend on Foundational. US1 (P1) is the MVP. US2 and US3 can start after Foundational; US3 is most effective once US1/US2 content exists (it audits their citations).
- **Polish (Phase 6)**: Depends on US1–US3 content (summary + HTML aggregate everything).

### User Story Dependencies

- **US1 (P1)**: Independent — needs only Foundational. Delivers `approaches.md` (MVP).
- **US2 (P2)**: Independent of US1 for authoring — needs only Foundational. Delivers `addon-workflow.md` + `prior-art.md`.
- **US3 (P3)**: Independently testable, but its audit (T021) is most useful after US1/US2 claims exist; references.md (T020) can begin anytime after Foundational.

### Within Each User Story

- Research/notes tasks (T007–T010, T014) before the authoring tasks that consume them.
- Approach sections (T011) before Recommendation (T012).
- Content authored before its citations are consolidated (T013, T019 → T020).

### Parallel Opportunities

- Setup: T003 and T004 are [P] (different files).
- US1 research: T007, T008, T009, T010 are all [P] (independent reading/notes).
- US2: T014 (prior-art research) is [P] and can run alongside US1 authoring.
- Polish: T025 and T026 are [P].
- Whole stories: US1 and US2 authoring can proceed in parallel by different contributors once Foundational is done.

---

## Parallel Example: User Story 1 Research

```text
# Launch all US1 research/notes tasks together (independent reading):
Task: "T007 Research Displace + procedural over subdivided mesh (local refs)"
Task: "T008 Research image/height-map displacement (UV coords)"
Task: "T009 Research Geometry Nodes displacement (intro.rst + web)"
Task: "T010 Research STL export apply_modifiers behavior"
# Then author approaches.md (T011) from the combined notes.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (structure + tooling + `pip install markdown`).
2. Complete Phase 2: Foundational (overview/glossary + citation scheme).
3. Complete Phase 3: User Story 1 → `approaches.md`.
4. **STOP and VALIDATE**: A reviewer can pick the primary approach + fallback from
   `approaches.md` alone. Optionally build a partial `summary.md`/HTML for early review.

### Incremental Delivery

1. Setup + Foundational → ready.
2. US1 → `approaches.md` reviewable (MVP — the core decision).
3. US2 → `addon-workflow.md` + `prior-art.md` reviewable.
4. US3 → full citation traceability.
5. Polish → `summary.md` + `docs/index.html` for high-level browser review; final validation.

### Parallel Team Strategy

After Foundational: Contributor A authors US1 (`approaches.md`), Contributor B authors US2
(`addon-workflow.md` + `prior-art.md`); US3 audits citations as content lands; Polish builds
the HTML and runs validation.

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps each task to a user story for traceability.
- No software tests (no code in this feature); "validation" = `check_deliverable.py` (C1–C6),
  `build_docs.py --check` (C7), and manual SC sign-off (C8) per `contracts/validation-contract.md`.
- Local Blender source/manual/TOC are authoritative; web is supplemental and always cited.
- Commit after each task or logical group; stop at any checkpoint to review a deliverable.
