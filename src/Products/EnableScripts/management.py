"""Manager-only ZMI control panel with persistent module selections."""

from html import escape
from importlib import metadata
import sys

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.class_init import InitializeClass
from App.ApplicationManager import ApplicationManager
from OFS.SimpleItem import SimpleItem
from zExceptions import BadRequest, Forbidden, Unauthorized

try:
    from ZPublisher import zpublish
except ImportError:  # Zope 5 uses docstring-based publishing.
    def zpublish(value):
        return value

from . import runtime
from .policy import module_groups
from .registry import FEATURES, availability, expand
from .settings import get_settings


def _items(value):
    return (value,) if isinstance(value, str) else tuple(value or ())


def _checkbox(name, value, label, checked=True, disabled=False):
    attributes = (' checked' if checked else '') + (' disabled' if disabled else '')
    return (f'<label><input type="checkbox" name="{escape(name)}:list" '
            f'value="{escape(value, quote=True)}"{attributes}> {escape(label)}</label>')


class EnableScriptsPanel(SimpleItem):
    """Configure process-wide library access for restricted Zope scripts."""

    id = "EnableScripts"
    title = "EnableScripts"
    meta_type = "EnableScripts settings"
    __roles__ = ("Manager",)
    security = ClassSecurityInfo()
    security.declareObjectProtected("Manage properties")
    manage_options = ({"label": "EnableScripts", "action": "manage_main"},)

    def _require_manager(self):
        app = self.getPhysicalRoot()
        user = getSecurityManager().getUser()
        if "Manager" not in user.getRolesInContext(app):
            raise Unauthorized("Only a root Manager can configure EnableScripts")
        return app, user.getId() or user.getUserName()

    @zpublish
    @security.protected("Manage properties")
    def manage_main(self, REQUEST=None, saved=False):
        """Display installed integrations and the policy for the next restart."""
        app, user_id = self._require_manager()
        settings = get_settings(app, create=True)
        enabled = set(settings.enabled)
        disabled = set(settings.disabled)
        pending = runtime.SNAPSHOT != runtime.snapshot(enabled, disabled, getattr(settings, "custom", ()),
                                                       getattr(settings, "custom_enabled", ()))
        content = [self._header()]
        content.append(self._trust_warning())
        if saved:
            content.append('<p class="notice">Settings saved in ZODB.</p>')
        if pending:
            content.append('<p class="notice">Restart required. Restart every Zope worker to apply these settings.</p>')
        content.append(f'<p>Current process: <strong>{runtime.PROCESS_ID}</strong>. Settings affect all sites in this process.</p>')
        content.append('<details class="feature"><summary>How to install, enable and disable libraries</summary>'
                       '<ol><li>Install EnableScripts and any required library into the Python environment used by Zope. '
                       'The commands shown below must use that environment&#8217;s Python. With buildout, also retain '
                       'the packages in the instance eggs. This page does not install packages.</li>'
                       '<li>Restart Zope after installing packages, then return here. An unavailable library cannot '
                       'be enabled; read its reported error. An installed version may still lack required APIs.</li>'
                       '<li>Select the library and the modules you need. Module choices default to on. Expand Includes '
                       'to review the exposed objects and methods. Dependencies such as BytesIO are selected automatically.</li>'
                       '<li>Click Save settings, then restart every Zope worker using this configuration, including '
                       'ZEO clients. Saving alone does not change running scripts&#8217; permissions.</li>'
                       '<li>Reload this page and check the process status and any activation errors. Active means the '
                       'integration loaded in this process; it does not prove every library operation will work.</li>'
                       '<li>Use the displayed import statement in Script (Python). Test with representative data before '
                       'using the integration in your application.</li></ol>'
                       '<p><strong>To revoke access:</strong> uncheck the library or module, save, and restart every worker. '
                       'For custom entries, disable or remove the policy and restart. Until then, existing grants remain '
                       'active. Other products or enabled APIs may still grant overlapping access.</p></details>')
        content.append('<form method="post" action="manage_save">')
        content.append(f'<input type="hidden" name="token" value="{settings.token(user_id)}">')
        reportlab_install = ('python -m pip install "reportlab>=4,<4.4.3"'
                             if sys.version_info < (3, 9) else 'python -m pip install reportlab')
        pdf_keys = ("reportlab", "platypus", "barcodes", "pdf_helpers")
        ordered = sorted(FEATURES, key=lambda key: (
            1 if key in pdf_keys else 0 if key == "bytesio" else 2, list(FEATURES).index(key)))
        reportlab_group = False
        for key in ordered:
            feature = FEATURES[key]
            is_reportlab = key in pdf_keys
            if is_reportlab and not reportlab_group:
                content.append('<div class="library-group"><h2>ReportLab &amp; PDF</h2>'
                               '<p>Install in Zope&#8217;s Python environment: '
                               f'<code>{escape(reportlab_install)}</code><br>'
                               'One package provides Canvas, Platypus and the ReportLab barcode modules. '
                               'PDF helpers are included with EnableScripts.</p>')
                reportlab_group = True
            elif reportlab_group and not is_reportlab:
                content.append('</div>')
                reportlab_group = False
            available, reason = availability(feature)
            selected = key in enabled
            active = key in runtime.ACTIVE
            status = "Active" if active else "Inactive"
            if key in runtime.ERRORS:
                status = "Could not activate: " + runtime.ERRORS[key]
            content.append('<section class="feature">')
            content.append('<div class="feature-title">' + _checkbox(
                "enabled", key, feature.title, selected, not available and not selected))
            content.append(f'<span class="status">{escape(status)}</span></div>')
            content.append(f'<p>{escape(feature.description)}</p>')
            content.append(f'<p class="availability">{escape(reason)}</p>')
            if feature.requires:
                content.append('<p class="dependencies">Requires: ' + escape(
                    ", ".join(FEATURES[k].title for k in feature.requires)) + '</p>')
            if feature.distributions:
                install = "python -m pip install " + " ".join(feature.distributions)
            elif key == "hubarcode":
                install = "python -m pip install hubarcode==1.0.0"
            elif feature.exports:
                install = "Included with Products.EnableScripts; no additional package needed."
            else:
                install = "Python standard library; no additional package needed."
            if not is_reportlab:
                content.append(f'<p class="installation">Install in Zope&#8217;s Python environment: '
                               f'<code>{escape(install)}</code></p>')
            if key == "hubarcode":
                content.append('<p class="hint">Hubarcode 1.0.0 also needs the Python 3 DataMatrix compatibility repair '
                               'described in the project README.</p>')
            for choice, (module, keys) in module_groups(feature).items():
                excluded = keys & disabled
                content.append('<div class="module">' + _checkbox(
                    "modules", choice, module, choice not in disabled and not excluded))
                if excluded and excluded != keys:
                    content.append('<p class="hint">Previously restricted individually. Left unchecked to preserve '
                                   'restrictions; checking this enables the whole listed API.</p>')
                names = tuple(feature.exports) if module == "Products.EnableScripts" else feature.modules.get(module, ())
                preferred = {"io": "BytesIO" if key == "bytesio" else "StringIO",
                             "reportlab.pdfgen.canvas": "Canvas", "reportlab.lib.utils": "ImageReader",
                             "reportlab.lib.pagesizes": "A4", "PIL.Image": "new", "PIL.ImageDraw": "Draw", "PIL.ImageFont": "truetype",
                             "PIL.ImageOps": "fit", "PIL.ImageEnhance": "Contrast",
                             "reportlab.lib.colors": "Color", "reportlab.lib.units": "mm",
                             "reportlab.pdfbase.pdfmetrics": "registerFont", "reportlab.pdfbase.ttfonts": "TTFont",
                             "reportlab.platypus": "SimpleDocTemplate", "reportlab.lib.styles": "getSampleStyleSheet",
                             "reportlab.lib.enums": "TA_CENTER", "reportlab.platypus.flowables": "Spacer",
                             "reportlab.graphics.barcode": "createBarcodeDrawing",
                             "reportlab.graphics.barcode.common": "Barcode",
                             "reportlab.graphics.barcode.code128": "Code128",
                             "reportlab.graphics.barcode.ecc200datamatrix": "ECC200DataMatrix",
                             "xml.etree.ElementTree": "fromstring", "urllib.request": "urlopen",
                             "urllib.parse": "urlencode", "urllib.error": "HTTPError",
                             "http.client": "HTTPConnection",
                             "hubarcode.datamatrix": "DataMatrixEncoder"}
                example = preferred.get(module, next(iter(names), None))
                statement = f"from {module} import {example}" if example else f"import {module}"
                content.append(f'<p class="hint">Import in Script (Python): <code>{escape(statement)}</code></p>')
                content.append('<details class="includes"><summary>Includes</summary>')
                content.append('<p>' + escape(", ".join(names) or "Package namespace") + '</p>')
                for path, members in {**feature.classes, **feature.types}.items():
                    if "object|" + path in keys:
                        content.append(f'<p><strong>{escape(path.replace(":", "."))}</strong>: '
                                       + escape(", ".join(members)) + '</p>')
                content.append('</details></div>')
            content.append('</section>')
        if reportlab_group:
            content.append('</div>')
        content.append('<button type="submit">Save settings</button></form>')
        content.append('<p>Library access includes filesystem paths where supported. '
                       'EnableScripts cannot revoke access granted by other products. '
                       'Remove old GlobalModule/GlobalModules grants when migrating.</p>')
        content.append(self._advanced(settings, user_id))
        installed = sorted({(d.metadata.get("Name", "?"), d.version) for d in metadata.distributions()})
        content.append('<details class="inventory"><summary>Installed Python packages</summary>'
                       '<p>Use Advanced custom libraries to configure modules from additional installed packages.</p>'
                       '<ul>')
        content.extend(f'<li>{escape(name)} {escape(version)}</li>' for name, version in installed)
        content.append('</ul></details></main></body></html>')
        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader("Content-Type", "text/html; charset=utf-8")
            REQUEST.RESPONSE.setHeader("Cache-Control", "no-store")
        return "\n".join(content)

    @zpublish
    @security.protected("Manage properties")
    def manage_save(self, REQUEST, token="", enabled=(), modules=()):
        """Persist selections. Assertions are not changed by this request."""
        app, user_id = self._require_manager()
        if REQUEST.get("REQUEST_METHOD") != "POST":
            raise Forbidden("Use POST to save settings")
        settings = get_settings(app)
        if settings is None or not settings.validate_token(user_id, token):
            raise Forbidden("Invalid or stale form. Reload EnableScripts and try again.")
        groups = {key: keys for feature in FEATURES.values()
                  for key, (_, keys) in module_groups(feature).items()}
        checked = set(_items(modules))
        if not checked <= groups.keys():
            raise BadRequest("Unknown module selection")
        try:
            selected = expand(_items(enabled))
        except ValueError as exc:
            raise BadRequest(str(exc)) from exc
        for key in selected:
            available, reason = availability(FEATURES[key])
            if not available and key not in settings.enabled:
                raise BadRequest(f"{FEATURES[key].title}: {reason}")
        settings.enabled = tuple(selected)
        settings.disabled = tuple(sorted(groups.keys() - checked))
        settings.revision += 1
        # ZPublisher commits the request transaction; no manual commit and no
        # process-local grants here, so aborted requests cannot leak access.
        return REQUEST.RESPONSE.redirect(self.absolute_url() + "/manage_main?saved=1", status=303)

    def _trust_warning(self):
        return ('<aside class="warning"><strong>RestrictedPython is restricted for a reason.</strong>'
                '<p><b>By enabling a library, you are trusting EVERY person who can create or edit '
                'Script (Python) or other restricted Python code anywhere on the affected Zope server.</b> '
                'This includes script authors in other sites and folders, now and in the future, '
                'even if they cannot open this control panel.</p>'
                '<p>Grants apply across the entire Zope process, not just to your account, the current site, '
                'or a particular script. Workers and ZEO clients loading these settings apply the same grants '
                'after restart. Separate Zope instances with separate processes and settings are not automatically changed.</p>'
                '<p>Allowed library code can read or write files, make network requests, consume server resources, '
                'and, depending on the API, run commands with the Zope operating-system account&#8217;s privileges. '
                'These checkboxes are not a sandbox and do not make a library safe. '
                'Do not enable access if you cannot trust all affected script authors with these capabilities.</p></aside>')

    def _advanced(self, settings, user_id):
        from .custom import rules_text
        token = escape(settings.token(user_id), quote=True)
        content = ['<section class="feature" id="advanced"><h2>Advanced: custom libraries</h2>'
                   '<ol><li>Install the package in Zope&#8217;s Python environment and restart if necessary.</li>'
                   '<li>Enter its importable module name, not necessarily its package name: for example, '
                   'the Pillow package uses PIL.Image. Existing preset modules must use their preset controls.</li>'
                   '<li>Click Inspect module. Review the detected exports and remove names you do not want to allow. '
                   'Inspection grants no EnableScripts permissions, but importing a library can execute its startup code.</li>'
                   '<li>If returned objects need access, add explicit class rules using the detected class names. '
                   'Start with only the methods and attributes your script needs.</li>'
                   '<li>Select Enable this module after restart and Save custom policy. Leaving it unchecked stores '
                   'a disabled draft. Restart all workers and check status before testing your script.</li></ol>'
                   '<p>Expose modules from installed packages or the Python standard library. '
                   'Inspection imports the module as ordinary server code and may have side effects. '
                   'Only inspect libraries you trust. No packages are installed here.</p>'
                   '<p>Exports are saved explicitly: new exports after library upgrades are not automatically allowed. '
                   'Returned objects may need class rules. Custom class rules cover exact types, not arbitrary subclasses. '
                   'Overlapping grants from other modules or products can still provide access.</p>']
        for record in getattr(settings, 'custom', ()):
            name, exports, classes = record
            enabled = name in getattr(settings, 'custom_enabled', ())
            active = 'custom:' + name in runtime.ACTIVE
            content.append('<div class="module"><h3>' + escape(name) + '</h3><p>' +
                           ('Active in this process' if active else 'Inactive in this process') + '</p>')
            error = runtime.ERRORS.get('custom:' + name)
            if error:
                content.append('<p class="notice">' + escape(error) + '</p>')
            content.append(f'<p>Import: <code>from {escape(name)} import {escape(exports[0])}</code></p>')
            content.append('<details><summary>Saved exports and object rules</summary><p>' +
                           escape(', '.join(exports)) + '</p><pre>' + escape(rules_text(record)) + '</pre></details>')
            content.append(f'<form method="post" action="manage_custom"><input type="hidden" name="token" value="{token}">'
                           f'<input type="hidden" name="module" value="{escape(name, quote=True)}">'
                           + _checkbox('custom_on', name, 'Enable this module after restart', enabled) +
                           '<p><button name="action" value="toggle">Save activation</button> '
                           '<button name="action" value="remove">Remove custom policy</button></p></form>')
            content.append(f'<form method="post" action="manage_inspect"><input type="hidden" name="token" value="{token}">'
                           f'<input type="hidden" name="module" value="{escape(name, quote=True)}">'
                           '<button type="submit">Inspect / edit policy</button></form></div>')
        content.append(f'<form method="post" action="manage_inspect"><input type="hidden" name="token" value="{token}">'
                       '<p><label>Module to inspect <input name="module" required placeholder="decimal"></label></p>'
                       '<button type="submit">Inspect module</button></form></section>')
        return '\n'.join(content)

    def _custom_request(self, REQUEST, token):
        app, user_id = self._require_manager()
        if REQUEST.get('REQUEST_METHOD') != 'POST':
            raise Forbidden('Use POST for custom library changes or inspection')
        settings = get_settings(app)
        if settings is None or not settings.validate_token(user_id, token):
            raise Forbidden('Invalid or stale form. Reload EnableScripts and try again.')
        return settings, user_id

    @zpublish
    @security.protected('Manage properties')
    def manage_inspect(self, REQUEST, token='', module=''):
        """Inspect installed module exports without granting script access."""
        from .custom import class_catalog, inspect_module, rules_text
        settings, user_id = self._custom_request(REQUEST, token)
        module = module.strip()
        try:
            names = inspect_module(module)
        except Exception as exc:
            raise BadRequest('Cannot inspect module: ' + str(exc)) from exc
        catalog = ''.join('<p><strong>' + escape(path) + '</strong>: ' + escape(', '.join(members)) + '</p>'
                          for path, members in class_catalog(module))
        previous = next((r for r in getattr(settings, 'custom', ()) if r[0] == module), None)
        exports = previous[1] if previous else names
        rules = rules_text(previous) if previous else ''
        enabled = module in getattr(settings, 'custom_enabled', ())
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/html; charset=utf-8')
        REQUEST.RESPONSE.setHeader('Cache-Control', 'no-store')
        return self._header() + self._trust_warning() + f'''
<h2>Inspect custom module: {escape(module)}</h2>
<p>No script permissions have changed. Review the exports and optional class rules before saving.</p>
<p><strong>Custom libraries are untested integrations.</strong> Public functions can access files, networks,
processes and other server resources. Allow only APIs intended for trusted script authors.</p>
<details><summary>Detected public exports ({len(names)})</summary><p>{escape(', '.join(names))}</p></details>
<details><summary>Detected classes and public members</summary>{catalog or "<p>No classes exported by this module.</p>"}</details>
<form method="post" action="manage_custom">
<input type="hidden" name="token" value="{escape(settings.token(user_id), quote=True)}">
<input type="hidden" name="module" value="{escape(module, quote=True)}">
<input type="hidden" name="action" value="save">
<p><label>Allowed exports (space or comma separated)<br>
<textarea name="exports" rows="8" style="width:100%">{escape(' '.join(exports))}</textarea></label></p>
<p><label>Optional object rules (one class per line)<br>
<textarea name="rules" rows="5" style="width:100%" placeholder="decimal:Decimal = quantize as_tuple">{escape(rules)}</textarea></label></p>
<p>For example, export <code>Decimal</code> from <code>decimal</code> and add
<code>decimal:Decimal = quantize as_tuple</code> to let a script call those two methods.
Import with <code>from decimal import Decimal</code>. Granting a class import alone does not
necessarily allow methods on its instances. Object rules do not enable imports from other modules;
inspect and save those modules separately if needed.</p>
<p>Format: <code>module:Class = method attribute</code>. Instance attributes may be listed explicitly.
No wildcards or private names. Classes already managed by a preset must be configured there.</p>
{_checkbox('custom_on', module, 'Enable this module after restart', enabled)}
<p><button type="submit">Save custom policy</button> <a href="manage_main#advanced">Cancel</a></p>
</form></main></body></html>'''

    @zpublish
    @security.protected('Manage properties')
    def manage_custom(self, REQUEST, token='', module='', action='', exports='', rules='', custom_on=()):
        """Save custom policy; security declarations only change at restart."""
        from .custom import validate
        settings, user_id = self._custom_request(REQUEST, token)
        records = {record[0]: record for record in getattr(settings, 'custom', ())}
        enabled = set(getattr(settings, 'custom_enabled', ()))
        if action == 'save':
            try:
                record = validate(module, exports, rules)
                # Two custom entries must not overwrite each other's exact-type policy.
                other_paths = {path for name, entry in records.items() if name != module
                               for path, members in entry[2]}
                from .registry import resolve
                if any(resolve(path) is resolve(other) for path, members in record[2] for other in other_paths):
                    raise ValueError('This class already has rules in another custom policy.')
            except Exception as exc:
                raise BadRequest('Invalid custom policy: ' + str(exc)) from exc
            records[module] = record
        elif action not in ('toggle', 'remove') or module not in records:
            raise BadRequest('Unknown custom policy or action')
        if action == 'remove':
            del records[module]
            enabled.discard(module)
        elif module in _items(custom_on):
            enabled.add(module)
        else:
            enabled.discard(module)
        settings.custom = tuple(records[key] for key in sorted(records))
        settings.custom_enabled = tuple(sorted(enabled))
        settings.revision += 1
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_main?saved=1#advanced', status=303)

    def _header(self):
        return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>EnableScripts</title>
