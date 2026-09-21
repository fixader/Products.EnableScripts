"""Persistent selections; the actual AccessControl assertions are process-local."""

import hashlib
import hmac
import secrets

from persistent import Persistent

SETTINGS_ATTRIBUTE = "_enable_scripts_settings"


class Settings(Persistent):
    def __init__(self):
        self.custom = ()
        self.custom_enabled = ()
        self.enabled = ()
        self.disabled = ()
        self.revision = 0
        self.secret = secrets.token_bytes(32)

    def token(self, user_id):
        payload = f"{user_id}\n{self.revision}".encode("utf-8")
        return hmac.new(self.secret, payload, hashlib.sha256).hexdigest()

    def validate_token(self, user_id, token):
        return isinstance(token, str) and hmac.compare_digest(self.token(user_id), token)


def get_settings(app, create=False):
    settings = getattr(app, SETTINGS_ATTRIBUTE, None)
    if settings is None and create:
        settings = Settings()
        setattr(app, SETTINGS_ATTRIBUTE, settings)
    return settings
