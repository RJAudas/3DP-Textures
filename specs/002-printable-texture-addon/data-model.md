# Phase 1 Data Model: Printable Texture Add-on

Entities here are Blender data structures and add-on-defined `PropertyGroup`s, not a database
schema. Field types reference `bpy.props` / `bpy.types`. Maps the spec § Key Entities to concrete
runtime data. Property mappings cite the Displace RNA properties documented in the reference TOC
(`source/blender/makesrna/intern/rna_modifier.cc`) and manual
(`modifiers/deform/displace.rst`).

---

## Entity: SurfaceSettings (PropertyGroup on Object)

The user-adjustable state for one target object. Stored as
`Object.tdp_surface = PointerProperty(type=SurfaceSettings)`.

| Field | Type | Default | Maps to / Notes |
|-------|------|---------|-----------------|
| `preset` | `EnumProperty` {`WOOD`,`BRICK`,`ROCK`,`CUSTOM`} | `WOOD` | Selects a preset bundle or custom source. Brick/Rock are named stubs in v1. |
| `strategy` | `EnumProperty` {`PROCEDURAL`,`IMAGE`} | `PROCEDURAL` | Which engine strategy drives Displace. `IMAGE` enables the fallback (A2). |
| `texture` | `PointerProperty(Texture)` | created on apply | The `Texture` datablock referenced by the Displace modifier (`DisplaceModifier.texture`). |
| `image` | `PointerProperty(Image)` | `None` | Height-map for `IMAGE` strategy (wrapped in a `TEX_IMAGE` texture). |
| `strength_mm` | `FloatProperty` (unit LENGTH, min 0) | `0.4` (mm) | Relief depth; written to `DisplaceModifier.strength` (scene-unit aware). |
| `scale` | `FloatProperty` (min > 0) | `1.0` | Pattern size/frequency; texture `noise_scale`/size. |
| `coord_mode` | `EnumProperty` {`LOCAL`,`GLOBAL`,`OBJECT`,`UV`} | `LOCAL` | `DisplaceModifier.texture_coords`. |
| `direction` | `EnumProperty` {`NORMAL`,`X`,`Y`,`Z`,`RGB_TO_XYZ`} | `NORMAL` | `DisplaceModifier.direction`. |
| `mid_level` | `FloatProperty` (0–1) | `0.5` | `DisplaceModifier.mid_level`. |
| `subdiv_auto` | `BoolProperty` | `True` | When true, level computed for ~0.2–0.5 mm edges. |
| `subdiv_level` | `IntProperty` (1–6) | computed | `SubsurfModifier.levels` (Simple). Used when `subdiv_auto` is False. |
| `apply_mode` | `EnumProperty` {`DEFER`,`APPLY_NOW`} | `DEFER` | Non-destructive default vs explicit bake. |

**Validation rules**:

- `strength_mm >= 0`; warn (not block) when `strength_mm` exceeds ~10% of the object's smallest
  world-space dimension (self-intersection / non-manifold risk → FR-013, edge case).
- `scale > 0`.
- `mid_level` clamped to [0, 1].
- When `strategy == IMAGE` and `image is None` → operator reports `{'ERROR'}` and aborts.
- When `coord_mode == UV` and the object has no UV layer → warn and fall back to `LOCAL` (or
  auto-create a UV map for the image strategy).

## Entity: Preset (static registry, presets.py)

A named quick-start bundling a strategy + texture configuration + default control values. Not a
`PropertyGroup`; a plain Python dict/dataclass registry keyed by id.

| Field | Type | Notes |
|-------|------|-------|
| `id` | str | `wood` (designed), `brick`, `rock` (named). |
| `label` | str | UI display name. |
| `strategy` | enum | `PROCEDURAL` for wood/rock; `PROCEDURAL` or `IMAGE` for brick. |
| `texture_type` | str | `TEX_WOOD` (wood), `TEX_NOISE`/`TEX_VORONOI` (rock). |
| `defaults` | dict | strength_mm, scale, coord_mode, direction, mid_level overrides. |

**Wood preset (fully specified)**: `TEX_WOOD`, ring/band grain, strength 0.4 mm, scale 1.0,
coord `LOCAL`, direction `NORMAL`, mid_level 0.5, subdivision auto. **Brick/Rock**: named stubs
that follow the same shape; not required for the MVP slice.

## Entity: Target Object (existing bpy.types.Object, mesh)

The user's selected mesh receiving relief. The add-on does not subclass it; it attaches
`tdp_surface` (SurfaceSettings) and a modifier stack.

**Tracked lifecycle state** (derived, not a stored field — inferred from the modifier stack):

| State | Meaning | How detected |
|-------|---------|--------------|
| `none` | No relief setup | No add-on-created Displace modifier present. |
| `live` | Non-destructive setup present | Subsurf (Simple) + Displace modifiers present and un-applied. |
| `baked` | Relief realized into mesh | Modifiers applied; geometry is real, no add-on modifiers remain. |
| `exported` | STL written | Transient outcome of the export operator (not persisted on the object). |

**State transitions**:

```text
none --[Apply Texture]--> live
live --[adjust controls]--> live        (non-destructive, FR-007)
live --[Apply now / bake]--> baked      (explicit, FR-014)
live --[Export STL]--> exported         (geometry realized for the file only; object stays live)
baked --[Export STL]--> exported        (geometry already real)
live/baked --[Clear]--> none            (remove add-on modifiers + texture)
```

## Entity: Modifier Stack (managed, on Target Object)

The concrete Blender objects the add-on creates/updates. Ordering matters: Subsurf below Displace
so displacement runs on the densified mesh.

| Modifier | Type | Key properties set | Purpose |
|----------|------|--------------------|---------|
| `"3DP Subdivision"` | `SUBSURF` | `subdivision_type='SIMPLE'`, `levels` | Densify base mesh for fine relief. |
| `"3DP Displace"` | `DISPLACE` | `texture`, `texture_coords`, `strength`, `mid_level`, `direction` | Offset vertices from the texture. |

The add-on identifies *its* modifiers by name prefix (`3DP `) so re-applying updates the existing
stack rather than stacking duplicates (spec edge case "re-applying on an already-textured object").

## Entity: Generated Texture (managed Texture datablock)

| Field | Type | Notes |
|-------|------|-------|
| name | str | `"3DP <preset>"`, e.g. `3DP Wood`. |
| type | enum | `TEX_WOOD` / `TEX_NOISE` / `TEX_VORONOI` / `TEX_IMAGE`. |
| params | per-type | wood bands/rings + noise scale; image pointer for `TEX_IMAGE`. |

Created and owned by the add-on; referenced by the Displace modifier. Cleared when the user runs
**Clear**.

## Entity: Exported Model (STL file)

Not a runtime entity; the output artifact. Produced by `wm.stl_export(apply_modifiers=True)`; its
geometry must carry the relief shown in preview (FR-008/FR-009, SC-002). Covered by the export
contract and the round-trip headless test.

---

## Entity-to-spec mapping

| Spec § Key Entity | Implemented as |
|-------------------|----------------|
| Target object | `bpy.types.Object` + lifecycle state above |
| Texture selection | `SurfaceSettings.preset` / `strategy` / `texture` / `image` |
| Surface settings | `SurfaceSettings` fields (strength_mm, scale, coord_mode, direction, mid_level, subdiv) |
| Preset | `Preset` registry in `presets.py` |
| Exported model | STL file from the export operator |
