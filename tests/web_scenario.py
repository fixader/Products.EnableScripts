"""A real Zope WSGI request cycle and FileStorage across process restarts."""

import base64
from pathlib import Path
import sys

import transaction
from webtest import TestApp
from Zope2.Startup.run import make_wsgi_app
from zExceptions import BadRequest, Forbidden


def expect_http_error(call, status, exception):
    # A minimal Zope instance may have no HTML exception view installed.
    # In that case WSGIPublisher re-raises the same HTTP exception.
    try:
        response = call()
    except exception:
        return
    assert response.status_int == status


def main(folder, phase):
    root = Path(folder)
    config = root / "zope.conf"
    if phase == "initial":
        (root / "var").mkdir()
        (root / "etc").mkdir()
        config.write_text(f'''instancehome {root.as_posix()}
clienthome {(root / "var").as_posix()}
security-policy-implementation C
debug-exceptions off
<zodb_db main>
  <filestorage>
    path {(root / "var" / "Data.fs").as_posix()}
  </filestorage>
  mount-point /
</zodb_db>
''')
    app = TestApp(make_wsgi_app({}, str(config)), extra_environ={"x-wsgiorg.throw_errors": False})
    import Zope2
    from Products.EnableScripts import runtime
    from Products.EnableScripts.policy import module_groups
    from Products.EnableScripts.registry import FEATURES
    from Products.EnableScripts.settings import get_settings
    from scenario import run, denied

    if phase == "initial":
        root_app = Zope2.app()
        root_app.acl_users._doAddUser("testmanager", "testpassword", ["Manager"], [])
        root_app.acl_users._doAddUser("testreader", "testpassword", [], [])
        transaction.commit()
        root_app._p_jar.close()
    path = "/Control_Panel/EnableScripts/manage_main"
    save_path = "/Control_Panel/EnableScripts/manage_save"
    auth = "Basic " + base64.b64encode(b"testmanager:testpassword").decode()
    reader = "Basic " + base64.b64encode(b"testreader:testpassword").decode()
    headers = {"Authorization": auth}
    app.get(path, status=401)
    app.get(path, headers={"Authorization": reader}, status=401)
    page = app.get(path, headers=headers, status=200)
    assert "EnableScripts" in page.text
    assert "no-store" == page.headers["Cache-Control"]
    token = page.html.find("input", {"name": "token"})["value"]
    groups = {key: keys for f in FEATURES.values() for key, (_, keys) in module_groups(f).items()}
    disabled_module = "module|reportlab|reportlab.lib.pagesizes"
    details = groups.keys() - {disabled_module}
    params = [("token", token)] + [("modules:list", key) for key in sorted(details)]
    assert page.html.html["lang"] == "en"
    assert not page.html.select('input[name="details:list"]')
    assert len(page.html.select('input[name="modules:list"]')) == len(groups)
    pdf_group = page.html.select_one('.library-group')
    assert {i["value"] for i in pdf_group.select('input[name="enabled:list"]')} == {
        "reportlab", "platypus", "barcodes", "pdf_helpers"}
    assert "from reportlab.pdfgen.canvas import Canvas" in page.text
    assert "python -m pip install reportlab" in page.text
    if phase == "initial":
        assert not runtime.ACTIVE
        expect_http_error(lambda: app.get(save_path, headers=headers, expect_errors=True), 403, Forbidden)
        expect_http_error(lambda: app.post(save_path, {"token": "invalid"}, headers=headers, expect_errors=True), 403, Forbidden)
        expect_http_error(lambda: app.post(save_path, [("token", token), ("enabled:list", "unknown")], headers=headers, expect_errors=True), 400, BadRequest)
        params.append(("enabled:list", "reportlab"))
        response = app.post(save_path, params, headers=headers, status=303)
        assert not runtime.ACTIVE, "Saving must not mutate process security"
        expect_http_error(lambda: app.post(save_path, params, headers=headers, expect_errors=True), 403, Forbidden)  # stale token
        saved = response.follow(headers=headers)
        assert "Restart required" in saved.text
        root_app = Zope2.app()
        settings = get_settings(root_app)
        assert settings.enabled == ("bytesio", "reportlab")
        assert settings.disabled == (disabled_module,)
        root_app._p_jar.close()
        (root / "panel.html").write_text(saved.text, encoding="utf-8")
    elif phase == "restart":
        assert runtime.ACTIVE == {"bytesio", "reportlab"}
        assert "Restart required" not in page.text
        assert run("from io import BytesIO\nb=BytesIO(b'yes')\nreturn b.read()") == b"yes"
        denied("from reportlab.lib.pagesizes import A4\nreturn A4")
        assert run("from io import BytesIO\nfrom reportlab.pdfgen.canvas import Canvas\nb=BytesIO()\nc=Canvas(b)\nc.drawString(10,10,'ok')\nc.save()\nreturn b.getvalue()").startswith(b"%PDF")
        app.post(save_path, params, headers=headers, status=303)
        assert runtime.ACTIVE == {"bytesio", "reportlab"}, "Disabling takes effect after restart"
    elif phase == "disabled_again":
        assert not runtime.ACTIVE
        denied("from io import BytesIO\nreturn BytesIO()")
        root_app = Zope2.app()
        settings = get_settings(root_app)
        assert settings.disabled == (disabled_module,), "Subchoices must survive disabling"
        root_app._p_jar.close()
    else:
        raise ValueError(phase)
    print("WSGI phase passed:", phase)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
