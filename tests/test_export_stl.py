"""T013 (US1): exported STL carries relief absent from the undisplaced base (SC-002)."""

import os

import bpy

import helpers


def test_export_stl_contains_relief():
    with helpers.addon_registered():
        helpers.reset_scene()
        obj = helpers.build_test_mesh('CYLINDER', size_m=0.02)
        settings = obj.tdp_surface
        settings.preset = 'WOOD'

        # Export the displaced relief.
        assert bpy.ops.tdp.apply_texture() == {'FINISHED'}
        relief_path = helpers.temp_stl_path()
        assert bpy.ops.tdp.export_stl(filepath=relief_path) == {'FINISHED'}
        assert os.path.exists(relief_path), "relief STL was not written"
        assert os.path.getsize(relief_path) > 0, "relief STL is empty"
        relief_verts = helpers.read_stl_vertices(relief_path)
        assert relief_verts, "no triangles parsed from relief STL"

        # Export the undisplaced base for comparison.
        assert bpy.ops.tdp.clear() == {'FINISHED'}
        base_path = helpers.temp_stl_path()
        assert bpy.ops.tdp.export_stl(filepath=base_path) == {'FINISHED'}
        base_verts = helpers.read_stl_vertices(base_path)
        assert base_verts, "no triangles parsed from base STL"

        relief_b = helpers.bounds(relief_verts)
        base_b = helpers.bounds(base_verts)
        delta = max(
            (relief_b[0] - base_b[0]).length,
            (relief_b[1] - base_b[1]).length,
        )
        assert delta > 1e-6, "exported relief geometry matches the flat base (delta %g)" % delta

        for path in (relief_path, base_path):
            try:
                os.remove(path)
            except OSError:
                pass
