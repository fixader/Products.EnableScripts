# Security model

**RestrictedPython is restricted for a reason.**

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
* The checkboxes select supported module APIs. They are not argument filters,
  capability isolation, resource quotas, or a defense against hostile Python.
  Alternative APIs can perform equivalent operations through other enabled modules.
* Image/PDF parsing and rendering can consume substantial memory or CPU.
  Use deployment-level resource controls for untrusted inputs.
* Other products may grant overlapping access. EnableScripts cannot guarantee
  revocation when another product, startup hook or trusted code changes policies.
* A library upgrade can introduce new public names. Discovered preset exports in
  enabled modules default to enabled. Custom exports are frozen when saved, but
  implementations of already permitted functions can still change. Disabled
  modules stay disabled. Review upgrades accordingly.
* Inspecting a custom module imports it as ordinary Python code and can execute
  initialization with side effects. Inspect only trusted installed libraries.
  Inspection itself does not add EnableScripts access declarations.
* Custom rules authorize exact object types and explicit public names. They are
  not argument validation and do not guarantee arbitrary libraries will work.

## Choosing the boundary

EnableScripts is intended for educational exploration, rapid prototyping and
other environments with a small, controlled group of trusted script authors.
Group size does not limit what an allowed library can do. If any affected author
is untrusted, use an appropriately isolated environment or a narrower interface.

A reviewed External Method or filesystem product can expose a specific operation
with argument validation and permission checks, rather than broad library access.
External Methods execute unrestricted code too; their safety depends on their
implementation, not their name.

The administrator accepts responsibility for the grants and their consequences.
The software is provided as is, without warranty, under the disclaimer and
limitation of liability in [LICENSE](LICENSE). No security guarantee is made for
an arbitrary library or a particular deployment.

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
