import model
import threading, os, hmac, hashlib, qrcode
from io import BytesIO

class Controller:

    def __init__(self):
        self.model = model.Model()
        self.verified = False
        self.lock_timer = None

    def register(self, password):
        self.model.register(password)

    def is_password_correct(self, password):
        self.verified = self.model.password_match(password)
        return self.verified

    def get_clipboard_list(self, state=1):
        clips = self.model.get_clip(state)
        return [clip[0] for clip in clips]

    def clip_changed(self, clip):
        self.model.new_clip(clip)

    def lock_after_seconds(self, timeout):
        if self.lock_timer:
            self.lock_timer.close()
        self.lock_timer = threading.Timer(timeout, lock_vault)
        self.lock_timer.start()

    def getkeyfile(self):
        return self.model.generate_keyfile()

    def authenticate_keyfile(self, key):
        challange = os.urandom(16)
        signature = hmac.new(key, challange, hashlib.sha256).digest()
        return self.model.authenticate_keyfile(signature, challange)

    def authenticate_totp(self, totp):
        return self.model.authenticate_totp(totp)

    def get_authenticator_secret(self):
        uri = self.model.generate_authenticator_secret()
        buffer = BytesIO()
        qrcode.make(uri).resize((200,200)).save(buffer, format="PNG")
        return buffer.getvalue()

    def lock_vault(self):
        self.verified = False
