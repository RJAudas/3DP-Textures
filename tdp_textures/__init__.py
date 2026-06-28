"""Texture to Geometry (3D-Print Textures) -- Blender add-on entry point.

Turns a surface texture into real, printable mesh relief via a Subsurf (Simple) +
Displace modifier stack behind a 3D-Viewport N-panel. register()/unregister() wire
every submodule symmetrically and idempotently (Constitution Principle II).
"""

from . import presets
from . import properties
from . import engine
from . import operators
from . import ui

# Registration order. unregister() runs in reverse for symmetric teardown.
_MODULES = (
    presets,
    properties,
    engine,
    operators,
    ui,
)


def register():
    for module in _MODULES:
        module.register()


def unregister():
    for module in reversed(_MODULES):
        module.unregister()
