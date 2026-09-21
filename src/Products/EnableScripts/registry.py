"""Explicit integration descriptions; never auto-grant discovered packages."""

from dataclasses import dataclass, field
from importlib import import_module, metadata


@dataclass(frozen=True)
class Feature:
    key: str
    title: str
    description: str
    modules: dict = field(default_factory=dict)
    classes: dict = field(default_factory=dict)
    types: dict = field(default_factory=dict)
    distributions: tuple = ()
    requires: tuple = ()
    exports: dict = field(default_factory=dict)


FEATURES = {}


def register(feature):
    if not isinstance(feature, Feature) or feature.key in FEATURES:
        raise ValueError("Expected a Feature with a unique key")
    FEATURES[feature.key] = feature


def resolve(path):
    module, name = path.split(":", 1)
    value = import_module(module)
    for part in name.split("."):
        value = getattr(value, part)
    return value


def prepare(feature):
    """Check imports and exported names before making security declarations."""
    for module, names in feature.modules.items():
        obj = import_module(module)
        for name in names:
            getattr(obj, name)
    classes = [(resolve(path), names) for path, names in feature.classes.items()]
    types = [(resolve(path), names) for path, names in feature.types.items()]
    for cls, names in classes + types:
        if not isinstance(cls, type):
            raise TypeError(f"{cls!r} is not a class")
        # Attribute names may refer to instance attributes, e.g. Image.size.
    exports = {name: resolve(path) for name, path in feature.exports.items()}
    return classes, types, exports


def availability(feature):
    versions = []
    try:
        for name in feature.distributions:
            versions.append(f"{name} {metadata.version(name)}")
        prepare(feature)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return True, ", ".join(versions) or "Python / Zope"


def expand(keys):
    result = []
    visiting = set()

    def visit(key):
        if key not in FEATURES:
            raise ValueError(f"Unknown integration: {key}")
        if key in visiting:
            raise ValueError(f"Circular integration dependency: {key}")
        if key in result:
            return
        visiting.add(key)
        for dependency in FEATURES[key].requires:
            visit(dependency)
        visiting.remove(key)
        result.append(key)

    for key in keys:
        visit(key)
    return tuple(result)


def load_extensions():
    """Trusted installed eggs may contribute a callable returning Features."""
    entries = metadata.entry_points()
    if hasattr(entries, "select"):
        entries = entries.select(group="enablescripts.integrations")
    else:  # Python 3.8/3.9 importlib.metadata returns a dictionary.
        entries = entries.get("enablescripts.integrations", ())
    for entry in sorted(entries, key=lambda item: item.name):
        for feature in entry.load()():
            register(feature)
