"""Stable keys for the detailed checkboxes and their effective policy."""


def symbol_key(module, name):
    return f"symbol|{module}|{name}"


def object_key(path):
    return f"object|{path}"


def member_key(path, name):
    return f"member|{path}|{name}"


def choices(feature):
    keys = set()
    for module, names in feature.modules.items():
        keys.update(symbol_key(module, name) for name in names)
    for path, names in {**feature.classes, **feature.types}.items():
        keys.add(object_key(path))
        keys.update(member_key(path, name) for name in names)
    keys.update(symbol_key("Products.EnableScripts", name) for name in feature.exports)
    return keys


def allowed_members(path, names, disabled):
    if object_key(path) in disabled:
        return {}
    return {name: 1 for name in names if member_key(path, name) not in disabled}
