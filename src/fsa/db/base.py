import sqlite3
from pathlib import Path

Connection = sqlite3.Connection


class DatabaseConnector:
    DB_PATH: Path = Path("fsa.db")

    def __init__(self):
        self.con = sqlite3.connect(self.DB_PATH)
        self.con.row_factory = sqlite3.Row
        DatabaseConnector.create_tables(self.con)

    def __enter__(self):
        return self.con

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        self.con.close()

    @staticmethod
    def create_tables(con) -> None:
        cur = con.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS Publisher (
                        publisher_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        address TEXT,
                        url TEXT,
                        created_at DATE
                        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS Document (
                        document_id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        language TEXT,
                        year INTEGER,
                        publisher_id INTEGER,
                        created_at DATE,
                        UNIQUE(title, year)
                        FOREIGN KEY (publisher_id) REFERENCES Publisher (publisher_id)
                        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS Book (
                        document_id INTEGER PRIMARY KEY,
                        isbn TEXT UNIQUE,
                        edition TEXT,
                        publication_place TEXT,
                        FOREIGN KEY (document_id) REFERENCES Publisher (document_id)
                        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS Paper (
                        document_id INTEGER PRIMARY KEY,
                        doi TEXT UNIQUE,
                        journal TEXT,
                        issue TEXT,
                        pages TEXT,
                        volume TEXT,
                        FOREIGN KEY (document_id) REFERENCES Publisher (document_id)
                        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS Author (
                        author_id INTEGER PRIMARY KEY,
                        last_name TEXT,
                        remaining_name TEXT,
                        birth_date DATE,
                        email TEXT,
                        social_url TEXT,
                        nationality TEXT,
                        created_at DATE,
                        UNIQUE(last_name, remaining_name)
                        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS Writes (
                        document_id INTEGER,
                        author_id INTEGER,
                        PRIMARY KEY (document_id, author_id)
                        FOREIGN KEY (document_id) REFERENCES Document (document_id),
                        FOREIGN KEY (author_id) REFERENCES Author (author_id)
                        )""")
