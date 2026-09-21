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


def module_groups(feature):
    """Group existing policy keys without changing the persisted policy format."""
    groups = {module: set(symbol_key(module, name) for name in names)
              for module, names in feature.modules.items()}
    if feature.exports:
        groups["Products.EnableScripts"] = {
            symbol_key("Products.EnableScripts", name) for name in feature.exports}
    for path, names in {**feature.classes, **feature.types}.items():
        module = path.split(":", 1)[0]
        candidates = [name for name in groups if module == name or module.startswith(name + ".")]
        # Returned objects (Canvas text/path objects, BytesIO memory views)
        # belong to the module that creates them, not a separate import switch.
        owner = max(candidates, key=len) if candidates else next(iter(groups), module)
        if module.startswith("reportlab.pdfgen."):
            owner = "reportlab.pdfgen.canvas"
        groups.setdefault(owner, set()).update({object_key(path)} | {
            member_key(path, name) for name in names})
    return {f"module|{feature.key}|{module}": (module, keys)
            for module, keys in groups.items()}
