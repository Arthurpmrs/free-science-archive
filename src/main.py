import json
import time
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
            print("\n###################### INFO ######################")
            if self.logged_user:
                print(f"Logged in as: {self.logged_user.username}")
            else:
                print(f"Not logged in.")
            print("\n###################### MENU ######################")
            print("1. Login")
            print("2. Register")
            if self.logged_user:
                print("3. Add Publisher")
                print("4. Add Author")
                print("5. Add Book")
                print("6. Add Paper")
                print("7. Link Document to an existing Author")
                print("8. Link Document to an existing Publisher")
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
                self.add_document("book")
            elif option == "6":
                self.add_document("paper")
            elif option == "7":
                self.link_document_to_author()
            elif option == "0":
                break
            elif option == "98":
                add_admin()
            elif option == "99":
                self.populate_database()
            else:
                print(">> Invalid option. Try again.")

    def login(self) -> None:
        username = input("Username: ")
        password = input("Password: ")

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            user = handler.get_user_by_username(username)

            if user is None or user.password != password:
                print(">> Invalid credentials.")
            else:
                self.logged_user = user
                print(">> Logged in successfully.")

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

    def add_document(self, doc_type: str) -> None:
        if self.logged_user is None:
            print(">> You must be logged in to add a book.")
            return None

        user_id = self.logged_user.user_id
        title = input("Title: ")
        language = input("Language: ")
        year = input("Year: ")

        if doc_type == "book":
            isbn = input("ISBN: ")
            edition = input("Edition: ")
            publication_place = input("Publication place: ")

            document = Book(
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
        else:
            doi = input("DOI: ")
            journal = input("Journal: ")
            issue = input("Issue: ")
            pages = input("Pages: ")
            volume = input("Volume: ")

            document = Paper(
                title=title,
                language=language,
                tags=[],
                year=year,
                publisher=None,
                doi=doi,
                journal=journal,
                issue=issue,
                pages=pages,
                volume=volume,
                authors=[],
            )

        with DatabaseConnector() as con:
            handler = DBHandler(con)

            if doc_type == "book":
                document_id = handler.insert_book(document, user_id)
            else:
                document_id = handler.insert_paper(document, user_id)

            add_publisher = input("Add publisher? (y/n): ")
            if add_publisher == "y":
                publisher_id = self.add_publisher()
            else:
                publisher_id = None

            handler.set_document_publisher(document_id, publisher_id)

        add_authors = input("Add authors? (y/n): ")
        while add_authors == "y":
            author_id = self.add_author()
            print(document_id, author_id)
            with DatabaseConnector() as con:
                handler = DBHandler(con)
                handler.link_author(author_id, document_id)
            add_authors = input("Add another author? (y/n): ")

        print("Book added successfully.")

    def link_document_to_author(self) -> None:
        if self.logged_user is None:
            print(">> You must be logged in to add a book.")
            return None

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            document_id = input("Document ID: ")
            print("\nSelected Document: ")
            print(handler.get_document_by_id(document_id).title)

            authors = handler.get_authors()
            print("\nFetching authors...")
            time.sleep(3)

            print("\nAuthors: ")
            for author in authors:
                print(
                    f"{author.author_id}: {author.last_name}, {author.remaining_name}")
            author_id = input("Author ID: ")
            handler.link_author(author_id, document_id)

    def populate_database(self) -> None:
        if self.logged_user is None:
            print(">> You must be logged in to add a book.")
            return None

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            admin = handler.get_user_by_username("admin")

        populate_papers(admin.user_id)
        populate_books(admin.user_id)


if __name__ == "__main__":
    app = Application()
    app.run()
