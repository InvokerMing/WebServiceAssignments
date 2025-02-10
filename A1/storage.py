import sqlite3
from contextlib import closing

class UrlStorage:
    def __init__(self, db_path="urls.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with closing(self._get_conn()) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_url TEXT NOT NULL,
                    short_code TEXT UNIQUE NOT NULL
                )
            ''')
            conn.commit()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def add_url(self, original_url, short_code):
        with closing(self._get_conn()) as conn:
            try:
                cursor = conn.execute(
                    "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
                    (original_url, short_code)
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None

    def get_url(self, url_id):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute(
                "SELECT original_url FROM urls WHERE id = ?",
                (url_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def update_url(self, url_id, new_url):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute(
                "UPDATE urls SET original_url = ? WHERE id = ?",
                (new_url, url_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_url(self, url_id):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute(
                "DELETE FROM urls WHERE id = ?",
                (url_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_all_urls(self):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute("SELECT id, original_url FROM urls")
            return [{"id": row[0], "value": row[1]} for row in cursor.fetchall()]

    def delete_all(self):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute("DELETE FROM urls")
            conn.commit()
            return cursor.rowcount # return the number of deleted rows
        
    def count_codes_by_length(self, length):
        with closing(self._get_conn()) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM urls WHERE LENGTH(short_code) = ?",
                (length,)
            )
            result = cursor.fetchone
            return cursor.fetchone()[0] if result else 0