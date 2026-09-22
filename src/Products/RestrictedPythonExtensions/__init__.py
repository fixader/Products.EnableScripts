"""Zope product initialization. Optional libraries are not imported here."""

from . import integrations  # Register descriptions, without loading libraries.
from .registry import load_extensions

_extensions_loaded = False


def initialize(context):
    """Load persisted policy in every Zope worker and attach the ZMI panel."""
    global _extensions_loaded
    from .management import install_panel
    from .runtime import activate
    from .settings import get_settings

    if not _extensions_loaded:
        load_extensions()
        _extensions_loaded = True
    app = context.getApplication()
    settings = get_settings(app)
    activate(settings.enabled if settings else (), settings.disabled if settings else (),
             getattr(settings, "custom", ()), getattr(settings, "custom_enabled", ()))
    install_panel()