<style>
body{font:15px/1.5 system-ui,sans-serif;background:#f4f6f8;color:#24313f;margin:0}
main{max-width:1050px;margin:28px auto;padding:0 24px 40px}a{color:#245da2}
h1{margin-bottom:4px}h3{font-size:14px;margin:16px 0 7px;overflow-wrap:anywhere}
.feature{background:white;border:1px solid #d3dce5;border-radius:8px;padding:18px;margin:15px 0}
.feature-title{display:flex;gap:20px;align-items:center;justify-content:space-between;font-weight:650;font-size:18px}
.status{font-size:13px;color:#526378}.availability,.dependencies,.hint{color:#526378;font-size:13px}
.library-group{border-left:3px solid #9aafc5;padding-left:18px}.module{border-top:1px solid #e4e9ee;padding:12px 0}.module>label{font-weight:600}.includes{margin-left:22px;font-size:13px;overflow-wrap:anywhere}code{overflow-wrap:anywhere}.choices{display:grid;grid-template-columns:repeat(auto-fit,minmax(195px,1fr));gap:7px 12px;padding:5px 0 12px 22px}
.choices label{overflow-wrap:anywhere}.object{border-top:1px solid #e4e9ee;padding-top:12px;margin-top:12px}
.object>label{font-weight:600;overflow-wrap:anywhere}input{accent-color:#245da2}summary{cursor:pointer;font-weight:600}
.notice{padding:14px;background:#fff1c9;border-left:4px solid #ae7c00}button{background:#245da2;color:white;border:0;border-radius:5px;padding:12px 22px;font:inherit;cursor:pointer}
.warning{padding:16px;background:#fff2ef;border:1px solid #e5aca0;border-radius:6px;margin:18px 0}.warning strong{display:block;margin-bottom:5px}
.inventory{margin-top:25px}.inventory ul{columns:2}.hint{margin:4px 0 8px 22px}
</style></head><body><main><a href="../manage_main">← Zope Control Panel</a>
<h1>EnableScripts</h1><p>Libraries for Script (Python)</p>'''


InitializeClass(EnableScriptsPanel)


def install_panel():
    """Zope 5's Control Panel replaces the old persistent Products UI."""
    if not hasattr(ApplicationManager, "EnableScripts"):
        ApplicationManager.EnableScripts = EnableScriptsPanel()
    action = "EnableScripts/manage_main"
    if not any(item.get("action") == action for item in ApplicationManager.manage_options):
        ApplicationManager.manage_options += ({"label": "EnableScripts", "action": action},)
