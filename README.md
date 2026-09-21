# Products.EnableScripts

Granular, opt-in library access for **Zope 5 / 6 Script (Python)**, managed from
the ZMI. Detect installed supported libraries, enable an integration, and expand
its module choices. Each module lists its imports, objects, methods and attributes
without separate checkboxes for every API member. Installation commands appear once per library, with Script (Python) import
examples beside each module. ReportLab Canvas,
Platypus, barcodes and PDF helpers are grouped together.

> **RestrictedPython is restricted for a reason.**
>
> **Enabling a library means trusting EVERY person who can create or edit
> Script (Python), or other restricted Python code, anywhere on the affected
> Zope server.** That includes authors in other sites and folders, current and
> future authors, and people who cannot access this control panel. The grant is
> not limited to the administrator, current site or a particular script.
>
> Allowed library functions execute ordinary Python code with the Zope operating
> system account's privileges. Depending on the API, they can access files,
> networks, processes and server resources. Do not enable access unless you trust
> all affected script authors with those capabilities. Checkboxes are not a sandbox.
>
> Grants are process-wide. All workers/ZEO clients loading these settings apply
> them after restart. Independent Zope instances with separate processes and
> settings are not automatically affected.

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

## Compatibility

EnableScripts supports Python 3.8+ with Zope 5.8+ or Zope 6, using a Python
version supported by the chosen Zope release. Supporting Python 3.8 does not
mean that Zope 6 can run on it. The Python 3.8 test environment uses Zope 5.8.3
and Pillow 10.4 with ReportLab below 4.4.3; newer environments continue to test Zope 5 and Zope 6.

## Install

Install into Zope's Python environment from a wheel or source checkout:

```sh
python -m pip install /path/to/products_enablescripts-0.2.1-py3-none-any.whl
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

1. Sign in as a Manager at the Zope application root and open the panel.
2. Check the availability message. A package can be installed yet unavailable
   because its version lacks APIs required by the integration. Install a compatible
   version using **Zope's Python**, then restart and reload the panel.
3. Select the library and only the modules you need. Module subchoices default
   to on. Expand **Includes** to review the exposed objects and methods.
   Dependencies such as BytesIO are selected automatically when saving.
4. Click **Save settings**. This persists the policy in ZODB; it does not change
   permissions in any running worker.
5. Restart **every Zope worker and ZEO client** loading this configuration.
   Reload the panel and check for errors and the restart-required notice.
   Status describes the responding process, so verify every worker in a
   multi-worker deployment. Active means the integration loaded, not that all
   possible library operations are supported.
6. Use the module's displayed import example in Script (Python) and test with
   representative input before using it in your application.

To revoke a preset grant, uncheck the library or module and save. To revoke a
custom grant, disable or remove its saved entry. **Restart every worker in both
cases**: old grants remain active until restart. Removing EnableScripts cannot
revoke overlapping grants from another product or equivalent access through
another enabled library.

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

## Advanced: custom libraries

A root Manager can configure additional installed modules under **Advanced:
custom libraries**. Enter a dotted import name such as `decimal`, inspect the
public exports, and save the names you want scripts to import. No package is
installed from this screen. Package names and import names may differ.

Inspection imports the module as ordinary Python code, so only inspect trusted
libraries. Inspection itself adds no EnableScripts security declarations.
New entries are disabled by default. Enable the saved entry and restart every
worker to apply it. Editing, disabling or removing an entry also requires a
restart; the panel displays the policy currently active in that process.

For returned objects, add explicit rules such as:

```text
decimal:Decimal = quantize as_tuple
```

These rules cover exact object types. Instance attributes can be entered even
when inspection cannot discover them. Subclasses may need separate rules.
Private names, wildcards, duplicate class policies and classes that manage their
own Zope security are rejected. Modules and classes already covered by presets
must be configured in their existing controls. Custom exports are frozen when
saved: newly added names after library upgrades are not automatically allowed.

This is an advanced trust decision, not a sandbox. Libraries can expose filesystem,
network or process access. Arbitrary packages are not guaranteed to work, and
other libraries/products can grant overlapping access. Custom entries and preset
selections are saved independently in ZODB.

## Migration and limits

Disable previous GlobalModule / GlobalModules assertion products before
migrating. This product cannot revoke grants made elsewhere. Existing helper
imports from `Products.GlobalModule` must be changed to `Products.EnableScripts`;
normal imports from `PIL`, `reportlab`, `io`, etc. keep their names.

Known legacy ReportLab module exports and Canvas/ImageReader methods are
discovered from the installed version and listed under their module. Newly
discovered names after an upgrade default to enabled under an enabled
module: review selections after library upgrades. Private `_` names remain
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
