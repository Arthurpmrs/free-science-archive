import json
from datetime import datetime
from fsa.db.base import DatabaseConnector
from fsa.db.document_handler import DocumentHandler
from fsa.domain import Publisher, Book, Paper, Author


def populate_papers():
    papers = []
    with open("src/fakedata/papers.json", "r") as file:
        raw_papers = json.load(file)

        for raw_paper in raw_papers:
            papers.append(Paper.from_raw_data(raw_paper))

    for paper in papers:
        with DatabaseConnector() as con:
            handler = DocumentHandler(con)
            handler.insert_paper(paper)


def populate_books():
    books = []
    with open("src/fakedata/books.json", "r") as file:
        raw_books = json.load(file)
        for raw_book in raw_books:
            books.append(Book.from_raw_data(raw_book))

    for book in books:
        print(f"{book.authors[0].last_name} - {book.title}")
        with DatabaseConnector() as con:
            handler = DocumentHandler(con)
            handler.insert_book(book)


def insert_standalone_authors():
    from datetime import datetime

    authors = [
        Author(remaining_name='John',
               last_name='Doe',
               birth_date=datetime(1990, 5, 1),
               email='john.doe@example.com',
               social_url='http://john.doe.com',
               nationality='American',
               document_ids=[],
               ),
        Author(remaining_name='Jane',
               last_name='Doe',
               birth_date=datetime(1992, 6, 2),
               email='jane.doe@example.com',
               social_url='http://jane.doe.com',
               nationality='American',
               document_ids=[],
               ),
        Author(remaining_name='Al',
               last_name='Sweigart',
               birth_date=datetime(1991, 7, 3),
               email='sweigart@gmail.con',
               social_url='http://sweigart.com',
               nationality='American',
               document_ids=[],
               )
    ]

    with DatabaseConnector() as con:
        handler = DocumentHandler(con)
        for author in authors:
            print(author)
            handler.insert_author(author)


def insert_standalone_publisher():
    publisher = Publisher(
        name="Microsoft Press",
        address=None,
        url="https://www.microsoftpressstore.com/",
        document_ids=[]
    )

    with DatabaseConnector() as con:
        handler = DocumentHandler(con)
        handler.insert_publisher(publisher)


def update_document_publisher():
    with DatabaseConnector() as con:
        handler = DocumentHandler(con)
        # 13 is the Book: Introduction do Algorithms on the database
        # 20 is the Publisher: Microsoft Press
        handler.update_document_publisher(13, 20)


def test_query():
    with DatabaseConnector() as con:
        rows = con.execute("""
                    SELECT Document.created_at AS doc_created_at,
                    Publisher.created_at AS pub_created_at,
                    * FROM Paper
                    INNER JOIN Document
                    ON Paper.document_id = Document.document_id
                    INNER JOIN Publisher
                    ON Document.publisher_id = Publisher.publisher_id
                    """)

        for row in rows:
            data = dict(row)
            print(data)
            paper = Paper.from_db_row(data)
            print(paper)
            break
            # publisher_id = data["publisher_id"]
            # res = con.execute("""
            #                   SELECT document_id FROM Document
            #                   WHERE publisher_id = ?
            #                   """, (publisher_id,))
            # print([dict(r)["document_id"] for r in list(res.fetchall())])


def test_query_2():
    with DatabaseConnector() as con:
        rows = con.execute("""
                           SELECT 
                                Document.created_at AS doc_created_at,
                                Publisher.created_at AS pub_created_at, 
                                * 
                                FROM Author
                           INNER JOIN Writes
                           ON Author.author_id = Writes.author_id
                           AND Author.last_name = ?
                           INNER JOIN Document
                           ON Writes.document_id = Document.document_id
                           LEFT JOIN Book
                           ON Document.document_id = Book.document_id
                           LEFT JOIN Paper
                           ON Document.document_id = Paper.document_id
                           """, ("Fowler",))
        for row in rows:
            data = dict(row)
            print(data)


def test_query_3():
    with DatabaseConnector() as con:
        handler = DocumentHandler(con)
        # document = handler.get_document_by_id(8)
        # print(document)
        # documents = handler.get_documents_by_author("Ribeiro")
        # documents = handler.get_documents_by_publisher("Elsevier")
        # documents = handler.get_books()
        # documents = handler.get_papers()
        # for document in documents:
        #     print(document.title)

        # author = handler.get_author_by_id(26)
        # print(author)
        # author.email = "marcio@ic.ufal.br"
        # author.social_url = "@gabarito"
        # print(author)
        # handler.update_author(author)
        # publisher = handler.get_publisher_by_id(15)
        # print(publisher)
        # publisher.address = "Rua Juquinha, 1255"
        # print(publisher)
        # handler.update_publisher(publisher)
        # publisher = handler.get_publisher_by_id(15)
        # print(publisher)
        # book = handler.get_book_by_id(21)
        # book = handler.get_book_by_id(21)
        # print(book)
        # book.publication_place = "Boca Raton"
        # print(" ")
        # handler.update_document(book)
        # book = handler.get_book_by_id(21)
        # print(book)
        paper = handler.get_paper_by_id(6)
        paper.pages = "1-10"
        paper.doi = "10.1016/j.jss.2000.1x11x1"
        print(paper)
        handler.update_document(paper)


if __name__ == "__main__":
    # populate_papers()
    # populate_books()
    test_query_3()
