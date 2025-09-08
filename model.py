import sqlite3
import os

class Model:

    def __init__(self, username):
        self.db_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), f"model/{username}.db"
                )
        self.connection = sqlite3.connect(self.db_path)
        self.init_db()

    def init_db(self):
        self.connection.execute("""
            create table if not exists clips (
                id integer primary key autoincrement,
                clip text
            );
        """)

    def new_clip(self, clip):
        cursor = self.connection.cursor()
        cursor.execute("""
            insert into clips (clip) values (?)
        """, (clip,))
        self.connection.commit()

    def get_clip(self, num):
        cursor = self.connection.cursor()
        cursor.execute("""
            select clip from clips order by id desc limit (?) offset 0
        """, (num,))
        clips = cursor.fetchall()
        return clips

    def close(self):
        self.connection.close()
