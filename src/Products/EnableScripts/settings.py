"""Compatibility shim for settings objects pickled before the product rename."""

from Products.RestrictedPythonExtensions.settings import Settings

__all__ = ("Settings",)
