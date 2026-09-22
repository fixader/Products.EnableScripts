"""Trusted helper, retaining the caller's Zope permissions."""

from AccessControl import getSecurityManager
from AccessControl.Permissions import add_documents_images_and_files, change_images_and_files, delete_objects
from zExceptions import Unauthorized


def save_image_object(folder, object_id, image_bytes, title="", content_type="image/jpeg"):
    manager = getSecurityManager()
    if not manager.checkPermission(add_documents_images_and_files, folder):
        raise Unauthorized("Add Documents, Images, and Files permission required")
    object_id = str(object_id)
    if object_id in folder.objectIds():
        if not manager.checkPermission(delete_objects, folder):
            raise Unauthorized("Delete objects permission required to replace an image")
        existing = folder._getOb(object_id)
        if getattr(existing, "meta_type", None) != "Image":
            raise ValueError("Refusing to replace a non-image object")
        if not manager.checkPermission(change_images_and_files, existing):
            raise Unauthorized("Change Images and Files permission required")
        # Preserve existing metadata and references when replacing an image.
        existing.manage_edit(title=title, content_type=content_type, filedata=image_bytes)
        return existing
    folder.manage_addImage(id=object_id, file=image_bytes, title=title, content_type=content_type)
    return folder._getOb(object_id)
