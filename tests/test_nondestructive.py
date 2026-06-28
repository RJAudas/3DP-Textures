"""T019 (US2): non-destructive apply/clear and explicit bake (SC-006, FR-014)."""

import bpy

import helpers


def test_apply_then_clear_recovers_base_mesh():
    with helpers.addon_registered():
        helpers.reset_scene()
        obj = helpers.build_test_mesh('CYLINDER', size_m=0.02)
        settings = obj.tdp_surface
        settings.preset = 'WOOD'

        base_count = len(obj.data.vertices)
        base_positions = [v.co.copy() for v in obj.data.vertices]

        assert bpy.ops.tdp.apply_texture() == {'FINISHED'}

        # The base mesh data must be untouched (relief is live/non-destructive).
        assert len(obj.data.vertices) == base_count, "base mesh vertex count changed on apply"
        for v, p in zip(obj.data.vertices, base_positions):
            assert (v.co - p).length < 1e-9, "base mesh vertex moved on apply"

        assert bpy.ops.tdp.clear() == {'FINISHED'}

        from importlib import import_module
        engine = import_module("tdp_textures.engine")
        assert not engine.owned_modifiers(obj), "add-on modifiers remain after clear"
        assert len(obj.data.vertices) == base_count, "base mesh changed after clear"
        for v, p in zip(obj.data.vertices, base_positions):
            assert (v.co - p).length < 1e-9, "base mesh vertex moved after clear"


def test_bake_realizes_geometry_and_removes_modifiers():
    with helpers.addon_registered():
        helpers.reset_scene()
        obj = helpers.build_test_mesh('CYLINDER', size_m=0.02)
        obj.tdp_surface.preset = 'WOOD'

        base_count = len(obj.data.vertices)
        assert bpy.ops.tdp.apply_texture() == {'FINISHED'}
        assert bpy.ops.tdp.bake() == {'FINISHED'}

        from importlib import import_module
        engine = import_module("tdp_textures.engine")
        assert not engine.owned_modifiers(obj), "modifiers remain after bake"
        # Geometry was realized into the real mesh.
        assert len(obj.data.vertices) > base_count, "bake did not realize subdivided geometry"
