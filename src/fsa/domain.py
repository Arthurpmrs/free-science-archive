from typing import Any, Self
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass(kw_only=True)
class Publisher:
    publisher_id: int | None = None
    name: str
    address: str
    url: str
    document_ids: list[int]
    created_at: datetime = datetime.now()

    def get_parsed_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_raw_data(self, data: dict) -> Self:
        return Publisher(
            name=data.get("name"),
            address=data.get("address"),
            url=data.get("url"),
            document_ids=[],
        )

    @classmethod
    def from_db_row(self, row: dict) -> Self:
        return Publisher(
            publisher_id=row.get("publisher_id"),
            name=row.get("name"),
            address=row.get("address"),
            url=row.get("url"),
            document_ids=[],
            created_at=row.get("pub_created_at")
        )


@dataclass(kw_only=True)
class Author:
    author_id: int | None = None
    remaining_name: str
    last_name: str
    birth_date: datetime | None
    email: str | None
    social_url: str | None
    nationality: str | None
    document_ids: list[int]
    created_at: datetime = datetime.now()

    def __str__(self):
        return f"{self.last_name}, {self.remaining_name}"

    def get_parsed_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_raw_data(self, data: dict) -> Self:
        return Author(
            author_id=None,
            remaining_name=data.get("given"),
            last_name=data.get("family"),
            birth_date=None,
            email=None,
            social_url=None,
            nationality=None,
            document_ids=[]
        )


@dataclass(kw_only=True)
class Document:
    document_id: int | None = None
    title: str
    language: str | None
    year: int | None
    tags: list[str]
    publisher: Publisher | None
    authors: list[Author]
    created_at: datetime = datetime.now()

    def get_parsed_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(kw_only=True)
class Book(Document):
    publication_place: str | None
    isbn: str | None
    edition: str | None


@dataclass(kw_only=True)
class Paper(Document):
    journal: str | None
    volume: str | None
    issue: str | None
    pages: str | None
    doi: str | None

    def __str__(self):
        return (
            f"{self.title}\n"
            f"{self.journal}\n"
            f"{'; '.join([str(author) for author in self.authors])}\n"
            f"{self.year}\n"
            f"{self.doi}\n"
        )

    @classmethod
    def from_raw_data(self, data: dict) -> Self:
        """Create a new Paper object from raw data"""

        publisher: Publisher = Publisher.from_raw_data(data.get("publisher"))

        authors: list[Author] = []
        for author in data.get("author"):
            authors.append(Author.from_raw_data(author))

        return Paper(
            title=data.get("title"),
            language=data.get("language"),
            year=data.get("issued").get("date-parts")[0][0],
            tags=[],
            publisher=publisher,
            authors=authors,
            journal=data.get("container-title"),
            volume=data.get("volume"),
            issue=data.get("issue"),
            pages=data.get("page"),
            doi=data.get("DOI")
        )

    @classmethod
    def from_db_row(self, row: dict) -> Self:
        """Create a new Paper object from a database row"""

        publisher: Publisher = Publisher.from_db_row(row)

        return Paper(
            document_id=row.get("document_id"),
            title=row.get("title"),
            language=row.get("language"),
            year=row.get("year"),
            tags=[],
            publisher=publisher,
            authors=[],
            journal=row.get("journal"),
            volume=row.get("volume"),
            issue=row.get("issue"),
            pages=row.get("pages"),
            doi=row.get("doi"),
            created_at=row.get("doc_created_at")
        )
