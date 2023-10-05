import sys
import json
import time
from fsa.db.base import DatabaseConnector
from fsa.db.handler import DBHandler
from fsa.domain import Publisher, Book, Paper, Author, User


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


def check_go_back() -> None:
    confirm = input("Go back to menu? (y/n) ")
    if confirm == "y":
        return None
    else:
        sys.exit()


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
                print("9. Update entity")
                print("10. Delete entity")
                print("11. Get documents by author")
                print("12. Get all books")
                print("13. Get all papers")
                print("14. Get all publishers")
                print("15. Get all authors")
                print("16. Get all users")
                print("17. Update user")
                print("18. Delete user")
                print("19. Get Book by ID")
                print("20. Get Paper by ID")
                print("100. Logout")

            print("0. Exit")

            if self.logged_user and self.logged_user.username == "admin":
                print("\n##################### ADMIN ######################")
                print("9999. Populate database with fake data")

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
            elif option == "8":
                self.link_document_to_publisher()
            elif option == "9":
                self.update_entity()
            elif option == "10":
                self.delete_entity()
            elif option == "11":
                self.get_documents_by_author()
            elif option == "12":
                self.get_all_books()
            elif option == "13":
                self.get_all_papers()
            elif option == "14":
                self.get_all_publishers()
            elif option == "15":
                self.get_all_authors()
            elif option == "16":
                self.get_all_users()
            elif option == "17":
                self.update_user()
            elif option == "18":
                self.delete_user()
            elif option == "19":
                self.get_book_by_id()
            elif option == "20":
                self.get_paper_by_id()
            elif option == "100":
                self.logged_user = None
                print(">> Logged out successfully.")
            elif option == "9999":
                self.populate_database()
            elif option == "0":
                break
            else:
                print(">> Invalid option. Try again.")

    def login(self) -> None:
        username = input("Username: ")
        password = input("Password: ")

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            try:
                user = handler.get_user_by_username(username)
            except Exception:
                user = None

            if user is None or user.password != password:
                print(">> Invalid credentials.")
                return check_go_back()
            else:
                self.logged_user = user
                print(">> Logged in successfully.")

    def _login_as_admin(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            admin = handler.get_user_by_username("admin")
            self.logged_user = admin

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

    def link_document_to_publisher(self) -> None:
        if self.logged_user is None:
            print(">> You must be logged in to add a book.")
            return None

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            document_id = input("Document ID: ")
            print("\nSelected Document: ")
            try:
                print(handler.get_document_by_id(document_id).title)
            except ValueError:
                print(">> Invalid document ID.")
                return None

            publishers = handler.get_publishers()
            print("\nFetching publishers...")
            time.sleep(3)

            print("\nPublishers: ")
            for publisher in publishers:
                print(f"{publisher.publisher_id}: {publisher.name}")
            publisher_id = input("Publisher ID: ")
            handler.set_document_publisher(document_id, publisher_id)

    def update_entity(self) -> None:
        if self.logged_user is None:
            print(">> You must be logged in to add a book.")
            return None

        print("\n##################### UPDATE #####################")
        print("1. Update a book")
        print("2. Update a paper")
        print("3. Update a publisher")
        print("4. Update an author")
        option = input("Choose an option: ")

        if option == "1":
            self.update_book()
        elif option == "2":
            self.update_paper()
        elif option == "3":
            self.update_publisher()
        elif option == "4":
            self.update_author()
        else:
            print(">> Invalid option.")

    def update_book(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            books = handler.get_books()
            print("\nFetching books...")
            time.sleep(3)

            print("\nBooks: ")
            for book in books:
                print(f"{book.document_id}: {book.title}")
            book_id = input("Book ID: ")

            book = handler.get_book_by_id(book_id)
            print("\nSelected book: ")
            print(book.title)

            title = input("Title: ")
            language = input("Language: ")
            year = input("Year: ")
            isbn = input("ISBN: ")
            edition = input("Edition: ")
            publication_place = input("Publication place: ")

            book.title = title
            book.language = language
            book.year = year
            book.isbn = isbn
            book.edition = edition
            book.publication_place = publication_place

            handler.update_document(book)
            print("Book updated successfully.")

    def update_paper(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            papers = handler.get_papers()
            print("\nFetching papers...")
            time.sleep(3)

            print("\nPapers: ")
            for paper in papers:
                print(f"{paper.document_id}: {paper.title}")
            paper_id = input("Paper ID: ")

            paper = handler.get_paper_by_id(paper_id)
            print("\nSelected paper: ")
            print(paper.title)

            title = input("Title: ")
            language = input("Language: ")
            year = input("Year: ")
            doi = input("DOI: ")
            journal = input("Journal: ")
            issue = input("Issue: ")
            pages = input("Pages: ")
            volume = input("Volume: ")

            paper.title = title
            paper.language = language
            paper.year = year
            paper.doi = doi
            paper.journal = journal
            paper.issue = issue
            paper.pages = pages
            paper.volume = volume

            handler.update_document(paper)
            print("Paper updated successfully.")

    def update_author(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            authors = handler.get_authors()
            print("\nFetching authors...")
            time.sleep(3)

            print("\nAuthors: ")
            for author in authors:
                print(
                    f"{author.author_id}: {author.last_name}, {author.remaining_name}")

            author_id = input("Author ID: ")
            author = handler.get_author_by_id(author_id)
            print("\nSelected author: ")
            print(f"{author.last_name}, {author.remaining_name}")

            last_name = input("Last name: ")
            remaining_names = input("Remaining names: ")
            birth_date = input("Birth date: ")
            email = input("Email: ")
            social_url = input("Social network url: ")
            nationality = input("Nationality: ")

            author.last_name = last_name
            author.remaining_name = remaining_names
            author.birth_date = birth_date
            author.email = email
            author.social_url = social_url
            author.nationality = nationality

            handler.update_author(author)
            print("Author updated successfully.")

    def update_publisher(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            publishers = handler.get_publishers()
            print("\nFetching publishers...")
            time.sleep(3)

            print("\nPublishers: ")
            for publisher in publishers:
                print(f"{publisher.publisher_id}: {publisher.name}")

            publisher_id = input("Publisher ID: ")
            publisher = handler.get_publisher_by_id(publisher_id)
            print("\nSelected publisher: ")
            print(publisher.name)

            name = input("Name: ")
            address = input("Address: ")
            url = input("url: ")

            publisher.name = name
            publisher.address = address
            publisher.url = url

            handler.update_publisher(publisher)
            print("Publisher updated successfully.")

    def update_user(self) -> None:
        if self.logged_user is None:
            print(">> You must be logged in.")
            return None

        print(f"You are logged in as: {self.logged_user.username}")
        with DatabaseConnector() as con:
            handler = DBHandler(con)

            user = handler.get_user_by_username(self.logged_user.username)

            email = input("Email: ")
            username = input("Username: ")
            password = input("Password: ")

            user.email = email
            user.username = username
            user.password = password

            handler.update_user(user)
            print("User updated successfully.")

    def delete_entity(self) -> None:
        if self.logged_user is None:
            print(">> You must be logged in to add a book.")
            return None

        print("\n##################### DELETE #####################")
        print("1. Delete a book")
        print("2. Delete a paper")
        print("3. Delete a publisher")
        print("4. Delete an author")

        option = input("Choose an option: ")

        if option == "1":
            self.delete_book()
        elif option == "2":
            self.delete_paper()
        elif option == "3":
            self.delete_publisher()
        elif option == "4":
            self.delete_author()
        else:
            print(">> Invalid option.")

    def delete_book(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            books = handler.get_books()
            print("\nFetching books...")
            time.sleep(3)

            print("\nBooks: ")
            for book in books:
                print(f"{book.document_id}: {book.title}")
            book_id = input("Book ID: ")
            confirm = input("Are you sure? (y/n) ")
            if confirm:
                handler.delete_document(book_id)
                print("Book deleted successfully.")
            else:
                print("Operation canceled.")
                return None

    def delete_paper(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            papers = handler.get_papers()
            print("\nFetching papers...")
            time.sleep(3)

            print("\nPapers: ")
            for paper in papers:
                print(f"{paper.document_id}: {paper.title}")
            paper_id = input("Paper ID: ")
            confirm = input("Are you sure? (y/n) ")
            if confirm == "y":
                handler.delete_document(paper_id)
                print("paper deleted successfully.")
            else:
                print("Operation canceled.")
                return None

    def delete_author(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            authors = handler.get_authors()
            print("\nFetching authors...")
            time.sleep(3)

            print("\nAuthors: ")
            for author in authors:
                print(
                    f"{author.author_id}: {author.last_name}, {author.remaining_name}")
            author_id = input("Author ID: ")
            confirm = input("Are you sure? (y/n) ")
            if confirm == "y":
                handler.delete_author(author_id)
                print("Author deleted successfully.")
            else:
                print("Operation canceled.")
                return None

    def delete_publisher(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            publishers = handler.get_publishers()
            print("\nFetching publishers...")
            time.sleep(3)

            print("\nPublishers: ")
            for publisher in publishers:
                print(f"{publisher.publisher_id}: {publisher.name}")
            publisher_id = input("Publisher ID: ")
            confirm = input("Are you sure? (y/n) ")
            if confirm == "y":
                handler.delete_publisher(publisher_id)
                print("Publisher deleted successfully.")
            else:
                print("Operation canceled.")
                return None

    def delete_user(self) -> None:
        if self.logged_user is None:
            print(">> You must be logged in.")
            return None

        print(f"You are logged in as: {self.logged_user.username}")
        with DatabaseConnector() as con:
            handler = DBHandler(con)

            confirm = input("Are you sure? (y/n) ")
            if confirm == "y":
                handler.delete_user(self.logged_user.user_id)
                self.logged_user = None
                print("User deleted successfully.")
            else:
                print("Operation canceled.")
                return None

    def populate_database(self) -> None:
        if self.logged_user is None:
            print(">> You must be logged in to add a paper.")
            return None

        with DatabaseConnector() as con:
            handler = DBHandler(con)
            admin = handler.get_user_by_username("admin")

        populate_papers(admin.user_id)
        populate_books(admin.user_id)

    def get_documents_by_author(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            authors = handler.get_authors()
            print("\nFetching authors...")
            time.sleep(3)

            print("\nAuthors: ")
            for author in authors:
                print(
                    f"{author.author_id}: {author.last_name}, {author.remaining_name}")
            author_id = input("Author ID: ")

            target_author = None
            for author in authors:
                if author.author_id == int(author_id):
                    target_author = author
                    break

            documents = handler.get_documents_by_author(
                target_author.last_name)
            print("\nDocuments: ")
            for document in documents:
                print(f"{document.document_id}: {document.title}")

            print("Documents fetched successfully.")

    def get_all_books(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            books = handler.get_books()
            print("\nFetching books...")
            time.sleep(3)

            print("\nBooks: ")
            for book in books:
                print(f"{book.document_id}: {book.title}")

        return check_go_back()

    def get_all_papers(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            papers = handler.get_papers()
            print("\nFetching papers...")
            time.sleep(3)

            print("\nPapers: ")
            for paper in papers:
                print(f"{paper.document_id}: {paper.title}")

        return check_go_back()

    def get_all_publishers(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            publishers = handler.get_publishers()
            print("\nFetching publishers...")
            time.sleep(3)

            print("\nPublishers: ")
            for publisher in publishers:
                print(f"{publisher.publisher_id}: {publisher.name}")

        return check_go_back()

    def get_all_authors(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            authors = handler.get_authors()
            print("\nFetching authors...")
            time.sleep(3)

            print("\nAuthors: ")
            for author in authors:
                print(
                    f"{author.author_id}: {author.last_name}, {author.remaining_name}")

        return check_go_back()

    def get_all_users(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            users = handler.get_users()
            print("\nFetching users...")
            time.sleep(3)

            print("\nUsers: ")
            for user in users:
                print(f"{user.user_id}: {user.username}")

        return check_go_back()

    def get_book_by_id(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            books = handler.get_books()
            print("\nFetching books...")
            time.sleep(3)

            print("\nBooks: ")
            for book in books:
                print(f"{book.document_id}: {book.title}")
            book_id = input("Book ID: ")

            book = handler.get_book_by_id(book_id)
            print("\nSelected book: ")
            print(
                "---------------------------------------------------------------------------------")
            print(f"Title: {book.title}") if book.title else None
            print("Authors: ")
            for author in book.authors:
                print(f"    {author.last_name}, {author.remaining_name}")
            print(f"Language: {book.language}") if book.language else None
            print(f"Year: {book.year}") if book.year else None
            print(f"ISBN: {book.isbn}") if book.isbn else None
            print(f"Edition: {book.edition}") if book.edition else None
            print(
                f"Publication place: {book.publication_place}") if book.publication_place else None
            print(
                f"Publisher: {book.publisher.name}") if book.publisher else None
            print(
                "---------------------------------------------------------------------------------")

        return check_go_back()

    def get_paper_by_id(self) -> None:
        with DatabaseConnector() as con:
            handler = DBHandler(con)
            papers = handler.get_papers()
            print("\nFetching papers...")
            time.sleep(3)

            print("\nPapers: ")
            for paper in papers:
                print(f"{paper.document_id}: {paper.title}")
            paper_id = input("Paper ID: ")

            paper = handler.get_paper_by_id(paper_id)
            print("\nSelected paper: ")
            print(
                "---------------------------------------------------------------------------------")
            print(f"Title: {paper.title}") if paper.title else None
            print("Authors: ")
            for author in paper.authors:
                print(f"    {author.last_name}, {author.remaining_name}")
            print(f"Language: {paper.language}") if paper.language else None
            print(f"Year: {paper.year}") if paper.year else None
            print(f"DOI: {paper.doi}") if paper.doi else None
            print(f"Journal: {paper.journal}") if paper.journal else None
            print(f"Issue: {paper.issue}") if paper.issue else None
            print(f"Pages: {paper.pages}") if paper.pages else None
            print(f"Volume: {paper.volume}") if paper.volume else None
            print(
                f"Publisher: {paper.publisher.name}") if paper.publisher else None
            print(
                "---------------------------------------------------------------------------------")

        return check_go_back()


if __name__ == "__main__":
    app = Application()
    app.run()
