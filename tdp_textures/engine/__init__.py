"""Strategy interface and registry (Constitution Principle IV).

All relief generators implement the same ``Strategy`` contract and register
themselves by key (matching ``SurfaceSettings.strategy``). Operators dispatch
through :func:`get_strategy`; nothing else needs to know which strategy is active.
"""

# Names the add-on uses for the modifiers and texture datablocks it owns. The
# add-on identifies *its* objects by the "3DP " prefix so re-applying updates the
# existing setup rather than stacking duplicates.
MOD_PREFIX = "3DP "
SUBSURF_NAME = "3DP Subdivision"
DISPLACE_NAME = "3DP Displace"


class Strategy:
    """Common interface for relief-building strategies.

    Subclasses configure the managed Subsurf + Displace modifier stack and the
    owned ``Texture`` datablock on the target object.
    """

    key = None  # matches SurfaceSettings.strategy, e.g. 'PROCEDURAL'

    def build(self, obj, settings):
        """Create (or update) the relief setup on ``obj``. Idempotent."""
        raise NotImplementedError

    def update(self, obj, settings):
        """Refresh an existing live setup to match ``settings`` (live preview)."""
        # Default: re-run build (idempotent).
        self.build(obj, settings)

    def teardown(self, obj):
        """Remove this add-on's modifiers and owned texture from ``obj``."""
        remove_relief_setup(obj)


_REGISTRY = {}


def register_strategy(strategy):
    _REGISTRY[strategy.key] = strategy


def get_strategy(key):
    return _REGISTRY.get(key)


def all_strategies():
    return dict(_REGISTRY)


# ---------------------------------------------------------------------------
# Shared modifier-stack helpers (used by strategies and operators)
# ---------------------------------------------------------------------------

def owned_modifiers(obj):
    """Return the add-on-owned modifiers on ``obj`` (by name prefix)."""
    return [m for m in obj.modifiers if m.name.startswith(MOD_PREFIX)]


def has_relief_setup(obj):
    """True when ``obj`` carries this add-on's live relief modifiers."""
    return any(m.name == DISPLACE_NAME for m in obj.modifiers)


def ensure_modifier(obj, name, mod_type):
    """Return the named modifier on ``obj``, creating it if absent."""
    mod = obj.modifiers.get(name)
    if mod is None or mod.type != mod_type:
        if mod is not None:
            obj.modifiers.remove(mod)
        mod = obj.modifiers.new(name=name, type=mod_type)
    return mod


def scene_scale_length(scene=None):
    """Return the scene's unit scale-length (metres per Blender unit)."""
    import bpy

    if scene is None:
        scene = getattr(bpy.context, "scene", None)
    if scene is not None and getattr(scene, "unit_settings", None) is not None:
        return scene.unit_settings.scale_length or 1.0
    return 1.0


def mm_to_bu(value_mm, scene=None):
    """Convert a real-world millimetre length into Blender units for the scene."""
    return (value_mm / 1000.0) / scene_scale_length(scene)


def configure_stack(obj, settings, texture):
    """Create/update the Subsurf (Simple) + Displace stack from ``settings``.

    Subsurf is ensured first so it sits above (evaluates before) Displace, so the
    displacement runs on the densified mesh. Idempotent.
    """
    from ..subdivision import compute_subdiv_level

    subsurf = ensure_modifier(obj, SUBSURF_NAME, 'SUBSURF')
    subsurf.subdivision_type = 'SIMPLE'
    if settings.subdiv_auto:
        import bpy
        scene = getattr(bpy.context, "scene", None)
        level = compute_subdiv_level(obj, scene)
    else:
        level = settings.subdiv_level
    subsurf.levels = level
    subsurf.render_levels = level

    displace = ensure_modifier(obj, DISPLACE_NAME, 'DISPLACE')
    displace.texture = texture
    displace.texture_coords = settings.coord_mode
    displace.strength = mm_to_bu(settings.strength_mm)
    displace.mid_level = settings.mid_level
    displace.direction = settings.direction
    if settings.coord_mode == 'UV':
        uv_layers = getattr(obj.data, "uv_layers", None)
        if uv_layers and len(uv_layers) > 0:
            displace.uv_layer = uv_layers.active.name

    _ensure_order(obj, SUBSURF_NAME, DISPLACE_NAME)
    return subsurf, displace


def _ensure_order(obj, first_name, second_name):
    """Best-effort: make sure ``first_name`` sits above ``second_name``."""
    mods = obj.modifiers
    first = mods.get(first_name)
    second = mods.get(second_name)
    if first is None or second is None:
        return
    if list(mods).index(first) < list(mods).index(second):
        return
    try:
        import bpy
        target = list(mods).index(second)
        bpy.ops.object.modifier_move_to_index(modifier=first_name, index=target)
    except Exception:  # pragma: no cover - non-fatal ordering best-effort
        pass


def ensure_texture(settings, tex_type, label):
    """Return the add-on-owned Texture datablock, (re)creating it if needed."""
    import bpy

    tex = settings.texture
    desired_name = MOD_PREFIX + label
    if tex is None or tex.type != tex_type or not tex.name.startswith(MOD_PREFIX):
        tex = bpy.data.textures.new(name=desired_name, type=tex_type)
        settings.texture = tex
    return tex


def remove_relief_setup(obj):
    """Remove the add-on's modifiers and its owned texture datablock."""
    import bpy

    settings = getattr(obj, "tdp_surface", None)
    for mod in list(owned_modifiers(obj)):
        obj.modifiers.remove(mod)

    if settings is not None and settings.texture is not None:
        tex = settings.texture
        settings.texture = None
        # Only free the texture if it is our managed one and now unused.
        if tex.name.startswith(MOD_PREFIX) and tex.users == 0:
            try:
                bpy.data.textures.remove(tex)
            except (RuntimeError, ReferenceError):
                pass


def register():
    """Populate the strategy registry with the available strategies."""
    _REGISTRY.clear()
    from . import displace_procedural  # noqa: F401  (registers itself)
    from . import displace_image  # noqa: F401  (registers itself)

    register_strategy(displace_procedural.ProceduralStrategy())
    register_strategy(displace_image.ImageStrategy())


def unregister():
    _REGISTRY.clear()
