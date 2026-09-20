from io import BytesIO

from OFS.Folder import Folder
from OFS.Image import manage_addImage
from PIL import Image
import pytest
from zExceptions import Unauthorized

from Products.EnableScripts import zope_helpers


class ImageFolder(Folder):
    manage_addImage = manage_addImage


def png(color):
    output = BytesIO()
    Image.new("RGB", (2, 2), color).save(output, "PNG")
    return output.getvalue()


class Permissions:
    def __init__(self, denied=None):
        self.denied = denied

    def checkPermission(self, permission, context):
        return permission != self.denied


def test_image_creation_replacement_and_permissions(monkeypatch):
    folder = ImageFolder("images")
    permissions = Permissions()
    monkeypatch.setattr(zope_helpers, "getSecurityManager", lambda: permissions)
    original = zope_helpers.save_image_object(folder, "picture", png("red"), "First", "image/png")
    assert original.getContentType() == "image/png"
    permissions.denied = "Change Images and Files"
    with pytest.raises(Unauthorized):
        zope_helpers.save_image_object(folder, "picture", png("blue"))
    assert folder.picture.title == "First"
    permissions.denied = None
    zope_helpers.save_image_object(folder, "picture", png("blue"), "Updated", "image/png")
    assert folder.picture.title == "Updated"
    assert bytes(folder.picture.data) == png("blue")
    permissions.denied = "Add Documents, Images, and Files"
    with pytest.raises(Unauthorized):
        zope_helpers.save_image_object(folder, "second", png("red"))
    assert "second" not in folder.objectIds()
