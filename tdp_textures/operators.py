"""Operators (the add-on's command surface). See contracts/operators.md.

All operators live in the ``tdp`` namespace, guard with ``poll()``, register Undo
(``{'REGISTER','UNDO'}``), and report user-facing errors via ``self.report`` rather
than raising (Constitution Principles II & III).
"""

import bpy

from . import engine, validation


def _active_mesh(context):
    obj = context.active_object
    if obj is not None and obj.type == 'MESH':
        return obj
    return None


class TDP_OT_apply_texture(bpy.types.Operator):
    """Create or update the non-destructive relief setup on the active mesh"""

    bl_idname = "tdp.apply_texture"
    bl_label = "Apply Texture"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _active_mesh(context) is not None

    def execute(self, context):
        obj = _active_mesh(context)
        if obj is None:
            self.report({'ERROR'}, "Select a mesh object first")
            return {'CANCELLED'}

        settings = obj.tdp_surface
        strategy = engine.get_strategy(settings.strategy)
        if strategy is None:
            self.report({'ERROR'}, "Unknown relief strategy: %s" % settings.strategy)
            return {'CANCELLED'}

        try:
            strategy.build(obj, settings)
        except ValueError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        except Exception as exc:  # pragma: no cover - defensive
            self.report({'ERROR'}, "Failed to build relief: %s" % exc)
            return {'CANCELLED'}

        for message in validation.check_printability(obj, settings):
            self.report({'WARNING'}, message)

        self.report({'INFO'}, "Relief applied (live, non-destructive)")
        return {'FINISHED'}


class TDP_OT_bake(bpy.types.Operator):
    """Bake the live relief into permanent mesh geometry (Apply now)"""

    bl_idname = "tdp.bake"
    bl_label = "Apply Now"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = _active_mesh(context)
        return obj is not None and engine.has_relief_setup(obj)

    def execute(self, context):
        obj = _active_mesh(context)
        if obj is None or not engine.has_relief_setup(obj):
            self.report({'ERROR'}, "No live relief to bake")
            return {'CANCELLED'}

        # Apply in stack order: Subdivision first, then Displace.
        view_layer = context.view_layer
        prev_active = view_layer.objects.active
        view_layer.objects.active = obj

        for name in (engine.SUBSURF_NAME, engine.DISPLACE_NAME):
            if obj.modifiers.get(name) is not None:
                try:
                    bpy.ops.object.modifier_apply(modifier=name)
                except RuntimeError as exc:
                    view_layer.objects.active = prev_active
                    self.report({'ERROR'}, "Could not bake '%s': %s" % (name, exc))
                    return {'CANCELLED'}

        # Remove any remaining add-on modifiers (defensive).
        for mod in list(engine.owned_modifiers(obj)):
            obj.modifiers.remove(mod)

        view_layer.objects.active = prev_active
        mesh = obj.data
        self.report(
            {'INFO'},
            "Relief baked: %d vertices, %d faces" % (len(mesh.vertices), len(mesh.polygons)),
        )
        return {'FINISHED'}


class TDP_OT_clear(bpy.types.Operator):
    """Remove the add-on's relief setup, restoring the base mesh"""

    bl_idname = "tdp.clear"
    bl_label = "Clear"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = _active_mesh(context)
        if obj is None:
            return False
        settings = getattr(obj, "tdp_surface", None)
        has_tex = settings is not None and settings.texture is not None
        return bool(engine.owned_modifiers(obj)) or has_tex

    def execute(self, context):
        obj = _active_mesh(context)
        if obj is None:
            self.report({'ERROR'}, "Select a mesh object first")
            return {'CANCELLED'}
        engine.remove_relief_setup(obj)
        self.report({'INFO'}, "Relief cleared; base mesh restored")
        return {'FINISHED'}


class TDP_OT_export_stl(bpy.types.Operator):
    """Export the active object as an STL containing the relief"""

    bl_idname = "tdp.export_stl"
    bl_label = "Export STL"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    filter_glob: bpy.props.StringProperty(default="*.stl", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return _active_mesh(context) is not None

    def invoke(self, context, event):
        if not self.filepath:
            obj = _active_mesh(context)
            base = obj.name if obj is not None else "model"
            self.filepath = bpy.path.ensure_ext(base, ".stl")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = _active_mesh(context)
        if obj is None:
            self.report({'ERROR'}, "Select a mesh object first")
            return {'CANCELLED'}
        if not self.filepath:
            self.report({'ERROR'}, "No output path given")
            return {'CANCELLED'}

        filepath = bpy.path.ensure_ext(self.filepath, ".stl")

        # Pre-export printability advisory.
        settings = getattr(obj, "tdp_surface", None)
        if settings is not None:
            for message in validation.check_printability(obj, settings):
                self.report({'WARNING'}, message)

        # Select only the target, then restore selection afterwards.
        view_layer = context.view_layer
        prev_active = view_layer.objects.active
        prev_selected = [o for o in context.selected_objects]
        try:
            for o in prev_selected:
                o.select_set(False)
            obj.select_set(True)
            view_layer.objects.active = obj
            bpy.ops.wm.stl_export(
                filepath=filepath,
                export_selected_objects=True,
                apply_modifiers=True,
                global_scale=1.0,
                use_scene_unit=True,
            )
        except RuntimeError as exc:
            self.report({'ERROR'}, "STL export failed: %s" % exc)
            return {'CANCELLED'}
        finally:
            obj.select_set(False)
            for o in prev_selected:
                try:
                    o.select_set(True)
                except ReferenceError:
                    pass
            view_layer.objects.active = prev_active

        self.report({'INFO'}, "Exported STL: %s" % filepath)
        return {'FINISHED'}


_CLASSES = (
    TDP_OT_apply_texture,
    TDP_OT_bake,
    TDP_OT_clear,
    TDP_OT_export_stl,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
