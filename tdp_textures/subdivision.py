"""Automatic Simple-subdivision level calculation (research.md Decision 7).

Picks a Subsurf (Simple) level so the post-subdivision edge length targets the
print-detail range (~0.2-0.5 mm), derived from the object's world-space size.
"""

import math

# Target post-subdivision edge length, in millimetres (print-detail range).
TARGET_EDGE_MM = 0.35

# Clamp range for the computed level (data-model: subdiv_level 1-6).
MIN_LEVEL = 1
MAX_LEVEL = 6


def _world_bbox_dims(obj):
    """Return the (x, y, z) world-space bounding-box dimensions of ``obj``."""
    corners = [obj.matrix_world @ corner.to_4d() for corner in
               (_v(c) for c in obj.bound_box)]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    return (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def _v(corner):
    import mathutils
    return mathutils.Vector(corner)


def _estimate_base_edge(obj):
    """Estimate a representative base-mesh edge length in world units."""
    mesh = obj.data
    if not getattr(mesh, "edges", None) or len(mesh.edges) == 0:
        # Fall back to the largest bbox dimension.
        return max(_world_bbox_dims(obj)) or 1.0

    mw = obj.matrix_world
    total = 0.0
    count = 0
    # Sample up to 64 edges for speed on dense meshes.
    step = max(1, len(mesh.edges) // 64)
    for i in range(0, len(mesh.edges), step):
        e = mesh.edges[i]
        v0 = mw @ mesh.vertices[e.vertices[0]].co
        v1 = mw @ mesh.vertices[e.vertices[1]].co
        total += (v1 - v0).length
        count += 1
    return (total / count) if count else 1.0


def compute_subdiv_level(obj, scene=None):
    """Compute a Simple subdivision level targeting print-scale relief detail.

    Each Simple-subdivision level halves edge length, so the required number of
    levels is ``log2(base_edge / target_edge)``, clamped to [MIN_LEVEL, MAX_LEVEL].
    """
    base_edge = _estimate_base_edge(obj)
    if base_edge <= 0:
        return MIN_LEVEL

    scale_length = 1.0
    if scene is not None and getattr(scene, "unit_settings", None) is not None:
        scale_length = scene.unit_settings.scale_length or 1.0

    # Convert the mm target into Blender units (base_edge is in BU).
    target_bu = (TARGET_EDGE_MM / 1000.0) / scale_length
    if target_bu <= 0:
        return MAX_LEVEL

    ratio = base_edge / target_bu
    if ratio <= 1.0:
        return MIN_LEVEL

    level = math.ceil(math.log2(ratio))
    return max(MIN_LEVEL, min(MAX_LEVEL, level))
