import json
from fsa.db.base import DatabaseConnector
from fsa.db.handler import DBHandler
from fsa.domain import Publisher, Book, Paper, Author, User


def add_admin():
    user = User(
        username="admin",
        password="admin",
        email="admin@admin.com"
    )

    with DatabaseConnector() as con:
        handler = DBHandler(con)
        admin_id = handler.insert_user(user)

    return admin_id


def populate_books(user_id: int):
    books = []
    with open("src/fakedata/books.json", "r") as file:
        raw_books = json.load(file)
        for raw_book in raw_books:
            books.append(Book.from_raw_data(raw_book))

    for book in books:
        print(f"{book.authors[0].last_name} - {book.title}")
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            handler.insert_book(book, user_id)


def populate_papers(user_id: int):
    papers = []
    with open("src/fakedata/papers.json", "r") as file:
        raw_papers = json.load(file)

        for raw_paper in raw_papers:
            papers.append(Paper.from_raw_data(raw_paper))

    for paper in papers:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            handler.insert_paper(paper, user_id)


class Application:

    logged_user: User | None = None

    def run(self) -> None:

        while True:
            print("1. Login")
            print("2. Register")
            print("3. Add Publisher")
            print("4. Add Author")
            print("5. Add Book")
            # print("6. Add Paper")
            print("98. Add Admin")
            print("99. Populate database with fake data")
            print("0. Exit")
            option = input("Choose an option: ")

            if option == "1":
                self.login()
            elif option == "2":
                self.register()
            elif option == "3":
                self.add_publisher()
            elif option == "4":
                self.add_author()
            elif option == "5":
                self.add_book()
            elif option == "0":
                break
            elif option == "98":
                add_admin()
            elif option == "99":
                self.populate_database()
            else:
                print("Invalid option. Try again.")

    def login(self) -> None:
        username = input("Username: ")
        password = input("Password: ")

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            user = handler.get_user_by_username(username)

            if user is None or user.password != password:
                print("Invalid credentials.")
            else:
                self.logged_user = user
                print("Logged in successfully.")

    def register(self) -> None:
        email = input("Email: ")
        username = input("Username: ")
        password = input("Password: ")

        user = User(
            username=username,
            password=password,
            email=email
        )

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            handler.insert_user(user)
            print("User registered successfully.")

    def add_publisher(self) -> int:
        name = input("Name: ")
        address = input("Address: ")
        url = input("url: ")

        publisher = Publisher(
            name=name,
            address=address,
            url=url,
            document_ids=[]
        )

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            publisher_id = handler.insert_publisher(publisher)
            print("Publisher added successfully.")

        return publisher_id

    def add_author(self) -> int:
        last_name = input("Last name: ")
        remaining_names = input("Remaining names: ")
        birth_date = input("Birth date: ")
        email = input("Email: ")
        social_url = input("Social network url: ")
        nationality = input("Nationality: ")

        author = Author(
            last_name=last_name,
            remaining_name=remaining_names,
            birth_date=birth_date,
            email=email,
            social_url=social_url,
            nationality=nationality,
            document_ids=[]
        )

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            author_id = handler.insert_author(author)
            print("Author added successfully.")

        return author_id

    def add_book(self) -> None:
        if self.logged_user is None:
            print("You must be logged in to add a book.")
            return None

        user_id = self.logged_user.user_id
        title = input("Title: ")
        language = input("Language: ")
        year = input("Year: ")
        isbn = input("ISBN: ")
        edition = input("Edition: ")
        publication_place = input("Publication place: ")

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            book = Book(
                title=title,
                language=language,
                tags=[],
                year=year,
                publisher=None,
                isbn=isbn,
                edition=edition,
                publication_place=publication_place,
                authors=[],
            )

            document_id = handler.insert_book(book, user_id)

            add_publisher = input("Add publisher? (y/n): ")
            if add_publisher == "y":
                publisher_id = self.add_publisher()
            else:
                publisher_id = None

            handler.set_document_publisher(document_id, publisher_id)

            add_authors = input("Add authors? (y/n): ")
            while add_authors == "y":
                author_id = self.add_author()
                with DatabaseConnector() as con:
                    handler = DBHandler(con)
                    handler.link_author(document_id, author_id)
                add_authors = input("Add another author? (y/n): ")

            print("Book added successfully.")

    def populate_database(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            admin = handler.get_user_by_username("admin")

        populate_papers(admin.user_id)
        populate_books(admin.user_id)


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
        handler = DBHandler(con)
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
        handler = DBHandler(con)
        handler.insert_publisher(publisher)


def update_document_publisher():
    with DatabaseConnector() as con:
        handler = DBHandler(con)
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
        handler = DBHandler(con)
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
        # paper = handler.get_paper_by_id(6)
        # paper.pages = "1-10"
        # paper.doi = "10.1016/j.jss.2000.1x11x1"
        # print(paper)
        # handler.update_document(paper)
        # handler.delete_publisher(7)


def test_query_4():
    with DatabaseConnector() as con:
        handler = DBHandler(con)
        # handler.delete_author(41)
        # print(handler.get_document_by_id(16))
        handler.delete_document(2)


if __name__ == "__main__":
    app = Application()
    app.run()
