# Changelog

## 0.1.0

* Add a Manager-only ZMI panel with per-library and per-symbol/object/member choices.
* Persist selections in the ZODB and apply them at worker startup.
* Support BytesIO, Pillow, ReportLab Canvas/Platypus/barcodes, XML, HTTP and optional Hubarcode.
* Port the original PDF/image helpers to Products.EnableScripts.
* Add real restricted-script tests and WSGI/restart/authorization tests.
* Package for buildout/pip and prepare manual PyPI Trusted Publishing.
