# Quickstart: Build & Validate the Options Document

**Feature**: Texture-to-Geometry Approaches Research | **Date**: 2026-06-28

This is the run/validation guide for the **documentation deliverable** (no add-on code).
Follow it to (re)generate the HTML review page and confirm the deliverable meets the spec.
Details of structure and rules live in `contracts/` and `data-model.md`; this guide just
runs and checks.

## Prerequisites

- Python 3.12 (already present: `python --version`).
- `python-markdown`: `pip install markdown`
- The deliverable Markdown authored under
  `specs/001-texture-geometry-research/deliverables/` (produced in `/speckit.implement`).

## Build the user-facing HTML review page

From the repository root:

```powershell
python tools\build_docs.py
```

**Expected**: `docs\index.html` is created/updated in < 5 s with no errors. Open it in a
browser (double-click) — it renders offline with a table of contents and the
"Recommendation at a Glance" up top.

## Run the automated validation checks

```powershell
python tools\build_docs.py --check    # C7: HTML build smoke check (no write)
python tools\check_deliverable.py     # C1-C6: file/section/citation/controls/prior-art
```

**Expected**: both exit `0`. Any failure prints the specific contract clause
(`validation-contract.md` C1–C7) that failed.

## Manual review (C8) — map to Success Criteria

Open `deliverables\summary.md` (or `docs\index.html`) and confirm against the spec:

| Check | Success Criterion |
|-------|-------------------|
| Primary approach + top reason clear within 15 min | SC-001 |
| ≥2 (target 3+) approaches, each with all required fields | SC-002 |
| 100% of major claims carry a citation tag | SC-003 |
| Full example journey + ≥6 controls with defaults | SC-004 |
| Every recommendation maps to a real Blender feature/API | SC-005 |
| Single recommended next step + open questions/risks | SC-006 |
| ≥2 prior-art entries with gaps + sources | SC-007 |

## Validation scenarios (prove the deliverable works)

1. **Decision scenario (US1)**: A reviewer reads `approaches.md` → can name the recommended
   primary approach, its top reason, and one fallback. *Pass if all three are unambiguous.*
2. **Workflow scenario (US2)**: A reviewer reads `addon-workflow.md` → can recount the
   cylinder→wood→place/size→apply-or-defer→export journey and list the six controls with
   defaults. *Pass if the journey and controls are complete.*
3. **Traceability scenario (US3)**: Pick any 3 claims at random → each has a citation tag
   resolving to a real local path or URL in `references.md`. *Pass if all 3 resolve.*

## What "done" means

C1–C7 pass automatically, C8 is signed off, and the three validation scenarios above pass.
Then the feature is complete and ready for `/speckit.tasks` follow-on (if iterating) or to
inform the next feature that designs/builds the actual add-on.
