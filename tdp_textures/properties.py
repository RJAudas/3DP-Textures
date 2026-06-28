"""Shared user-adjustable settings for the Texture to Geometry add-on.

Defines the ``SurfaceSettings`` PropertyGroup stored per-object as
``Object.tdp_surface`` (see data-model.md). Live-update callbacks that refresh
the modifier stack are attached here (User Story 2).
"""

import bpy

from . import presets


# ---------------------------------------------------------------------------
# Enum item definitions
# ---------------------------------------------------------------------------

PRESET_ITEMS = [
    ('WOOD', "Wood", "Procedural wood grain relief"),
    ('BRICK', "Brick", "Brick / masonry relief"),
    ('ROCK', "Rock", "Rough rocky / stone relief"),
    ('CUSTOM', "Custom", "Use the controls below without a preset bundle"),
]

STRATEGY_ITEMS = [
    ('PROCEDURAL', "Procedural", "Drive relief from a procedural texture (no UVs required)"),
    ('IMAGE', "Image", "Drive relief from a supplied grayscale height-map image"),
]

COORD_ITEMS = [
    ('LOCAL', "Local", "Object-local texture coordinates (good for most shapes)"),
    ('GLOBAL', "Global", "World-space texture coordinates"),
    ('OBJECT', "Object", "Coordinates from another object"),
    ('UV', "UV", "UV map coordinates (required for image height-maps)"),
]

DIRECTION_ITEMS = [
    ('NORMAL', "Normal", "Displace along surface normals (wraps curved shapes)"),
    ('X', "X", "Displace along the X axis"),
    ('Y', "Y", "Displace along the Y axis"),
    ('Z', "Z", "Displace along the Z axis"),
    ('RGB_TO_XYZ', "RGB to XYZ", "Use texture RGB channels as an XYZ displacement"),
]

APPLY_MODE_ITEMS = [
    ('DEFER', "Defer to export", "Keep relief live and non-destructive; realize it only on export"),
    ('APPLY_NOW', "Apply now", "Bake the relief into permanent mesh geometry immediately"),
]


def _live_update(self, context):
    """Re-run the active strategy's ``update`` so edits preview live (US2)."""
    obj = getattr(context, "object", None)
    if obj is None or obj.type != 'MESH':
        return
    # Only refresh if a live setup already exists; never auto-build.
    from .engine import get_strategy, has_relief_setup

    if not has_relief_setup(obj):
        return
    strategy = get_strategy(self.strategy)
    if strategy is not None:
        try:
            strategy.update(obj, self)
        except Exception:  # pragma: no cover - defensive; never break the UI
            pass


def _on_preset_change(self, context):
    """Apply a preset's default control values when the preset changes."""
    preset = presets.get_preset(self.preset)
    if preset is not None:
        presets.apply_preset_defaults(preset, self)
    _live_update(self, context)


class SurfaceSettings(bpy.types.PropertyGroup):
    """Per-object relief configuration (see data-model.md § SurfaceSettings)."""

    preset: bpy.props.EnumProperty(
        name="Preset",
        description="Quick-start texture bundle",
        items=PRESET_ITEMS,
        default='WOOD',
        update=_on_preset_change,
    )
    strategy: bpy.props.EnumProperty(
        name="Strategy",
        description="Which engine drives the relief",
        items=STRATEGY_ITEMS,
        default='PROCEDURAL',
        update=_live_update,
    )
    texture: bpy.props.PointerProperty(
        name="Texture",
        description="Texture datablock referenced by the Displace modifier (managed by the add-on)",
        type=bpy.types.Texture,
    )
    image: bpy.props.PointerProperty(
        name="Height-map",
        description="Grayscale image driving relief when the Image strategy is selected",
        type=bpy.types.Image,
        update=_live_update,
    )
    strength_mm: bpy.props.FloatProperty(
        name="Strength (mm)",
        description="Relief depth in real-world millimetres (converted to scene units on apply)",
        default=0.4,
        min=0.0,
        soft_max=5.0,
        update=_live_update,
    )
    scale: bpy.props.FloatProperty(
        name="Scale",
        description="Pattern size / frequency of the texture",
        default=1.0,
        min=0.0001,
        soft_min=0.01,
        soft_max=100.0,
        update=_live_update,
    )
    coord_mode: bpy.props.EnumProperty(
        name="Coordinate Mode",
        description="How texture coordinates map onto the mesh",
        items=COORD_ITEMS,
        default='LOCAL',
        update=_live_update,
    )
    direction: bpy.props.EnumProperty(
        name="Direction",
        description="Direction the surface is displaced",
        items=DIRECTION_ITEMS,
        default='NORMAL',
        update=_live_update,
    )
    mid_level: bpy.props.FloatProperty(
        name="Mid-level",
        description="Texture value that produces no displacement",
        default=0.5,
        min=0.0,
        max=1.0,
        update=_live_update,
    )
    subdiv_auto: bpy.props.BoolProperty(
        name="Auto Subdivision",
        description="Automatically choose a subdivision level for fine, print-scale relief",
        default=True,
        update=_live_update,
    )
    subdiv_level: bpy.props.IntProperty(
        name="Subdivision Level",
        description="Simple subdivision level used when Auto Subdivision is off",
        default=3,
        min=1,
        max=6,
        update=_live_update,
    )
    apply_mode: bpy.props.EnumProperty(
        name="Apply Mode",
        description="Keep relief live (non-destructive) or bake it immediately",
        items=APPLY_MODE_ITEMS,
        default='DEFER',
    )


def register():
    bpy.utils.register_class(SurfaceSettings)
    bpy.types.Object.tdp_surface = bpy.props.PointerProperty(type=SurfaceSettings)


def unregister():
    if hasattr(bpy.types.Object, "tdp_surface"):
        del bpy.types.Object.tdp_surface
    bpy.utils.unregister_class(SurfaceSettings)
