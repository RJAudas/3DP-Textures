"""Strategy A1 (primary): procedural Texture + Displace + Subsurf.

Builds relief from a procedural ``Texture`` datablock (wood/noise/voronoi) driving
a Displace modifier over a Simple-subdivided mesh. No UV unwrap required; Normal
displacement wraps cleanly around curved shapes (research.md Decision 1).
"""

from . import Strategy, configure_stack, ensure_texture
from .. import presets

# Map preset texture-type ids to Blender Texture.type enum values.
_TEX_TYPE_MAP = {
    'WOOD': 'WOOD',
    'NOISE': 'NOISE',
    'VORONOI': 'VORONOI',
    'MUSGRAVE': 'MUSGRAVE',
    'CLOUDS': 'CLOUDS',
}


def _resolve_texture_type(settings):
    preset = presets.get_preset(settings.preset)
    if preset is not None and preset.strategy == 'PROCEDURAL':
        return _TEX_TYPE_MAP.get(preset.texture_type, 'WOOD')
    return 'WOOD'


def _configure_texture(tex, settings):
    """Apply control values onto the procedural texture datablock."""
    if hasattr(tex, "noise_scale"):
        tex.noise_scale = max(0.0001, 0.25 * settings.scale)
    # Wood: bands give clear directional grain relief.
    if tex.type == 'WOOD':
        tex.wood_type = 'BANDNOISE'
        tex.noise_basis_2 = 'SIN'
        if hasattr(tex, "turbulence"):
            tex.turbulence = 5.0
    elif tex.type == 'VORONOI':
        if hasattr(tex, "distance_metric"):
            tex.distance_metric = 'DISTANCE'


class ProceduralStrategy(Strategy):
    key = 'PROCEDURAL'

    def build(self, obj, settings):
        tex_type = _resolve_texture_type(settings)
        preset = presets.get_preset(settings.preset)
        label = preset.label if preset is not None else "Procedural"
        tex = ensure_texture(settings, tex_type, label)
        _configure_texture(tex, settings)
        configure_stack(obj, settings, tex)
