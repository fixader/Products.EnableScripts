# Products.EnableScripts

Granular, opt-in library access for **Zope 5 / 6 Script (Python)**, managed from
the ZMI. Detect installed supported libraries, enable an integration, and expand
its checkboxes to control individual imports, objects, methods and attributes.

> **RestrictedPython is restricted for a reason.** This product intentionally
> expands what restricted scripts can access. Use it only when you trust every
> person who can create or edit scripts on the affected Zope server. These grants
> are process-wide. Library calls may access files, networks and server resources.
> Checkboxes do **not** make third-party libraries safe or establish a sandbox.
> Read [SECURITY.md](https://github.com/fixader/Products.EnableScripts/blob/main/SECURITY.md)
> before enabling anything.

## Features

* **BytesIO**: binary file-like objects in memory, without enabling `io.open`.
* **Pillow**: direct `PIL.Image`, `ImageDraw`, `ImageFont`, `ImageOps` and `ImageEnhance` imports.
* **ReportLab**: Canvas, ImageReader, text/path objects, colors, fonts, Platypus and barcodes.
* **XML / ElementTree**, **HTTP / urllib**, optional **Hubarcode**.
* **Helpers**: PdfBuffer, ImageBuffer, PDF/image responses, saving Zope images.
* **Extended io compatibility**: a separate choice for other io exports, including filesystem APIs.
* Manager-only settings with POST and CSRF checks, persisted in the ZODB.
* Extension entry points for additional explicitly supported libraries.

Libraries start **disabled**. Their individual subchoices default to enabled, so
one checkbox enables the supported integration. Subchoices are remembered when
the parent is disabled. Dependencies such as BytesIO are selected automatically.

## Install

Install into Zope's Python environment from a wheel or source checkout:

```sh
python -m pip install /path/to/products_enablescripts-0.1.0-py3-none-any.whl
# Or, from a checkout, also installing Pillow and ReportLab:
python -m pip install '.[all]'
```

Once published on PyPI, the package name is `Products.EnableScripts`.
The base distribution does not install Pillow or ReportLab; use the `pillow`,
`reportlab`, or `all` extras when desired. It never installs packages from the ZMI.

Restart Zope, then open **Control Panel → EnableScripts**:

```text
/Control_Panel/EnableScripts/manage_main
```

Select integrations, optionally adjust subchoices, save, and restart **every Zope
worker**. The page distinguishes saved selections from the current process's
active policy. Saving does not change process-global assertions during an HTTP
transaction. Missing optional dependencies are shown on the page and skipped at
startup. Only a root Manager can change settings.

For buildout, keep this product's source outside generated instance/parts
directories and include it in `develop` and the instance `eggs`:

```ini
[buildout]
develop = src/Products.EnableScripts

[instance]
eggs =
    Zope
    Products.PythonScripts
    Products.EnableScripts
    Pillow
    reportlab
```

Merge these entries into your existing buildout. Product code is reproducibly
installed by buildout; saved selections survive in the preserved ZODB.

## Example: a restricted Python Script

Enable BytesIO, Pillow and ReportLab Canvas:

```python
from io import BytesIO
from PIL import Image, ImageDraw
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader

image = Image.new('RGB', (400, 150), 'white')
ImageDraw.Draw(image).text((20, 20), 'Hello from Zope', fill='black')
output = BytesIO()
canvas = Canvas(output)
canvas.drawImage(ImageReader(image), 30, 550, width=400, height=150)
canvas.save()
context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
return output.getvalue()
```

Helpers are available separately, e.g.
`from Products.EnableScripts import ImageBuffer, PdfBuffer`.

## Migration and limits

Disable previous GlobalModule / GlobalModules assertion products before
migrating. This product cannot revoke grants made elsewhere. Existing helper
imports from `Products.GlobalModule` must be changed to `Products.EnableScripts`;
normal imports from `PIL`, `reportlab`, `io`, etc. keep their names.

Known legacy ReportLab module exports and Canvas/ImageReader methods are
discovered from the installed version and displayed individually. Newly
discovered names after an upgrade default to enabled under an enabled
integration: review selections after library upgrades. Private `_` names remain
subject to RestrictedPython. Import access does not promise that every object
returned by every library function is usable; supported object policies are
listed in the panel. These policies govern attribute access, not arbitrary
attribute assignment.

## Development and publishing

```sh
python -m pip install -e '.[all,test]'
python -m pytest -q
python -m build
python -m twine check dist/*
```

Use a Zope-compatible dependency set. Zope 5.14.2 tests use ZODB < 6.3 because
the `class-factory` configuration key is defined by Zope itself. Zope 6.1 tests
use ZODB >= 6.3, which supplies that key. Separate constraint files are provided
for these upstream combinations; this is not an EnableScripts data format requirement.

See [RELEASING.md](https://github.com/fixader/Products.EnableScripts/blob/main/RELEASING.md)
for the manual PyPI Trusted Publishing workflow, and
[README.md](https://github.com/fixader/Products.EnableScripts/blob/main/README.md)
for Norwegian instructions and the integration extension API.

MIT licensed. Early release: validate your actual scripts on a test server
before deploying it to production.

## Legacy Hubarcode 1.0.0

The original DataMatrix implementation contains Python 2 imports, tuple arguments
and string buffers. A separate, explicit maintenance command is provided in the
source distribution/repository:

```sh
python tools/repair_hubarcode.py
python tools/repair_hubarcode.py --apply --backup-dir /safe/path/hubarcode-before-repair
```

It verifies the exact original files, saves backups, and repairs only the
DataMatrix implementation for Python 3. It is never run automatically. Restart
Zope afterward. Reinstalling the original dependency overwrites the repair, so
include this explicit step in your deployment if using this legacy package.
The original size limit remains 44 encoded data codewords; larger inputs and
non-Latin-1 text raise ValueError. Code128/EAN13/QR implementations in this old
package are outside this repair; use the separate ReportLab barcode integration
for supported alternatives.
