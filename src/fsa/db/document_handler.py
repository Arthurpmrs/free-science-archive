import sqlite3
import traceback
from ..domain import Paper, Author, Publisher, Book, Document

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

    def insert_author(self, author: Author, cur: Cursor | None = None) -> int:
        """Insert a new author into the database"""

        commit = False
        if not cur:
            commit = True
            cur = self.con.cursor()

        try:
            cur.execute("""
                        INSERT INTO Author
                        VALUES(:author_id, :last_name, :remaining_name, 
                        :birth_date, :email, :social_url, :nationality,
                        :created_at)
                        """, author.get_parsed_dict())
            author_id = cur.lastrowid

            if commit:
                self.con.commit()

        except sqlite3.IntegrityError:
            print("This Author already exists.")

            res = cur.execute("""
                            SELECT author_id FROM Author
                            WHERE last_name = ? AND remaining_name = ?
                            """, (author.last_name, author.remaining_name))

            author_id = res.fetchone()[0]

        return author_id

    def link_author(self, author_id: int, document_id: int, cur: Cursor) -> None:
        """Link an author to a document"""

        try:
            cur.execute("""
                        INSERT INTO Writes VALUES(?, ?)
                        """, (document_id, author_id))
        except sqlite3.IntegrityError:
            print("This author is already linked to this document.")

    def _insert_document(self, parsed_document: dict, type: str,
                         cur: Cursor) -> tuple[bool, int]:
        """Insert a new document into the database"""

        parsed_document.update({"type": type})

        try:
            cur.execute("""
                        INSERT INTO Document
                        VALUES(:document_id, :title, :language, :year, 
                        :publisher_id, :created_at, :type)
                        """, parsed_document)

            document_id = cur.lastrowid
            success = True
        except sqlite3.IntegrityError:
            print("This Document already exists.")

            res = cur.execute("""
                        SELECT document_id FROM Document
                        WHERE title = ? AND year = ?
                        """, (parsed_document.get("title"),
                              parsed_document.get("year")))

            document_id = res.fetchone()[0]
            success = False

        return success, document_id

    def insert_paper(self, paper: Paper) -> int:
        """Insert a new paper into the database"""

        publisher_id = self.insert_publisher(paper.publisher)

        parsed_paper = paper.get_parsed_dict()
        parsed_paper.update({"publisher_id": publisher_id})

        self.con.isolation_level = None
        cur = self.con.cursor()
        cur.execute("BEGIN")
        success, document_id = self._insert_document(
            parsed_paper, "paper", cur)

        if not success:
            return document_id

        parsed_paper.update({"document_id": document_id})

        cur.execute("""
                    INSERT INTO Paper
                    VALUES(:document_id, :doi, :journal, :issue, :pages, 
                    :volume)
                    """, parsed_paper)

        for author in paper.authors:
            author_id = self.insert_author(author, cur)
            self.link_author(author_id, document_id, cur)

        self.con.commit()

        return document_id

    def insert_book(self, book: Book) -> int:
        """Insert a new book into the database"""

        publisher_id = self.insert_publisher(book.publisher)

        parsed_book = book.get_parsed_dict()
        parsed_book.update({"publisher_id": publisher_id})

        self.con.isolation_level = None
        cur = self.con.cursor()
        cur.execute("BEGIN")
        success, document_id = self._insert_document(parsed_book, "book", cur)

        if not success:
            return document_id

        parsed_book.update({"document_id": document_id})

        cur.execute("""
                    INSERT INTO Book
                    VALUES(:document_id, :isbn, :edition, :publication_place)
                    """, parsed_book)

        for author in book.authors:
            author_id = self.insert_author(author, cur)
            self.link_author(author_id, document_id, cur)

        self.con.commit()

        return document_id

    def set_document_publisher(self, document_id: int, publisher_id: int) -> None:
        """Update the publisher of a document"""

        cur = self.con.cursor()

        try:
            cur.execute("""
                        UPDATE Document
                        SET publisher_id = ?
                        WHERE document_id = ?
                        """, (publisher_id, document_id))
        except sqlite3.IntegrityError:
            print("This Document does not exist.")

        self.con.commit()

    def _get_document_authors(self, document_id: int) -> list[Author]:
        """Get all authors of a document"""

        cur = self.con.cursor()

        rows = cur.execute("""
                            SELECT Author.* FROM Author
                            INNER JOIN Writes
                                ON Writes.author_id = Author.author_id
                                AND Writes.document_id = ?                                   
                            """, (document_id, ))

        authors: list[Author] = []
        for row in rows:
            authors.append(Author.from_db_row(dict(row)))

        return authors

    def get_document_by_id(self, document_id: int) -> Document:
        """Get a document by its id"""

        cur = self.con.cursor()

        rows = cur.execute("""
                        SELECT 
                            Document.created_at AS doc_created_at,
                            Publisher.created_at AS pub_created_at,
                            * 
                            FROM Document
                        INNER JOIN Publisher
                            ON Document.publisher_id = Publisher.publisher_id
                            AND Document.document_id = ?
                        LEFT JOIN Book
                            ON Document.document_id = Book.document_id
                        LEFT JOIN Paper
                            ON Document.document_id = Paper.document_id
                        """, (document_id,))

        data = dict(rows.fetchone())
        if data["type"] == "book":
            document = Book.from_db_row(data)
        else:
            document = Paper.from_db_row(data)

        document.authors = self._get_document_authors(document_id)

        return document

    def get_documents_by_author(self, last_name: str) -> list[Document]:
        """Get all documents written by an author"""

        rows = self.con.execute("""
                                SELECT Writes.document_id from Author
                                INNER JOIN Writes
                                    ON Writes.author_id = Author.author_id 
                                    AND Author.last_name = ?
                                """, (last_name, ))

        documents: list[Document] = []
        for row in rows:
            documents.append(self.get_document_by_id(row["document_id"]))

        return documents

    def get_documents_by_publisher(self, name: str) -> list[Document]:
        """Get all documents published by a publisher"""

        rows = self.con.execute("""
                                SELECT 
                                    Document.created_at AS doc_created_at,
                                    Publisher.created_at AS pub_created_at,
                                    *
                                    FROM Document
                                INNER JOIN Publisher
                                    ON Publisher.publisher_id = Document.publisher_id
                                    AND Publisher.name = ?
                                """, (name, ))

        documents: list[Document] = []
        for row in rows:
            data = dict(row)
            if data["type"] == "book":
                document = Book.from_db_row(data)
            else:
                document = Paper.from_db_row(data)

            document.authors = self._get_document_authors(data["document_id"])

            documents.append(document)
        return documents

    def get_book_by_id(self, document_id: int) -> Book:
        """Get a book by its id"""

        document = self.get_document_by_id(document_id)
        if isinstance(document, Book):
            return document
        else:
            raise ValueError("This document is not a book.")

    def get_books(self) -> list[Book]:
        """Get all books"""

        rows = self.con.execute("""
                                SELECT Document.document_id FROM Document
                                INNER JOIN Book
                                ON Document.document_id = Book.document_id
                                AND Document.type = "book"
                                """)

        books: list[Book] = []
        for row in rows:
            books.append(self.get_document_by_id(row["document_id"]))

        return books

    def get_papers(self) -> list[Paper]:
        """Get all papers"""

        rows = self.con.execute("""
                                SELECT Document.document_id FROM Document
                                INNER JOIN Paper
                                ON Document.document_id = Paper.document_id
                                AND Document.type = "paper"
                                """)

        papers: list[Paper] = []
        for row in rows:
            papers.append(self.get_document_by_id(row["document_id"]))

        return papers

    def get_paper_by_id(self, document_id: int) -> Paper:
        """Get a paper by its id"""

        document = self.get_document_by_id(document_id)
        if isinstance(document, Paper):
            return document
        else:
            raise ValueError("This document is not a paper.")

    def get_author_by_id(self, author_id: int) -> Author:
        """Get an author by its id"""

        cur = self.con.cursor()

        rows = cur.execute("""
                        SELECT * FROM Author
                        WHERE author_id = ?
                        """, (author_id,))

        author = Author.from_db_row(dict(rows.fetchone()))

        docs = cur.execute("""
                           SELECT Document.document_id FROM Document
                           INNER JOIN Writes
                                ON Writes.document_id = Document.document_id 
                                AND Writes.author_id = ?
                            """, (author_id,))

        for doc in docs:
            author.document_ids.append(doc["document_id"])

        return author

    def get_publisher_by_id(self, publisher_id: int) -> Publisher:
        """Get a publisher by its id"""

        cur = self.con.cursor()

        rows = cur.execute("""
                        SELECT * FROM Publisher
                        WHERE publisher_id = ?
                        """, (publisher_id,))

        publisher = Publisher.from_db_row(dict(rows.fetchone()))

        docs = cur.execute("""
                           SELECT Document.document_id FROM Document
                           WHERE Document.publisher_id = ?
                           """, (publisher_id,))

        for doc in docs:
            publisher.document_ids.append(doc["document_id"])

        return publisher

    def update_publisher(self, publisher: Publisher) -> None:
        """Update a publisher"""

        cur = self.con.cursor()

        try:
            cur.execute("""
                        UPDATE Publisher
                        SET name = ?, address = ?, url = ?
                        WHERE publisher_id = ?
                        """, (publisher.name, publisher.address,
                              publisher.url, publisher.publisher_id))
        except sqlite3.IntegrityError:
            print("This Publisher does not exist.")

        self.con.commit()

    def update_author(self, author: Author) -> None:
        """Update an author"""

        cur = self.con.cursor()

        try:
            cur.execute("""
                        UPDATE Author
                        SET last_name = ?, remaining_name = ?, birth_date = ?,
                        email = ?, social_url = ?, nationality = ?
                        WHERE author_id = ?
                        """, (author.last_name, author.remaining_name,
                              author.birth_date, author.email, author.social_url,
                              author.nationality, author.author_id))
        except sqlite3.integrityError:
            print("This Author does not exist.")

        self.con.commit()

    def update_document(self, document: Document) -> None:
        """Update a document"""

        cur = self.con.cursor()

        try:
            cur.execute("""
                        UPDATE Document
                        SET title = ?, language = ?, year = ?
                        WHERE document_id = ?
                        """, (document.title, document.language,
                              document.year, document.document_id))
        except sqlite3.IntegrityError:
            print("This Document does not exist.")
            return None

        if isinstance(document, Book):
            try:
                cur.execute("""
                            UPDATE Book
                            SET isbn = ?, edition = ?, publication_place = ?
                            WHERE document_id = ?
                            """, (document.isbn, document.edition,
                                  document.publication_place,
                                  document.document_id))
            except sqlite3.IntegrityError:
                print("This Book does not exist.")
                return None
        else:
            try:
                cur.execute("""
                            UPDATE Paper
                            SET doi = ?, journal = ?, issue = ?, pages = ?,
                            volume = ?
                            WHERE document_id = ?
                            """, (document.doi, document.journal,
                                  document.issue, document.pages,
                                  document.volume, document.document_id))
            except sqlite3.IntegrityError:
                print("This Paper does not exist.")
                return None

        self.con.commit()

    def delete_publisher(self, publisher_id: int) -> None:
        """Delete a publisher"""

        self.con.isolation_level = None
        try:
            cur = self.con.cursor()
            cur.execute("BEGIN")

            cur.execute("""
                        DELETE FROM Publisher
                        WHERE publisher_id = ?
                        """, (publisher_id,))

            self.con.commit()
        except sqlite3.Error:
            print("Something went wrong. Transaction cancelled")
            print(traceback.format_exc())
            self.con.rollback()

    def delete_author(self, author_id: int) -> None:
        """Delete an author"""

        self.con.isolation_level = None
        try:
            cur = self.con.cursor()
            cur.execute("BEGIN")

            cur.execute("""
                        DELETE FROM Writes
                        WHERE author_id = ?
                        """, (author_id, ))

            cur.execute("""
                        DELETE FROM Author
                        WHERE author_id = ?
                        """, (author_id,))

            self.con.commit()
        except sqlite3.Error:
            print("Something went wrong. Transaction cancelled")
            print(traceback.format_exc())
            self.con.rollback()

    def delete_document(self, document_id: int) -> None:
        """Delete a document"""

        self.con.isolation_level = None
        try:
            cur = self.con.cursor()
            cur.execute("BEGIN")
            is_books = True
            rows = cur.execute("""
                               SELECT document_id from Book
                               WHERE document_id = ?
                               """, (document_id, ))

            is_book = False if not rows.fetchone() else True

            if is_book:
                table = "Book"
            else:
                table = "Paper"

            subtype_del_query = f"DELETE FROM {table} WHERE document_id = ?"
            cur.execute(subtype_del_query, (document_id, ))

            cur.execute("""
                        DELETE FROM Writes
                        WHERE document_id = ?
                        """, (document_id, ))

            cur.execute("""
                        DELETE FROM Document
                        WHERE document_id = ?
                        """, (document_id, ))

            self.con.commit()

        except sqlite3.Error:
            print(traceback.format_exc())
            print("Something went Wrong. Transaction Cancelled.")
            self.con.rollback()
