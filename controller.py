import threading, os, hmac, hashlib
from model import Model
from io import BytesIO
import qrcode

class Controller:
    def __init__(self):
        self.model = Model()
        self.verified = False
        self.lock_timer = None

    def register(self, password):
        self.model.register(password)
        self.verified = True

    def is_password_correct(self, password):
        if self.model.password_match(password):
            self.verified = True
            return True
        return False

    def get_clipboard_list(self, state=1):
        clips = self.model.get_clip(state)
        return [clip[0] for clip in clips]

    def clip_changed(self, clip):
        return self.model.new_clip(clip)

    def lock_after_seconds(self, timeout):
        if self.lock_timer:
            self.lock_timer.cancel()
        self.lock_timer = threading.Timer(timeout, self.lock_vault)
        self.lock_timer.start()

    def getkeyfile(self):
        return self.model.generate_keyfile()

    def authenticate_keyfile(self, key):
        challenge = os.urandom(16)
        signature = hmac.new(key, challenge, hashlib.sha256).digest()
        return self.model.authenticate_keyfile(signature, challenge)

    def authenticate_totp(self, totp):
        return self.model.authenticate_totp(totp)

    def get_authenticator_secret(self):
        uri = self.model.generate_authenticator_secret()
        buffer = BytesIO()
        qrcode.make(uri).resize((200, 200)).save(buffer, format="PNG")
        return buffer.getvalue()

    def lock_vault(self):
        self.verified = False

    def backup_database(self, backup_path, new_password):
        return self.model.backup_database(backup_path, new_password)

    def restore_database(self, backup_path, password):
        return self.model.restore_database(backup_path, password)
