# Feature Specification: Printable Texture Add-on (Texture-to-Geometry)

**Feature Branch**: `002-printable-texture-addon`

**Created**: 2026-06-28

**Status**: Draft

**Input**: User description: "Create a Blender add-on that allows users to convert surface textures into real, printable mesh geometry suitable for STL export."

## Clarifications

### Session 2026-06-28

- Q: What is the minimum target Blender version for the add-on? → A: Blender 4.2 LTS (provides
  the modern STL export operator the research targets, supports the Extensions platform, and is a
  long-support release).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Turn a texture into a printable STL (Priority: P1)

A maker creates a primitive object (for example a cylinder), opens the add-on, picks a
surface-texture preset such as *Wood*, sees the surface relief appear on the object, and exports
an STL. When that STL is opened in a slicer, the surface detail is present as real geometry rather
than only flat shading.

**Why this priority**: This is the core promise of the feature. Without it the add-on delivers no
value. It is the minimum end-to-end slice that turns "a texture that only affects rendering" into
"a printable textured object," which is the entire reason the add-on exists.

**Independent Test**: Can be fully tested by creating a primitive mesh, applying a texture preset
through the add-on, and exporting an STL, then confirming in a slicer that the exported mesh
contains the surface relief as actual geometry. Delivers a printable textured object end to end.

**Acceptance Scenarios**:

1. **Given** a selected mesh object with no texture relief, **When** the user applies a texture
   preset through the add-on, **Then** visible surface relief appears on the object.
2. **Given** an object with relief applied through the add-on, **When** the user exports an STL,
   **Then** the exported file contains the surface detail as real mesh geometry.
3. **Given** an exported STL produced by the add-on, **When** it is loaded into a slicer, **Then**
   the surface detail is preserved and the model can be sliced for printing.
4. **Given** a user with only basic Blender experience, **When** they follow the add-on's guided
   workflow, **Then** they reach a printable STL without manually configuring a multi-step
   texture-to-geometry workflow.

---

### User Story 2 - Adjust and preview the surface before exporting (Priority: P2)

A designer applies a texture, then interactively changes how pronounced and how large the surface
pattern is, watching the object update in the viewport. They iterate until the relief looks right,
all without permanently altering the base model, and only then export.

**Why this priority**: Predictable, repeatable, experiment-friendly editing is what makes the
add-on approachable instead of a one-shot gamble. It builds directly on the P1 slice and turns a
single result into a controllable workflow, but the feature can still ship and demonstrate value
with P1 alone.

**Independent Test**: Can be tested by applying a texture, changing the relief depth and pattern
size controls, and confirming the viewport preview updates accordingly and that the original base
model can be recovered (the edits are non-destructive). Delivers a controllable, low-risk editing
loop.

**Acceptance Scenarios**:

1. **Given** a texture applied through the add-on, **When** the user changes the relief depth,
   **Then** the previewed surface becomes more or less pronounced accordingly.
2. **Given** a texture applied through the add-on, **When** the user changes the pattern size,
   **Then** the previewed pattern scales accordingly.
3. **Given** a series of adjustments, **When** the user decides to revert, **Then** the original
   base model is recoverable because the workflow is non-destructive by default.
4. **Given** the user is satisfied with the preview, **When** they export, **Then** the exported
   STL matches the previewed relief.

---

### User Story 3 - Work across shapes and choose textures flexibly (Priority: P3)

A user applies the workflow to both flat and curved objects, picking from quick presets for common
looks (*Wood*, plus planned *Brick* and *Rock*) and, when needed, supplying their own texture
source for a specific real-world surface.

**Why this priority**: Broad shape support and texture choice widen the add-on's usefulness, but
the feature is already valuable and demonstrable on a single shape with a single preset. This story
extends reach rather than establishing the core experience.

**Independent Test**: Can be tested by running the same apply-preview-export workflow on a flat
object and a curved object, and by selecting both a built-in preset and a user-supplied texture
source, then confirming each produces a printable STL with the expected relief. Delivers
generalized, flexible texturing.

**Acceptance Scenarios**:

1. **Given** a curved object, **When** the user applies a texture preset, **Then** the relief wraps
   the surface without obvious tearing or seams from the chosen default.
2. **Given** a flat object, **When** the user applies a texture preset, **Then** the relief is
   applied cleanly across the face.
3. **Given** the preset picker, **When** the user selects a built-in preset, **Then** sensible
   defaults are applied and relief appears immediately.
4. **Given** a user who needs a specific surface, **When** they supply their own texture source,
   **Then** the add-on drives the relief from that source.

---

### Edge Cases

- **No eligible object selected**: When no mesh object is active, the add-on's controls are
  unavailable or clearly disabled, and the user is told what to select first.
- **Excessive relief depth**: When the requested relief depth is large relative to the object's
  wall thickness, the surface can self-intersect or become non-watertight; the add-on should warn
  the user and/or guide them toward a printable range before export.
- **Detail below printer resolution**: When the pattern is finer than a typical printer can
  reproduce, the user is guided that very small features may not print, expressed in real-world
  size terms.
