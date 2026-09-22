# Products.EnableScripts

**Explore Python libraries directly from Zope's Script (Python).**

EnableScripts expands the capabilities available to restricted Python scripts in
**Zope 5 and 6**. It lets an administrator expose selected installed libraries
through a ZMI control panel, so script authors can use APIs that would otherwise
commonly be accessed through an External Method or a filesystem product.

The purpose is practical: shorten the path between an idea and a working
experiment. Explore HTTPS connections, generate a PDF with ReportLab, manipulate
images with Pillow, work with XML, or try another installed library without
writing a new External Method wrapper for each experiment. Once the administrator
has installed the libraries, configured access and restarted Zope, authors can
iterate on their Script (Python) code through the ZMI.

This can be especially useful for **teaching, learning, demonstrations and rapid
prototyping**. It can also be a useful development tool on a server where the
people who can create or edit scripts form a small, known and controlled group.
A small group is not a security mechanism: every member must be trusted with the
capabilities of the libraries you expose.

EnableScripts intentionally widens access. It does not turn every Python package
into a restricted library, guarantee compatibility with arbitrary APIs, or make
untrusted code safe to run.

## What this product includes — and what it does not

EnableScripts does **not** contain, redistribute or automatically install Pillow,
ReportLab, Hubarcode, or any other optional application library it can expose. It only provides Zope security
declarations and management controls that can expose selected APIs from
libraries already installed separately in the Python environment used by Zope.

Installing EnableScripts gives you no license or other right to use a third-party
library. You are responsible for obtaining each library from its own publisher
and complying with its license, copyright terms, commercial terms, export
restrictions and other applicable requirements. Those libraries remain the work
and responsibility of their respective authors and distributors. The
EnableScripts author does not supply, license, endorse or accept responsibility
for them.

What EnableScripts can do is make compatible libraries easier and more enjoyable
to explore from Script (Python): it shows useful imports and supported APIs,
provides tested presets, and lets trusted users experiment quickly in the ZMI.
Install every library independently before trying to enable it here.

## Why this exists

This is not only a classroom experiment. The author has used equivalent
GlobalModule-style integrations in substantial Zope software solutions since the
Zope 2 era. That approach has supported production systems generating hundreds
of thousands of PDFs and images. EnableScripts turns those years of practical
experience into an installable product with explicit controls, visible API
descriptions, persistent settings and much clearer warnings about the trust
boundary.

The productive idea is simple: when a small, controlled group already develops
inside Zope, direct access to carefully selected libraries can make Script
(Python) remarkably capable and enjoyable to use. It enables fast experiments
and can support serious workloads. Whether it is appropriate still depends on
the people, libraries, permissions and deployment around it; proven usefulness
does not remove the administrator's responsibility for those choices.

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

## When this approach is useful

* **Teaching and learning:** let trusted students or colleagues explore library
  APIs from Script (Python), see results immediately, and compare approaches.
  A shared teaching server still requires trust in every script author. Use
  separate environments where that trust is not appropriate.
* **Rapid development:** experiment with an HTTPS request, image transformation,
  PDF layout or barcode without deploying a new filesystem wrapper for every
  change to the experiment.
* **Small, controlled teams:** give a known group access to selected libraries
  when the administrator accepts the server-wide implications and controls who
  can create or modify scripts.

It is not suitable as a way to offer arbitrary Python execution to untrusted
users, customers, tenants or students on a shared server. Do not enable a library
because its name sounds harmless: review what its exposed APIs can actually do.

## EnableScripts and External Methods

An External Method is often a better choice when you want to expose **a narrow,
reviewed operation**. For example, a wrapper can accept a document ID, validate
it, and generate one specific report. It can keep file paths, network destinations
and low-level library operations out of the script author's control.

EnableScripts instead lets script authors call the selected library APIs directly.
That flexibility is its purpose, and also its trade-off: permission to use a PDF
or image library may include operations that read files, fetch URLs or consume
substantial resources. A module checkbox does not validate the arguments passed
to those operations.

External Methods themselves run unrestricted Python and are **not automatically
safe**. Their advantage is the opportunity to implement a smaller interface with
explicit validation and permission checks. A wrapper that simply accepts any
command, path or URL may offer little protection.

