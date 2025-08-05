import model

class Controller:

    def __init__(self, username):
        self.username = username
        self.model = model.Model(self.username)
        self.locked = True
        self.username = "USER"
        self.hashpass = "PASS"

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
