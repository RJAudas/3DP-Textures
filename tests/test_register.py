"""T011: register/unregister leaves no residue (Constitution Principle II)."""

import bpy

import helpers


def _addon_artifacts_present():
    has_pointer = hasattr(bpy.types.Object, "tdp_surface")
    has_panel = hasattr(bpy.types, "VIEW3D_PT_texture_to_geometry")
    has_op = hasattr(bpy.types, "TDP_OT_apply_texture")
    return has_pointer, has_panel, has_op


def test_enable_disable_reenable_no_residue():
    # Ensure a clean baseline.
    helpers.get_addon()
    p, panel, op = _addon_artifacts_present()
    assert not p and not panel and not op, "add-on artifacts present before register"

    helpers.register_addon()
    p, panel, op = _addon_artifacts_present()
    assert p, "Object.tdp_surface missing after register"
    assert panel, "panel class missing after register"
    assert op, "apply_texture operator missing after register"

    helpers.unregister_addon()
    p, panel, op = _addon_artifacts_present()
    assert not p, "Object.tdp_surface left behind after unregister"
    assert not panel, "panel class left behind after unregister"
    assert not op, "operator left behind after unregister"

    # Re-enable must work cleanly a second time.
    helpers.register_addon()
    p, panel, op = _addon_artifacts_present()
    assert p and panel and op, "re-register did not restore artifacts"
    helpers.unregister_addon()
    p, panel, op = _addon_artifacts_present()
    assert not p and not panel and not op, "residue after final unregister"
