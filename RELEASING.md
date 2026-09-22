# Publishing to PyPI

The repository is prepared for **manual Trusted Publishing**. Pushing code or
creating a tag does not publish the package.

## One-time setup

Sign in to your PyPI account and create a pending publisher:

| Field | Value |
|---|---|
| Project name | `Products.RestrictedPythonExtensions` |
| Owner | `fixader` |
| Repository | `Products.RestrictedPythonExtensions` |
| Workflow | `publish.yml` |
| Environment | `pypi` |

Create the equivalent publisher on TestPyPI using environment `testpypi`.
PyPI and TestPyPI are separate services and need separate configuration.
No API token needs to be stored in the repository.

Official instructions:
[Create a project through Trusted Publishing](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
and [publish with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/).

## Release

1. Update the version in `pyproject.toml`, changelog and relevant install examples.
2. Confirm CI passes and validate the package on a Zope test instance.
3. Tag that commit as `vVERSION` and push the tag.
4. Run **Publish package** from that tag, selecting `testpypi` first.
5. Verify TestPyPI metadata and install the wheel in a disposable Zope environment.
6. Run the same workflow/tag with `pypi` when ready to publish publicly.

The workflow requires a tag matching the package version, runs the test matrix,
builds and checks wheel/sdist, then publishes using the selected environment.
It does not run automatically on tags or releases.

Retain the RestrictedPython warning prominently in both readmes and in the
package's PyPI description. Review newly discovered names when upgrading any
optional library, because new subchoices default to enabled.
