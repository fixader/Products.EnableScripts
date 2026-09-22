# Installing and using EnableScripts

EnableScripts lets trusted authors explore libraries directly from Zope's
Script (Python), including operations often placed in External Methods: HTTPS
requests, PDF generation, image processing and more. It is useful for education
and rapid development where script-writing access is small and controlled.

EnableScripts itself contains and automatically installs none of the optional
application libraries it can expose. Pillow, ReportLab, Hubarcode and every additional package must be obtained and installed
separately. Their own licenses and terms govern their use; installing
EnableScripts does not provide, replace or extend those rights. The respective
authors and distributors remain responsible for their libraries. EnableScripts
only makes selected APIs from already installed software available to restricted
scripts.

**Before enabling anything, you must trust EVERY person who can create or edit
restricted Python scripts anywhere on the affected Zope server, including other
sites and folders.** A small group is not a sandbox. Libraries run ordinary Python
code and may exercise the Zope operating-system account's file, network or process
privileges. Read [SECURITY.md](SECURITY.md). You accept responsibility for the
consequences; this software is provided as is, without warranty, under [LICENSE](LICENSE).

A narrowly designed External Method may be preferable for a finished feature
because it can validate inputs and expose only one operation. External Methods
are unrestricted code too; their safety depends on their implementation.

## 1. Identify the Python that actually runs Zope

Do not assume the system `python` or `pip` belongs to Zope. Inspect the service's
startup command or the generated instance script. Use that environment's Python
explicitly in the following commands. Replace `/path/to/zope-venv` with its real
path; it is a placeholder, not a directory to create with that literal name.

```sh
/path/to/zope-venv/bin/python --version
/path/to/zope-venv/bin/python -m pip show Zope Products.PythonScripts
```

Buildout may keep packages in its `eggs` directory rather than ordinary
site-packages, so `pip show` alone is not conclusive there. Check buildout's
configuration and generated instance script as well.

EnableScripts requires Python 3.8+ and Zope 5.8+ or Zope 6. Your Zope release must
also support your Python version: this does not make Zope 6 compatible with
Python 3.8. Preserve your existing Zope dependency pins. Back up configuration
and the ZODB using your deployment's normal backup procedure before changing a
server you rely on; try the installation on a test server first.

## 2. Install EnableScripts, without optional libraries

At the time of this guide, the package has not been published on PyPI. Install
from the repository, or use a wheel you built from it. This command pins the
0.2.2 implementation to a specific commit and requires Git:

```sh
/path/to/zope-venv/bin/python -m pip install "Products.EnableScripts @ git+https://github.com/fixader/Products.EnableScripts.git@e2366c2dffe47c416e076fe80cd1b802d136eb4e"
```

Or install a local wheel:

```sh
/path/to/zope-venv/bin/python -m pip install /path/to/products_enablescripts-0.2.2-py3-none-any.whl
```

These commands install EnableScripts and resolve its required Zope dependencies;
they do not request the optional Pillow or ReportLab libraries. Use your normal
constraints file with pip if your deployment pins dependencies. In an already
validated environment, `--no-deps` prevents dependency changes, but then you must
ensure the declared runtime requirements are already satisfied yourself.

On Windows, use the equivalent environment executable, for example
`C:\Zope\venv\Scripts\python.exe -m pip install ...`.

**Buildout users: complete the buildout section below as well.** A manual pip
installation is not a replacement for recording the package in buildout.

## 3. Install only the extra libraries you need

Install these into the same Python environment. No installation is needed for
standard-library modules such as `io`, `xml`, `urllib` or `decimal`.

```sh
# Images; pip selects a release compatible with the interpreter.
/path/to/zope-venv/bin/python -m pip install "Pillow>=10"

# PDFs and ReportLab barcodes, with Python 3.9 or newer.
/path/to/zope-venv/bin/python -m pip install "reportlab>=4,<6"

# Use this ReportLab range instead on Python 3.8.
/path/to/zope-venv/bin/python -m pip install "reportlab>=4,<4.4.3"
```

These commands can upgrade existing libraries. Review their compatibility with
your application before running them. They are optional: you can install only
EnableScripts first and inspect which existing libraries are available.

EnableScripts deliberately has no convenience extra that installs these
libraries. Install each desired package explicitly so its source, version and
license are visible in your deployment configuration. Other packages are
installed in the same manner, then configured through Advanced; not every
library API will work in restricted scripts without additional object rules.

The ZMI panel **does not run pip, install packages, or repair dependencies**.
Package names and import names can differ: install `Pillow`, import `PIL.Image`.

## 4. Restart Zope and open the panel

Restart using the service manager or instance command your server already uses.
For example, only if your service is actually named `zope-instance.service`:

```sh
sudo systemctl restart zope-instance.service
```

Sign in as a Manager at the Zope application root and open:

```text
http://YOUR-SERVER:PORT/Control_Panel/EnableScripts/manage_main
```

EnableScripts appears in the Zope Control Panel, not Plone's add-on installer.
Libraries initially remain disabled. Installed, supported libraries are available
for selection; missing or incompatible ones show an error and cannot be newly
enabled. Installing a library does not itself grant restricted scripts access.

## 5. Grant access, then test a script

1. Review who can create or edit scripts across every affected site and folder.
2. Select a preset library and only the modules needed. Expand **Includes** to
   inspect the exposed API. Module choices default to on, and dependencies such
   as BytesIO are enabled automatically when saving.
