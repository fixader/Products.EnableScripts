# Changelog

## 0.3.0

* Rename the distribution, Python namespace, ZMI panel and repository from
  `Products.EnableScripts` to `Products.RestrictedPythonExtensions`.
* Preserve settings created by the earlier name and continue reading its
  integration entry-point group during migration.
* Add an explicit statement that this is an independent project and is not
  maintained by the RestrictedPython project or the Zope Foundation.

## 0.1.0

* Add a Manager-only ZMI panel with per-library and per-symbol/object/member choices.
* Persist selections in the ZODB and apply them at worker startup.
* Support BytesIO, Pillow, ReportLab Canvas/Platypus/barcodes, XML, HTTP and optional Hubarcode.
* Port the original PDF/image helpers to the product package.
* Add real restricted-script tests and WSGI/restart/authorization tests.
* Package for buildout/pip and prepare manual PyPI Trusted Publishing.
