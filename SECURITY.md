# Security model

**RestrictedPython is restricted for a reason. EnableScripts deliberately
widens the capabilities available to restricted Zope scripts.** It is intended
for servers where script authors are trusted by the server administrator.

Enabling a library is a trust decision, not a declaration that the library is
safe to expose to untrusted users.

## Scope of the grants

* Module declarations and type/class policies are global to a Python process.
  They affect other sites and restricted execution contexts using that process,
  not just the folder or user that opened the panel.
* Functions inside an allowed third-party library run as ordinary Python code.
  They can perform operations that the calling restricted script could not do
  directly. Examples include file access via Pillow or ReportLab and network or
  local URL access via urllib.
* The separate extended-io integration exposes filesystem constructors/functions.
  Enable BytesIO alone when you only need in-memory streams.
* The checkboxes are attribute/import controls. They are not argument filters,
  capability isolation, resource quotas, or a defense against hostile Python.
  Alternative APIs can perform equivalent operations even if one method is off.
* Image/PDF parsing and rendering can consume substantial memory or CPU.
  Use deployment-level resource controls for untrusted inputs.
* Other products may grant overlapping access. EnableScripts cannot guarantee
  revocation when another product, startup hook or trusted code changes policies.
* A library upgrade can introduce new public names. Discovered subchoices default
  to enabled, as do all subchoices in this product. Review upgrades accordingly.

## Administration and persistence

The panel explicitly requires Manager at the Zope application root. Changes use
POST and a per-ZODB secret with a user/revision-bound CSRF token. Stale forms are
rejected. Saved settings only affect newly started worker processes. Restart
every worker, including ZEO clients, before relying on a newly restricted policy.

Normal Zope permissions still govern access to Zope objects. The image-storage
helper explicitly checks image creation/replacement permissions. Allowing library
functions does not add role-based access control inside those third-party APIs.

## Reporting

Use the repository's private vulnerability reporting feature:
https://github.com/fixader/Products.EnableScripts/security/advisories/new

For ordinary bugs, use GitHub Issues. Do not include credentials, real documents,
customer data, or exploit details in a public issue.
