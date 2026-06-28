"""Strategy A2 (fallback): image / height-map + Displace.

Wraps a user-supplied ``Image`` in a ``TEX_IMAGE`` texture and drives Displace via
UV (or Generated) coordinates. Reproduces a specific real-world surface; warns
about UV seams/stretching on curved shapes (research.md Decision 2).
"""

from . import Strategy, configure_stack, ensure_texture


class MissingImageError(ValueError):
    """Raised when the Image strategy is used without a height-map image."""


class ImageStrategy(Strategy):
    key = 'IMAGE'

    def build(self, obj, settings):
        if settings.image is None:
            raise MissingImageError("No height-map image set for the Image strategy")

        tex = ensure_texture(settings, 'IMAGE', "Image")
        tex.image = settings.image

        # Image textures need 2D coordinates; prefer UV, fall back to Generated.
        coord = settings.coord_mode
        uv_layers = getattr(obj.data, "uv_layers", None)
        if coord == 'UV' and not (uv_layers and len(uv_layers) > 0):
            settings.coord_mode = 'GLOBAL'
        elif coord in {'LOCAL', 'OBJECT'}:
            # LOCAL/OBJECT are 3D; for a flat height-map use Global generated coords
            # unless the mesh actually has UVs the user picked.
            if uv_layers and len(uv_layers) > 0:
                settings.coord_mode = 'UV'

        configure_stack(obj, settings, tex)
