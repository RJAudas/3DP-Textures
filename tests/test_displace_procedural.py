"""T012 (US1): procedural Wood relief changes the evaluated mesh; integrity checks."""

import bpy

import helpers


def test_wood_displaces_evaluated_mesh():
    with helpers.addon_registered():
        helpers.reset_scene()
        obj = helpers.build_test_mesh('CYLINDER', size_m=0.02)
        settings = obj.tdp_surface
        settings.preset = 'WOOD'

        base_coords = helpers.evaluated_coords(obj)
        base_min, base_max = helpers.bounds(base_coords)

        result = bpy.ops.tdp.apply_texture()
        assert result == {'FINISHED'}, "apply_texture returned %s" % result

        # Modifier stack present and live.
        from importlib import import_module
        engine = import_module("tdp_textures.engine")
        assert engine.has_relief_setup(obj), "no live relief setup after apply"

        eval_coords = helpers.evaluated_coords(obj)
        helpers.assert_no_nan(eval_coords)

        # Subdivision densified the evaluated mesh.
        assert len(eval_coords) > len(base_coords), "evaluated mesh was not subdivided"

        # Displacement shifted the bounds beyond tolerance (relief is real geometry).
        ev_min, ev_max = helpers.bounds(eval_coords)
        delta = max((ev_min - base_min).length, (ev_max - base_max).length)
        assert delta > 1e-6, "evaluated bounds unchanged (delta %g)" % delta

        areas = helpers.evaluated_face_areas(obj)
        helpers.assert_no_zero_area_faces(areas)
