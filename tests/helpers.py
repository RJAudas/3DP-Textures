"""Shared headless-test helpers.

Provides add-on (un)registration, deterministic test-mesh construction, evaluated-
mesh inspection, and integrity assertions used by the headless suite (Principle V).
"""

import importlib
import os
import sys
import tempfile

import bpy
import mathutils

ADDON_NAME = "tdp_textures"
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_addon():
    """Import (once) and return the add-on package."""
    if _REPO_ROOT not in sys.path:
        sys.path.insert(0, _REPO_ROOT)
    return importlib.import_module(ADDON_NAME)


def register_addon():
    get_addon().register()


def unregister_addon():
    get_addon().unregister()


class addon_registered:
    """Context manager that registers the add-on for the duration of a test."""

    def __enter__(self):
        register_addon()
        return get_addon()

    def __exit__(self, exc_type, exc, tb):
        unregister_addon()
        return False


# ---------------------------------------------------------------------------
# Scene / mesh construction
# ---------------------------------------------------------------------------

def reset_scene():
    """Remove all objects from the current scene for an isolated test."""
    if bpy.context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError:
            pass
    if bpy.context.scene.objects:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
    for block in list(bpy.data.meshes):
        if block.users == 0:
            bpy.data.meshes.remove(block)


def build_test_mesh(kind='CYLINDER', size_m=0.02):
    """Create a small (print-scale) primitive and return the active object.

    ``size_m`` is the characteristic dimension in metres (default 20 mm) so the
    auto subdivision level and default relief depth stay print-realistic and fast.
    """
    radius = size_m * 0.25
    # Force a deterministic unit scale (1 BU = 1 m) so tests are independent of the
    # user's startup-file unit settings.
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0
    if kind == 'CYLINDER':
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=size_m, vertices=32)
    elif kind == 'PLANE':
        bpy.ops.mesh.primitive_plane_add(size=size_m)
    elif kind == 'SPHERE':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=24, ring_count=16)
    else:
        raise ValueError("Unknown mesh kind: %s" % kind)
    obj = bpy.context.active_object
    bpy.context.view_layer.objects.active = obj
    return obj


# ---------------------------------------------------------------------------
# Evaluated-mesh inspection
# ---------------------------------------------------------------------------

def evaluated_coords(obj):
    """Return the evaluated (modified) world-space vertex coordinates."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    mw = eval_obj.matrix_world
    coords = [mw @ v.co for v in mesh.vertices]
    eval_obj.to_mesh_clear()
    return coords


def bounds(coords):
    """Return (min_vec, max_vec) of a list of vectors."""
    xs = [c.x for c in coords]
    ys = [c.y for c in coords]
    zs = [c.z for c in coords]
    return (
        mathutils.Vector((min(xs), min(ys), min(zs))),
        mathutils.Vector((max(xs), max(ys), max(zs))),
    )


def evaluated_face_areas(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    areas = [p.area for p in mesh.polygons]
    eval_obj.to_mesh_clear()
    return areas


# ---------------------------------------------------------------------------
# Integrity assertions
# ---------------------------------------------------------------------------

def assert_changed(before, after, tol=1e-6):
    """Assert that the two coordinate sets differ beyond ``tol`` somewhere."""
    assert len(before) == len(after), "vertex count changed unexpectedly"
    max_delta = max((a - b).length for a, b in zip(before, after))
    assert max_delta > tol, "evaluated mesh did not change (max delta %g <= tol %g)" % (
        max_delta, tol)
    return max_delta


def assert_no_nan(coords):
    for c in coords:
        for component in c:
            assert component == component, "NaN coordinate found"  # NaN != NaN
            assert abs(component) != float("inf"), "infinite coordinate found"


def assert_no_zero_area_faces(areas, tol=1e-12):
    bad = [a for a in areas if a <= tol]
    assert not bad, "%d zero-area face(s) found" % len(bad)


def temp_stl_path():
    fd, path = tempfile.mkstemp(suffix=".stl")
    os.close(fd)
    os.remove(path)  # we only want the path; exporter will create the file
    return path


def read_stl_vertices(path):
    """Parse an STL file (ASCII or binary) and return a flat list of vertices."""
    import struct

    with open(path, "rb") as fh:
        head = fh.read(5)
        fh.seek(0)
        if head == b"solid":
            data = fh.read()
            try:
                text = data.decode("ascii", "ignore")
            except Exception:
                text = ""
            if "facet" in text:
                verts = []
                for line in text.splitlines():
                    line = line.strip()
                    if line.startswith("vertex"):
                        _, x, y, z = line.split()
                        verts.append(mathutils.Vector((float(x), float(y), float(z))))
                if verts:
                    return verts
            fh.seek(0)
        # Binary STL.
        fh.seek(80)
        count_bytes = fh.read(4)
        (tri_count,) = struct.unpack("<I", count_bytes)
        verts = []
        for _ in range(tri_count):
            fh.read(12)  # normal
            for _v in range(3):
                x, y, z = struct.unpack("<3f", fh.read(12))
                verts.append(mathutils.Vector((x, y, z)))
            fh.read(2)  # attribute byte count
        return verts