- **Coarse base geometry**: When the object lacks enough surface density to express the chosen
  pattern, the add-on ensures enough density is present so the relief is actually generated.
- **Re-applying on an already-textured object**: Applying the workflow again updates the existing
  relief rather than silently stacking conflicting results.
- **Curved surfaces with a user-supplied flat texture source**: The user is warned that seams or
  stretching may appear and is steered toward a default that wraps curves cleanly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The add-on MUST present a discoverable interface inside Blender from which the whole
  workflow can be started.
- **FR-002**: The add-on MUST let the user target an existing selected mesh object as the subject
  of the texture-to-geometry workflow.
- **FR-003**: The add-on MUST let the user choose a surface texture, including at least one curated
  quick-start preset (*Wood* available; *Brick* and *Rock* planned) and an option to supply a
  custom texture source.
- **FR-004**: The add-on MUST transform the chosen visual surface texture into real surface
  geometry on the target object (not merely a rendering effect).
- **FR-005**: The add-on MUST show a live preview of the resulting surface relief in the viewport
  before export.
- **FR-006**: The add-on MUST let the user interactively adjust the generated surface, at minimum
  the relief depth (in real-world size terms) and the pattern size.
- **FR-007**: The add-on MUST support an iterative, non-destructive workflow by default so users
  can refine the appearance and recover the original base model.
- **FR-008**: The add-on MUST allow the user to export an STL whose mesh preserves the generated
  surface detail as real geometry.
- **FR-009**: The exported STL MUST match the relief shown in the preview at the time of export.
- **FR-010**: The add-on MUST work for common printable objects with both flat and curved surfaces,
  applying a default that wraps relief around curved shapes without requiring manual coordinate
  setup.
- **FR-011**: The add-on MUST require significantly fewer manual steps than Blender's native
  texture-to-geometry workflow and MUST NOT require the user to understand Blender's modifier
  stack, texture coordinate systems, or displacement workflow to reach a printable result.
- **FR-012**: The add-on MUST produce predictable, repeatable results: the same object, texture,
  and settings yield the same relief and the same exported geometry.
- **FR-013**: The add-on MUST warn the user when chosen settings are likely to produce a
  non-printable result (for example, relief too deep for the wall, or detail finer than a typical
  printer can reproduce).
- **FR-014**: The add-on MUST offer the user a choice between deferring geometry realization until
  export (the non-destructive default) and realizing the geometry immediately in the scene.

### Key Entities *(include if feature involves data)*

- **Target object**: The user's selected mesh that will receive printable surface relief; tracked
  state includes whether relief is currently live, realized, or exported.
- **Texture selection**: What drives the relief — either a curated preset or a user-supplied texture
  source — along with its associated default settings.
- **Surface settings**: The user-adjustable parameters that shape the relief, primarily relief depth
  (real-world size) and pattern size, plus advanced options for users who want them.
- **Preset**: A named quick-start (e.g. *Wood*) that bundles a texture choice with sensible default
  surface settings appropriate for printing.
- **Exported model**: The STL artifact whose geometry carries the generated surface detail.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new Blender user can go from a primitive object to a printable, textured STL using
  only the add-on, without consulting an external multi-step tutorial.
- **SC-002**: 100% of STLs exported through the recommended workflow contain the previewed surface
  detail as real geometry when inspected in a slicer.
- **SC-003**: A user can complete the full create-apply-preview-export sequence in markedly fewer
  steps than Blender's native workflow for the same result (target: at most one quarter of the
  manual steps).
- **SC-004**: At least 90% of first-time test users successfully produce a sliceable textured STL
  on their first attempt without manual texture-to-geometry configuration.
- **SC-005**: Adjusting a surface setting updates the viewport preview promptly enough to feel
  interactive (target: visible update within about one second on a typical primitive).
- **SC-006**: Reverting after experimentation restores the original base model in 100% of cases
  when the non-destructive default is used.
- **SC-007**: The same object, texture, and settings reproduce the same exported geometry every
  time.

## Assumptions

- The add-on targets **Blender 4.2 LTS or newer** as the minimum supported version; older
  releases are out of scope for the MVP.
- Users have Blender installed and know basic operations (creating primitives, selecting objects,
  exporting files), but not modifiers, texture coordinate systems, or displacement workflows.
- STL is the target export format for the MVP; other print formats are out of scope for v1.
- *Wood* is the fully designed launch preset; *Brick* and *Rock* are planned names that follow the
  same workflow and are not required for the MVP slice.
- The non-destructive, defer-to-export path is the recommended default; an explicit "realize now"
  option is provided for users who want the geometry in the scene.
- Printability guidance is expressed in real-world size terms (e.g. millimeters) so users can relate
  settings to their printer without understanding internal mesh density.
- Final watertightness validation for aggressive settings may rely on existing print-preparation
  tooling and is surfaced to the user as guidance rather than guaranteed automatically.
- Implementation strategy, architecture, and technical mechanisms are intentionally documented
  separately in the project's research and architecture deliverables and are not restated here.
