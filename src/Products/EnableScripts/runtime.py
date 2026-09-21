"""Apply a frozen policy once in each server process, never during a request."""

import logging
import os
from importlib import import_module

from AccessControl import ModuleSecurityInfo
from AccessControl.SecurityInfo import secureModule
from AccessControl.SimpleObjectPolicies import allow_type

from .policy import allowed_members, module_groups, object_key, symbol_key
from .registry import FEATURES, availability, expand, prepare, resolve

logger = logging.getLogger("Products.EnableScripts")
ACTIVE = set()
ERRORS = {}
SNAPSHOT = None
PROCESS_ID = os.getpid()


def snapshot(enabled, disabled, custom=(), custom_enabled=()):
    return (tuple(sorted(expand(enabled))), tuple(sorted(disabled)),
            tuple(custom), tuple(sorted(custom_enabled)))


def activate(enabled=(), disabled=(), custom=(), custom_enabled=()):
    """Repeated identical initialization is harmless; live changes are refused."""
    global SNAPSHOT
    from .custom import features as custom_features
    features = dict(FEATURES, **custom_features(custom))
    current = snapshot(enabled, disabled, custom, custom_enabled)
    if SNAPSHOT is not None:
        if current != SNAPSHOT:
            raise RuntimeError("EnableScripts policy changed; restart this Zope process")
        return
    disabled = set(disabled)
    for feature in features.values():
        for key, (_, keys) in module_groups(feature).items():
            if key in disabled:
                disabled.update(keys)
    denied_objects = []
    for feature in features.values():
        for path in tuple(feature.classes) + tuple(feature.types):
            if object_key(path) in disabled:
                try:
                    denied_objects.append(resolve(path))
                except (ImportError, AttributeError):
                    pass
    for key in expand(tuple(enabled) + tuple("custom:" + name for name in custom_enabled), features):
        feature = features[key]
        blocked = set(feature.requires) - ACTIVE
        available, reason = availability(feature)
        if blocked or not available:
            ERRORS[key] = ("Unavailable dependencies: " + ", ".join(sorted(blocked))) if blocked else reason
            logger.error("%s not enabled: %s", key, ERRORS[key])
            continue
        # Resolve everything before granting anything for this feature.
        classes, types, exports = prepare(feature)
        class_paths = list(feature.classes)
        type_paths = list(feature.types)
        for module_name, names in feature.modules.items():
            module = import_module(module_name)
            security = ModuleSecurityInfo(module_name)
            for name in names:
                denied = (symbol_key(module_name, name) in disabled or
                          any(getattr(module, name) is cls for cls in denied_objects))
                if denied:
                    security.declarePrivate(name)
                else:
                    security.declarePublic(name)
        for path, (cls, names) in zip(class_paths, classes):
            policy = allowed_members(path, names, disabled)
            cls.__allow_access_to_unprotected_subobjects__ = policy
            # Type assertions cover exact types; the class map also covers
            # subclasses, notably Image.open()'s format-specific ImageFiles.
            if not hasattr(cls, "__roles__"):
                allow_type(cls, policy)
        for path, (cls, names) in zip(type_paths, types):
            # Built-in C types such as BytesIO cannot have class attributes set.
            allow_type(cls, allowed_members(path, names, disabled))
        package = import_module("Products.EnableScripts")
        security = ModuleSecurityInfo("Products.EnableScripts")
        for name, value in exports.items():
            setattr(package, name, value)
            denied = (symbol_key("Products.EnableScripts", name) in disabled or
                      any(value is cls for cls in denied_objects))
            if denied:
                security.declarePrivate(name)
            else:
                security.declarePublic(name)
        # `from PIL import Image` secures PIL, not necessarily PIL.Image.
        # Apply child declarations eagerly so Image.new is guarded correctly.
        for module_name in feature.modules:
            secureModule(module_name)
        if exports:
            secureModule("Products.EnableScripts")
        ACTIVE.add(key)
        logger.info("Enabled %s (process %s)", feature.title, PROCESS_ID)
    SNAPSHOT = current
