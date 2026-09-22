from types import SimpleNamespace

from Products.EnableScripts.settings import Settings as LegacySettings
from Products.RestrictedPythonExtensions.settings import get_settings, Settings


def test_legacy_settings_are_reused_and_migrated():
    app = SimpleNamespace()
    legacy = LegacySettings()
    legacy.enabled = ("bytesio",)
    app._enable_scripts_settings = legacy

    assert LegacySettings is Settings
    assert get_settings(app) is legacy
    assert not hasattr(app, "_restricted_python_extensions_settings")
    assert get_settings(app, create=True) is legacy
    assert app._restricted_python_extensions_settings is legacy
