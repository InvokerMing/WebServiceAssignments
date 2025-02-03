import sqlite3
from contextlib import closing

class UrlStorage:
    def __init__(self, db_path='urls.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with closing(self._get_conn()) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_url TEXT NOT NULL,
                    short_code TEXT UNIQUE NOT NULL,
                    visits INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def add_url(self, original_url, short_code):
        with closing(self._get_conn()) as conn:
            try:
                conn.execute(
                    'INSERT INTO urls (original_url, short_code) VALUES (?, ?)',
                    (original_url, short_code)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_url(self, short_code):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute(
                'SELECT original_url FROM urls WHERE short_code = ?',
                (short_code,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def increment_visits(self, short_code):
        with closing(self._get_conn()) as conn:
            conn.execute(
                'UPDATE urls SET visits = visits + 1 WHERE short_code = ?',
                (short_code,)
            )
            conn.commit()

    def get_stats(self, short_code):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute(
                'SELECT visits FROM urls WHERE short_code = ?',
                (short_code,)
            )
            result = cursor.fetchone()
            return result[0] if result else None