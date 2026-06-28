"""Printability warnings (research.md Decision 8; FR-013).

Pure helpers that inspect an object + settings and return human-readable warning
strings. The add-on guides (via ``self.report({'WARNING'})``) but never auto-repairs.
"""

import mathutils


def _world_bbox_dims(obj):
    mw = obj.matrix_world
    corners = [mw @ mathutils.Vector(c).to_4d() for c in obj.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    return (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def check_printability(obj, settings):
    """Return a list of non-blocking printability warning messages."""
    warnings = []

    scale_length = 1.0
    try:
        import bpy
        scene = bpy.context.scene
        if scene is not None and scene.unit_settings is not None:
            scale_length = scene.unit_settings.scale_length or 1.0
    except Exception:
        pass

    dims = _world_bbox_dims(obj)  # Blender units
    dims_mm = [d * scale_length * 1000.0 for d in dims]
    positive = [d for d in dims_mm if d > 0]
    smallest_mm = min(positive) if positive else 0.0

    # Strength large vs. the smallest dimension -> self-intersection / non-manifold.
    if smallest_mm > 0 and settings.strength_mm > 0.1 * smallest_mm:
        warnings.append(
            "Strength is large relative to the object's smallest dimension; relief "
            "may self-intersect (non-manifold). Validate with the 3D-Print Toolbox."
        )

    # UV coordinates requested but no UV layer present.
    uv_layers = getattr(obj.data, "uv_layers", None)
    if settings.coord_mode == 'UV' and not (uv_layers and len(uv_layers) > 0):
        warnings.append(
            "UV coordinate mode selected but the mesh has no UV map; falling back. "
            "Add a UV map or use Local/Global coordinates."
        )

    # Detail finer than a typical 0.4 mm nozzle.
    if 0 < settings.strength_mm < 0.2:
        warnings.append(
            "Relief depth is finer than a typical 0.4 mm nozzle and may not print "
            "with visible detail."
        )

    return warnings
