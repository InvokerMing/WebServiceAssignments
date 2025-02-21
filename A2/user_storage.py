import sqlite3
from contextlib import closing

class UserStorage:
    def __init__(self, db_path="urls.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with closing(self._get_conn()) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS token_blacklist (
                    token TEXT PRIMARY KEY,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')
            conn.commit()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def add_user(self, username, password_hash):
        with closing(self._get_conn()) as conn:
            try:
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_user(self, username):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute(
                "SELECT id, password_hash FROM users WHERE username = ?",
                (username,)
            )
            return cursor.fetchone()

    def update_user_password(self, username, new_password_hash):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (new_password_hash, username)
            )
            conn.commit()
            return cursor.rowcount > 0
        
    def is_token_blacklisted(self, token):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM token_blacklist WHERE token = ? AND expires_at > CUREENT_TIMESTAMP",
                (token,)
            )
            return cursor.fetchone() is not None