3. Click **Save settings**. Restart every worker and ZEO client loading these
   settings. Saving alone does not change permissions in running processes.
4. Reload the panel and check status and errors. Status refers to the process
   that answered the request; verify all workers in a multi-worker deployment.
5. Create a Script (Python) in a test folder. Copy the relevant import example
   and start with a small operation. See the [PDF/image example](README.md#example-a-restricted-python-script).

After the grants are active, ordinary script edits do not require restarts.
Changing EnableScripts permissions does. For HTTPS experiments, use a destination
you control, an explicit timeout and a bounded response size. The urllib preset
is not an HTTPS-only or destination-restricted policy.

## 6. Add an additional library through Advanced

Scroll to **Advanced: custom libraries**, or append `#advanced` to the panel URL.

1. Install the package in Zope's environment and restart as needed.
2. Enter the importable module name and click **Inspect module**. Inspection
   imports trusted installed code and may execute initialization with side
   effects; it does not add EnableScripts permission grants.
3. Review the detected exports and remove names you do not want to expose.
4. Add explicit class rules if returned objects need method or attribute access.
   For example, inspect `decimal`, retain the export `Decimal`, and enter:

   ```text
   decimal:Decimal = quantize as_tuple
   ```

5. Check **Enable this module after restart**, save and restart all workers.
   Leaving it unchecked saves a disabled draft.
6. In Script (Python), try:

   ```python
   from decimal import Decimal
   return str(Decimal('1.235').quantize(Decimal('0.01')))
   ```

The expected result is `1.24`. Class rules cover exact types; subclasses may need
separate rules. An import grant alone does not guarantee instance methods work.
Private names, wildcards and conflicting class rules are rejected. Preset modules
must use their existing controls. Custom exports are frozen when saved, but
upgrades may still change the behavior of functions you have already allowed.

## Buildout: retain the installation across rebuilds

Keep source or local distributions outside generated `parts` directories. Add
EnableScripts to the **existing** instance's eggs, preserving its current entries:

```ini
[Instance]
eggs =
    ... existing entries ...
    Products.EnableScripts==0.2.2
```

The ellipsis above is explanatory; do not paste it into your configuration.
Use your actual part name, which might be `instance` rather than `Instance`.
Only add Pillow, ReportLab or another library if you want buildout to install and
manage it. Preserve the versions required by your application.

Since this version is not on PyPI, buildout also needs a source for the package.
A modern source-development setup can use a checkout in `src/Products.EnableScripts`
with a corresponding `develop` entry. Older buildout/setuptools installations may
not understand a pyproject-only source tree. The following local-egg method was
used for the Python 3.8/Zope 5.8.3 deployment without upgrading its live setuptools:

1. In a separate build environment using the **same Python version** as the Zope
   instance, install a compatible setuptools and wheel, then check out the source:

   ```sh
   python3.8 -m venv /path/to/egg-build-env
   /path/to/egg-build-env/bin/python -m pip install --upgrade pip "setuptools>=61" wheel
   git clone https://github.com/fixader/Products.EnableScripts.git /path/to/enablescripts-source
   cd /path/to/enablescripts-source
   git checkout e2366c2dffe47c416e076fe80cd1b802d136eb4e
   /path/to/egg-build-env/bin/python -c "from setuptools import setup; setup(script_args=['bdist_egg'])"
   ```

2. Copy the generated `dist/Products.EnableScripts-0.2.2-py3.8.egg` into your
   buildout's local `downloads` directory. Retain it with your deployment files.
3. Add that directory to the existing `[buildout] find-links` list:

   ```ini
   [buildout]
   find-links =
       downloads
   ```

4. Run your existing `bin/buildout -N`, inspect the result, and restart the
   instance. `-N` prefers installed distributions but is not a substitute for
   dependency pins. Do not restart a working instance after a failed buildout;
   resolve the error or restore the prior configuration first.

The source checkout, local distribution and buildout configuration make the code
reinstallable. The enabled/disabled choices and custom rules persist in ZODB as
long as you retain that database.

## Disable, update or remove

To revoke access, uncheck the preset module/library, or disable/remove the custom
policy, then save and restart every worker. Existing grants remain until restart.
Another enabled API or another product may still grant overlapping access.

When updating EnableScripts, install the intended version, update buildout pins
and local distributions if applicable, and restart all workers. Review saved
settings and test actual scripts after library upgrades. Removing the package
requires removing its buildout entry as well, then restarting; remove or adapt
scripts that depend on it before doing so.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| No EnableScripts panel | Correct Python environment, instance eggs, startup log and completed restart. |
| No Advanced section | The server may run an older version. Advanced was introduced in 0.2.0. Check which server and port you opened. |
| Package installed but unavailable | The error may indicate an incompatible API/version or a missing dependency, not a missing installation. |
| Import works but a method is denied | Review the object's exact type and its explicit member rules; a returned subclass may need another rule. |
| Saved changes have no effect | Restart every worker; a load balancer may still route to an old process. |
| Disabling one API did not revoke equivalent access | Check overlapping preset/custom APIs and old GlobalModule/GlobalModules or other products. |
| Buildout cannot find EnableScripts | Retain the pinned distribution in its configured find-links location; the package is not yet on PyPI. |
