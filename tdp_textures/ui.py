"""3D-Viewport N-panel UI: "Texture to Geometry" (contracts/operators.md § Panel)."""

import bpy

from . import engine


class VIEW3D_PT_texture_to_geometry(bpy.types.Panel):
    bl_label = "Texture to Geometry"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Texture \u2192 Geometry"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj is None or obj.type != 'MESH':
            box = layout.box()
            box.label(text="Select a mesh object", icon='INFO')
            box.label(text="to add printable relief.")
            return

        settings = obj.tdp_surface
        is_live = engine.has_relief_setup(obj)

        # --- Primary controls -------------------------------------------------
        col = layout.column(align=True)
        col.prop(settings, "preset")
        col.prop(settings, "strength_mm")
        col.prop(settings, "scale")

        # --- Image source (Image strategy) -----------------------------------
        if settings.strategy == 'IMAGE':
            img_box = layout.box()
            img_box.label(text="Height-map", icon='IMAGE_DATA')
            img_box.template_ID(settings, "image", new="image.new", open="image.open")
            uv_layers = getattr(obj.data, "uv_layers", None)
            if not (uv_layers and len(uv_layers) > 0):
                img_box.label(text="No UV map: relief may distort on curves", icon='ERROR')

        # --- Advanced ---------------------------------------------------------
        header, panel = layout.panel("tdp_advanced", default_closed=True)
        header.label(text="Advanced")
        if panel is not None:
            panel.prop(settings, "strategy")
            panel.prop(settings, "coord_mode")
            panel.prop(settings, "direction")
            panel.prop(settings, "mid_level")
            sub = panel.column(align=True)
            sub.prop(settings, "subdiv_auto")
            row = sub.row()
            row.enabled = not settings.subdiv_auto
            row.prop(settings, "subdiv_level")

        # --- Mode + actions ---------------------------------------------------
        layout.prop(settings, "apply_mode")

        actions = layout.column(align=True)
        actions.operator("tdp.apply_texture", icon='MOD_DISPLACE')
        row = actions.row(align=True)
        row.enabled = is_live
        row.operator("tdp.bake", icon='CHECKMARK')
        row.operator("tdp.clear", icon='X')

        layout.separator()
        layout.operator("tdp.export_stl", icon='EXPORT')


_CLASSES = (
    VIEW3D_PT_texture_to_geometry,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
