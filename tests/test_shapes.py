"""T027 (US3): the procedural Wood workflow produces relief on flat and curved shapes."""

import bpy

import helpers


def _apply_and_check(kind, size_m):
    helpers.reset_scene()
    obj = helpers.build_test_mesh(kind, size_m=size_m)
    obj.tdp_surface.preset = 'WOOD'
    obj.tdp_surface.direction = 'NORMAL'

    base_coords = helpers.evaluated_coords(obj)
    base_min, base_max = helpers.bounds(base_coords)

    assert bpy.ops.tdp.apply_texture() == {'FINISHED'}, "apply failed on %s" % kind

    eval_coords = helpers.evaluated_coords(obj)
    helpers.assert_no_nan(eval_coords)
    ev_min, ev_max = helpers.bounds(eval_coords)
    delta = max((ev_min - base_min).length, (ev_max - base_max).length)
    assert delta > 1e-6, "no relief on %s (delta %g)" % (kind, delta)
    helpers.assert_no_zero_area_faces(helpers.evaluated_face_areas(obj))


def test_relief_on_flat_plane():
    with helpers.addon_registered():
        _apply_and_check('PLANE', size_m=0.05)


def test_relief_on_sphere():
    with helpers.addon_registered():
        _apply_and_check('SPHERE', size_m=0.04)
