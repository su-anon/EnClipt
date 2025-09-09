import sqlcipher3, os, hashlib, hmac

class Model:

    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "database")
        self.connection = None
        self.db_password = None
        self.offset = 0

    def register(self, password):
        connection = sqlcipher3.connect(self.db_path)

        connection.execute(f"pragma key = '{self.db_password}';")

        connection.execute("""
            create table if not exists clips (
                id   integer primary key autoincrement,
                clip text
            );
        """)
        connection.commit()
        connection.close()
        return True

    def generate_keyfile(self):
        secret = os.urandom(32)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "keyfile"), "wb") as f:
            f.write(secret)
        return secret

    def login(self, password):
        if not os.path.exists(self.db_path):
            return False
        try:
            self.connection = sqlcipher3.connect(self.db_path)
            self.connection.execute(f"pragma key = '{password}';")
            self.connection.execute("select * from sqlite_master")
            print("Logged in..")
            return True
        except:
            print("Login failed..")
            return False

    def new_clip(self, clip):
        cursor = self.connection.cursor()
        cursor.execute("insert into clips (clip) values (?);", (CLIP,))
        self.connection.commit()

    def get_clip(self, forward=True):
        cursor = self.connection.cursor()
        command = """
                select clip
                from clips
                order by id desc
                limit ? offset ?;
            """
        if not forward:
            if self.offset>=5:
                self.offset -= 5
            cursor.execute(command, (num,self.offset))
            return cursor.fetchall()

        if forward:
            cursor.execute(command, (num,self.offset+5))
            clips = cursor.fetchall()
            if clips:
                self.offset += 5
            else:
                return cursor.execute(command, (num, self.offset)).fetchall()

    def authenticate_keyfile(self, signature, challange):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "keyfile"), "rb") as f:
            key = f.read()
            expected_signature = hmac.new(key, challange, hashlib.sha256).digest()
        return hmac.compare_digest(signature, expected_signature)

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
