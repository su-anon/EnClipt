import model
import threading, os, hmac, hashlib

class Controller:

    def __init__(self):
        self.model = model.Model()
        self.verified = False
        self.lock_timer = None

    def register(self, password):
        self.model.register(password)

    def login(self, username, hashpass):
        self.verified = self.model.login(password)

    def get_clipboard_list(self):
        clips = self.model.get_clip(forward=True)
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

    def lock_vault(self):
        self.verified = False
