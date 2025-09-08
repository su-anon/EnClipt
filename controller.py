import model
import threading

class Controller:

    def __init__(self, username):
        self.username = username
        self.model = model.Model(self.username)
        self.locked = True
        self.username = "USER"
        self.hashpass = "PASS"
        self.lock_timer = None

    def register(self, username, hashpass):
        self.username = username
        self.hashpass = hashpass

    def login(self, username, hashpass):
        if username==self.username and hashpass==self.hashpass:
            self.locked = False

    def get_clipboard_list(self):
        clips = self.model.get_clip(5)
        return [clip[0] for clip in clips]

    def clip_changed(self, clip):
        self.model.new_clip(clip)

    def lock_after_seconds(self, timeout):
        if self.lock_timer:
            self.lock_timer.close()
        self.lock_timer = threading.Timer(timeout, lock_vault)
        self.lock_timer.start()

    def lock_vault(self):
        self.locked = True
