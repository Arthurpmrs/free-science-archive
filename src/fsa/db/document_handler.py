import sqlite3
from ..domain import Paper, Author, Publisher

Cursor = sqlite3.Cursor


class DocumentHandler:

    def __init__(self, con):
        self.con = con

    def insert_publisher(self, publisher: Publisher) -> int:
        """Insert a new publisher into the database"""

        cur = self.con.cursor()

        cur.execute("""
                    INSERT OR IGNORE INTO Publisher
                    VALUES(:publisher_id, :name, :address, :url, :created_at)
                    """, publisher.get_parsed_dict())

        self.con.commit()

        res = cur.execute("""
                        SELECT publisher_id FROM Publisher
                        WHERE name = ?
                        """, (publisher.name,))

        return res.fetchone()[0]

    def insert_author(self, author: Author, cur: Cursor,
                      document_id: int | None = None) -> int:
        """Insert a new author into the database"""

        cur.execute("""
                    INSERT INTO Author
                    VALUES(:author_id, :last_name, :remaining_name, 
                    :birth_date, :email, :social_url, :nationality,
                    :created_at)
                    """, author.get_parsed_dict())

        res = cur.execute("""
                        SELECT author_id FROM Author
                        WHERE last_name = ? AND remaining_name = ?
                        """, (author.last_name, author.remaining_name))

        author_id = res.fetchone()[0]

        if document_id:
            cur.execute("""
                        INSERT INTO Writes VALUES(?, ?)
                        """, (document_id, author_id))

        return author_id

    def insert_paper(self, paper: Paper) -> int:
        """Insert a new paper into the database"""

        publisher_id = self.insert_publisher(paper.publisher)

        parsed_paper = paper.get_parsed_dict()
        parsed_paper.update({"publisher_id": publisher_id})

        self.con.isolation_level = None
        cur = self.con.cursor()
        cur.execute("BEGIN")
        try:
            cur.execute("""
                        INSERT INTO Document
                        VALUES(:document_id, :title, :language, :year, 
                        :publisher_id, :created_at)
                        """, parsed_paper)

            paper.document_id = cur.lastrowid
        except sqlite3.IntegrityError:
            print("This Document already exists.")

            res = cur.execute("""
                        SELECT document_id FROM Document
                        WHERE title = ? AND year = ?
                        """, (paper.title, paper.year))

            return res.fetchone()[0]

        cur.execute("""
                    INSERT INTO Paper
                    VALUES(:document_id, :doi, :journal, :issue, :pages, 
                    :volume)
                    """, paper.get_parsed_dict())

        for author in paper.authors:
            self.insert_author(author, cur, paper.document_id)

        self.con.commit()

        return paper.document_id
