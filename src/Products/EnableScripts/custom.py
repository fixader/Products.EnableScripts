"""Validated, explicit custom policies. Inspection imports trusted installed code."""
import keyword
from importlib import import_module
from types import ModuleType

from .registry import FEATURES, Feature, resolve


def public_name(name):
    return name.isidentifier() and not name.startswith('_') and not keyword.iskeyword(name)


def module_name(name):
    if not name or not all(public_name(part) for part in name.split('.')):
        raise ValueError('Enter a public dotted module name, for example decimal or mypackage.tools.')
    if any(name in feature.modules for feature in FEATURES.values()):
        raise ValueError('This module already belongs to a preset. Use its existing controls.')
    return name


def inspect_module(name):
    module = import_module(module_name(name))
    return tuple(sorted(name for name, value in vars(module).items()
                        if public_name(name) and not isinstance(value, ModuleType)))


def validate(name, exports, rules):
    available = inspect_module(name)
    exports = tuple(sorted(set(exports.replace(',', ' ').split())))
    if not exports or not set(exports) <= set(available):
        raise ValueError('Exports must be public names shown by module inspection; select at least one.')
    classes = {}
    for line in rules.splitlines():
        if not line.strip():
            continue
        path, sep, members = line.partition('=')
        path = path.strip()
        parts = path.split(':')
        if not sep or len(parts) != 2 or not all(public_name(p) for p in parts[0].split('.') + parts[1].split('.')):
            raise ValueError('Use module:Class = method attribute, one class per line.')
        cls = resolve(path)
        if not isinstance(cls, type):
            raise ValueError(path + ' is not a class.')
        if hasattr(cls, '__roles__'):
            raise ValueError(path + ' manages its own Zope security and cannot use custom type rules.')
        if any(cls is resolve(other) for other in classes):
            raise ValueError('List each class only once, including aliases.')
        # Avoid overriding the object policies maintained by tested presets.
        for feature in FEATURES.values():
            for preset in tuple(feature.classes) + tuple(feature.types):
                try:
                    existing = resolve(preset)
                except (ImportError, AttributeError):
                    continue
                if cls is existing:
                    raise ValueError(path + ' belongs to a preset; configure it there.')
        names = tuple(sorted(set(members.replace(',', ' ').split())))
        if not names or not all(public_name(member) for member in names):
            raise ValueError('Class rules require explicit public method or attribute names; wildcards are not supported.')
        classes[path] = names
    return (name, exports, tuple(sorted(classes.items())))


def features(records):
    return { 'custom:' + name: Feature('custom:' + name, name, 'Custom module',
                modules={name: exports}, types=dict(classes))
             for name, exports, classes in records }


def rules_text(record):
    return '\n'.join(path + ' = ' + ' '.join(names) for path, names in record[2])


def class_catalog(name):
    module = import_module(name)
    return tuple((name + ':' + key, tuple(sorted(member for member in dir(value) if public_name(member))))
                 for key, value in sorted(vars(module).items())
                 if public_name(key) and isinstance(value, type))
