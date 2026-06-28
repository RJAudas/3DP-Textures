"""Preset registry: named quick-start texture bundles (see data-model.md).

A preset is a plain Python record (not a PropertyGroup) bundling a strategy, a
procedural texture type, and default control values. ``wood`` is fully designed;
``brick`` and ``rock`` are completed in User Story 3.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Preset:
    """A named relief quick-start."""

    id: str
    label: str
    strategy: str  # 'PROCEDURAL' | 'IMAGE'
    texture_type: str  # e.g. 'WOOD', 'NOISE', 'VORONOI', 'IMAGE'
    defaults: dict = field(default_factory=dict)


# Registry keyed by the SurfaceSettings.preset enum value (upper-case id).
_REGISTRY = {}


def register_preset(preset):
    _REGISTRY[preset.id] = preset


def get_preset(preset_id):
    return _REGISTRY.get(preset_id)


def all_presets():
    return dict(_REGISTRY)


def apply_preset_defaults(preset, settings):
    """Write a preset's strategy + default control values onto SurfaceSettings."""
    settings.strategy = preset.strategy
    for key, value in preset.defaults.items():
        if hasattr(settings, key):
            setattr(settings, key, value)


def _build_registry():
    _REGISTRY.clear()

    # Wood -- fully specified MVP preset.
    register_preset(Preset(
        id='WOOD',
        label="Wood",
        strategy='PROCEDURAL',
        texture_type='WOOD',
        defaults={
            'strength_mm': 0.4,
            'scale': 1.0,
            'coord_mode': 'LOCAL',
            'direction': 'NORMAL',
            'mid_level': 0.5,
        },
    ))

    # Brick -- procedural masonry relief (completed in US3).
    register_preset(Preset(
        id='BRICK',
        label="Brick",
        strategy='PROCEDURAL',
        texture_type='VORONOI',
        defaults={
            'strength_mm': 0.6,
            'scale': 2.0,
            'coord_mode': 'LOCAL',
            'direction': 'NORMAL',
            'mid_level': 0.4,
        },
    ))

    # Rock -- rough stone relief (completed in US3).
    register_preset(Preset(
        id='ROCK',
        label="Rock",
        strategy='PROCEDURAL',
        texture_type='NOISE',
        defaults={
            'strength_mm': 0.5,
            'scale': 1.5,
            'coord_mode': 'LOCAL',
            'direction': 'NORMAL',
            'mid_level': 0.5,
        },
    ))


def register():
    _build_registry()


def unregister():
    _REGISTRY.clear()
