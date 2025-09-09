import sqlcipher3, os, hashlib, hmac, base64, pyotp
from io import BytesIO
import qrcode

class Model:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "database")
        self.keyfile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "keyfile")
        self.authenticator_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "authenticator")
        self.connection = None
        self.db_password = None
        self.offset = 0

    def register(self, password):
        connection = sqlcipher3.connect(self.db_path)
        connection.execute(f"pragma key = '{password}';")
        connection.execute("""
            create table if not exists clips (
                id integer primary key autoincrement,
                clip text
            );
        """)
        connection.commit()
        connection.close()
        with open(self.authenticator_path, 'wb') as f:
            f.write(self.authenticator.encode())
        with open(self.keyfile_path, 'wb') as f:
            f.write(self.keyfile)
        return True

    def generate_keyfile(self):
        self.keyfile = os.urandom(32)
        return self.keyfile

    def password_match(self, password):
        if not os.path.exists(self.db_path):
            return False
        try:
            self.connection = sqlcipher3.connect(self.db_path)
            self.connection.execute(f"pragma key = '{password}';")
            self.connection.execute("select * from sqlite_master")
            return True
        except:
            return False

    def new_clip(self, clip):
        cursor = self.connection.cursor()
        cursor.execute("insert into clips (clip) values (?);", (clip,))
        self.connection.commit()

    def get_clip(self, state=1):
        num = 5
        cursor = self.connection.cursor()
        command = """
            select clip
            from clips
            order by id desc
            limit ? offset ?;
        """
        if state == 1:
            return cursor.execute(command, (num, self.offset)).fetchall()
        elif state == 2:
            next_offset = self.offset + 5
            clips = cursor.execute(command, (num, next_offset)).fetchall()
            if clips:
                self.offset = next_offset
                return clips
            else:
                return cursor.execute(command, (num, self.offset)).fetchall()
        elif state == 3:
            if self.offset >= 5:
                self.offset -= 5
            return cursor.execute(command, (num, self.offset)).fetchall()

    def authenticate_keyfile(self, signature, challenge):
        with open(self.keyfile_path, "rb") as f:
            key = f.read()
            expected_signature = hmac.new(key, challenge, hashlib.sha256).digest()
        return hmac.compare_digest(signature, expected_signature)

    def generate_authenticator_secret(self):
        self.authenticator = pyotp.random_base32()
        self.totp = pyotp.TOTP(self.authenticator)
        uri = self.totp.provisioning_uri(name='sudo', issuer_name='enclipt')
        return uri

    def authenticate_totp(self, totp):
        with open(self.authenticator_path, 'rb') as f:
            self.totp = pyotp.TOTP(f.read().decode())
        return self.totp.now() == totp

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