A practical workflow is to explore an API with EnableScripts on a controlled test
server, then decide whether the finished feature should remain available to
trusted script authors or move behind an External Method or filesystem product
with a carefully defined interface.

## A first learning session

1. Use a test server with data and operating-system permissions appropriate for
   the experiment. Identify everyone who can create or edit restricted scripts
   across all sites served by the affected Zope workers.
2. Install only the libraries needed for the exercise into Zope's own Python
   environment. EnableScripts configures access; it does not install packages
   from the browser.
3. Enable the required preset modules, save and restart every affected worker.
   For an additional library, use **Advanced: custom libraries** to inspect its
   exports and define any needed object rules before enabling it.
4. Create a Script (Python) in a test folder. Use the import examples shown in
   the panel and start with one small operation: create an in-memory image,
   generate a one-page PDF, or make an HTTPS request to a destination you control
   with an explicit timeout and bounded response size.
5. Change the script and run it again. Ordinary edits to the script do not
   require a Zope restart; changes to EnableScripts permissions do.
6. When finished, disable unnecessary grants, save and restart all affected
   workers. Review the experiment before turning it into an application feature.

The PDF/image example below provides a concrete starting point. For network
experiments, the HTTP / urllib preset includes URL-handling APIs; it is not an
HTTPS-only allowlist and does not restrict which destinations scripts may reach.

## Use at your own risk

**You are responsible for what you enable, who can write scripts, and the
consequences of those scripts.** This includes data loss, disclosure of sensitive
information, service disruption and misuse of server resources.

The author and contributors provide this software **as is, without warranty**,
and accept no responsibility for consequences arising from its use. If you
choose to expand RestrictedPython's capabilities, you do so at your own risk.
See [LICENSE](LICENSE) for the applicable MIT warranty disclaimer and limitation
of liability, and [SECURITY.md](SECURITY.md) for the security model and limitations.

## Features

* **BytesIO**: binary file-like objects in memory, without enabling `io.open`.
* **Pillow**: direct `PIL.Image`, `ImageDraw`, `ImageFont`, `ImageOps` and `ImageEnhance` imports.
* **ReportLab**: Canvas, ImageReader, text/path objects, colors, fonts, Platypus and barcodes.
* **XML / ElementTree**, **HTTP / urllib**, optional **Hubarcode**.
* **Helpers**: PdfBuffer, ImageBuffer, PDF/image responses, saving Zope images.
* **Extended io compatibility**: a separate choice for other io exports, including filesystem APIs.
* Manager-only settings with POST and CSRF checks, persisted in the ZODB.
* **Advanced custom libraries:** inspect installed modules, select exports and define explicit object rules.
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

Follow [INSTALL.md](INSTALL.md) for step-by-step virtualenv and buildout setup,
optional libraries, custom access rules, restarts, removal and troubleshooting.


Install into Zope's Python environment from a wheel or source checkout:

```sh
python -m pip install /path/to/products_enablescripts-0.2.2-py3-none-any.whl
# Or install the base product from a source checkout:
python -m pip install .
```

Once published on PyPI, the package name is `Products.EnableScripts`.
Install Pillow, ReportLab and every other library separately, under their own
licenses and terms. EnableScripts never installs third-party libraries from the
package or the ZMI.

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

For older buildout/setuptools versions, use the local-egg procedure in
[INSTALL.md](INSTALL.md#buildout-retain-the-installation-across-rebuilds) instead
of assuming a pyproject-only development checkout will work.

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
python -m pip install '.[test]'
python -m pytest -q
python -m build
python -m twine check dist/*
```

Use a Zope-compatible dependency set. Zope 5.14.2 tests use ZODB < 6.3 because
the `class-factory` configuration key is defined by Zope itself. Zope 6.1 tests
use ZODB >= 6.3, which supplies that key. Separate constraint files are provided
for these upstream combinations; this is not an EnableScripts data format requirement.

See [RELEASING.md](https://github.com/fixader/Products.EnableScripts/blob/main/RELEASING.md)
for the manual PyPI Trusted Publishing workflow.

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
