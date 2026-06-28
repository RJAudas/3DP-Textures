"""T026 (US3): image / height-map strategy displaces; missing image is an error."""

import bpy

import helpers


def _make_heightmap(name="tdp_test_hmap", size=32):
    img = bpy.data.images.new(name, width=size, height=size)
    pixels = []
    for y in range(size):
        for x in range(size):
            # Radial gradient height-map -> clear variation across the surface.
            cx, cy = x - size / 2.0, y - size / 2.0
            v = (cx * cx + cy * cy) ** 0.5 / (size / 2.0)
            v = min(1.0, v)
            pixels.extend((v, v, v, 1.0))
    img.pixels = pixels
    img.update()
    return img


def _ensure_uv(obj):
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")


def test_image_strategy_displaces():
    with helpers.addon_registered():
        helpers.reset_scene()
        obj = helpers.build_test_mesh('PLANE', size_m=0.05)
        _ensure_uv(obj)
        settings = obj.tdp_surface
        settings.strategy = 'IMAGE'
        settings.coord_mode = 'UV'
        settings.image = _make_heightmap()
        settings.subdiv_auto = False
        settings.subdiv_level = 4

        base_coords = helpers.evaluated_coords(obj)
        base_min, base_max = helpers.bounds(base_coords)

        assert bpy.ops.tdp.apply_texture() == {'FINISHED'}

        eval_coords = helpers.evaluated_coords(obj)
        helpers.assert_no_nan(eval_coords)
        ev_min, ev_max = helpers.bounds(eval_coords)
        delta = max((ev_min - base_min).length, (ev_max - base_max).length)
        assert delta > 1e-6, "image height-map did not displace the mesh (delta %g)" % delta


def test_missing_image_reports_error():
    with helpers.addon_registered():
        helpers.reset_scene()
        obj = helpers.build_test_mesh('PLANE', size_m=0.05)
        settings = obj.tdp_surface
        settings.strategy = 'IMAGE'
        settings.image = None

        # The operator reports {'ERROR'} and returns {'CANCELLED'}; Blender surfaces a
        # reported ERROR from a script-invoked operator as a RuntimeError.
        raised = False
        try:
            result = bpy.ops.tdp.apply_texture()
            assert result == {'CANCELLED'}, "missing image should cancel, got %s" % result
        except RuntimeError as exc:
            raised = True
            assert "image" in str(exc).lower(), "unexpected error message: %s" % exc

        from importlib import import_module
        engine = import_module("tdp_textures.engine")
        assert raised or not engine.has_relief_setup(obj), \
            "missing image must not build a relief setup"
