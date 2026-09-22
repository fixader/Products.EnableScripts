import base64
from pathlib import Path
import sys
import transaction
from webtest import TestApp
from Zope2.Startup.run import make_wsgi_app
from zExceptions import BadRequest, Forbidden
from web_scenario import expect_http_error

folder, phase = sys.argv[1:]
root = Path(folder)
config = root / 'zope.conf'
if phase == 'initial':
    (root / 'var').mkdir()
    config.write_text('instancehome ' + root.as_posix() + '\n<zodb_db main>\n<filestorage>\npath ' +
                      (root / 'var/Data.fs').as_posix() + '\n</filestorage>\nmount-point /\n</zodb_db>\n')
app = TestApp(make_wsgi_app({}, str(config)), extra_environ={'x-wsgiorg.throw_errors': False})
import Zope2
from Products.RestrictedPythonExtensions import runtime
from Products.RestrictedPythonExtensions.settings import get_settings
from scenario import run, denied
if phase == 'initial':
    db = Zope2.app()
    db.acl_users._doAddUser('manager', 'password', ['Manager'], [])
    db.acl_users._doAddUser('reader', 'password', [], [])
    transaction.commit(); db._p_jar.close()
headers = {'Authorization': 'Basic ' + base64.b64encode(b'manager:password').decode()}
base = '/Control_Panel/RestrictedPythonExtensions/'
def page():
    return app.get(base+'manage_main', headers=headers)
def token():
    return page().html.find('input', {'name':'token'})['value']
def post(action='save', rules='extra_library:Widget = read value', **changes):
    data = dict(token=token(), action=action, module='extra_library', exports='make', rules=rules)
    data['custom_on:list'] = 'extra_library'
    data.update(changes)
    return app.post(base+'manage_custom', data, headers=headers, status=303)
if phase == 'initial':
    denied('from extra_library import make\nreturn make()')
    for endpoint in ('manage_custom','manage_inspect'):
        app.post(base+endpoint, {}, status=401)
        reader = {'Authorization': 'Basic ' + base64.b64encode(b'reader:password').decode()}
        app.post(base+endpoint, {}, headers=reader, status=401)
        expect_http_error(lambda: app.get(base+endpoint, headers=headers, expect_errors=True),403,Forbidden)
        expect_http_error(lambda: app.post(base+endpoint, {'token':'wrong'}, headers=headers, expect_errors=True),403,Forbidden)
    preview = app.post(base+'manage_inspect', {'token':token(),'module':'extra_library'},headers=headers)
    assert 'Detected public exports' in preview.text
    assert not preview.html.select('input[checked]'), 'Inspection must not enable modules'
    denied('from extra_library import make\nreturn make()')
    for exports,rules in [('missing',''), ('make','extra_library:Widget = _private'), ('make','io:BytesIO = read')]:
        expect_http_error(lambda: app.post(base+'manage_custom',dict(token=token(),action='save',module='extra_library',exports=exports,rules=rules),headers=headers,expect_errors=True),400,BadRequest)
    old = token();post()
    denied('from extra_library import make\nreturn make()')
    expect_http_error(lambda: app.post(base+'manage_custom',dict(token=old,action='remove',module='extra_library'),headers=headers,expect_errors=True),403,Forbidden)
    assert 'Restart required' in page().text
elif phase == 'enabled':
    assert 'custom:extra_library' in runtime.ACTIVE
    assert run('from extra_library import make\nreturn make().read()') == 'hello'
    denied('from extra_library import Widget\nreturn Widget()')
    denied('from extra_library import make\nreturn make().write("no")')
    # Saving preset controls must preserve custom policies.
    form = page().html.find('form', {'action':'manage_save'})
    params=[(i['name'],i['value']) for i in form.find_all('input') if i.get('type')=='hidden' or i.has_attr('checked')]
    app.post(base+'manage_save',params,headers=headers,status=303)
    assert 'extra_library' in page().text
    post(rules='extra_library:Widget = write value')
    assert run('from extra_library import make\nreturn make().read()') == 'hello'
elif phase == 'edited':
    denied('from extra_library import make\nreturn make().read()')
    assert run('from extra_library import make\nreturn make().write("yes")') == 'yes'
    post(action='remove')
    assert run('from extra_library import make\nreturn make().write("still active")') == 'still active'
elif phase == 'removed':
    denied('from extra_library import make\nreturn make()')
    assert 'custom:extra_library' not in runtime.ACTIVE
    db=Zope2.app();assert not get_settings(db).custom;db._p_jar.close()
print('Custom policy phase passed:',phase)
