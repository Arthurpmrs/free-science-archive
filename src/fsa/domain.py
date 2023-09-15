from typing import Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass(kw_only=True)
class Publisher:
    publisher_id: int | None = None
    company_name: str
    trade_name: str
    address: str
    url: str
    document_ids: list[int]
    created_at: datetime = datetime.now()

    def get_parsed_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(kw_only=True)
class Author:
    author_id: int | None = None
    remaining_name: str
    last_name: str
    birth_date: datetime
    email: str
    social_url: str
    nationality: str
    document_ids: list[int]
    created_at: datetime = datetime.now()

    def get_parsed_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(kw_only=True)
class Document:
    document_id: int | None = None
    title: str
    language: str
    year: int
    n_pages: int
    tags: list[str]
    publisher: Publisher
    authors: list[Author]
    created_at: datetime = datetime.now()


@dataclass(kw_only=True)
class Book(Document):
    publication_place: str
    isbn: str
    edition: str


@dataclass(kw_only=True)
class Paper(Document):
    journal: str
    volume: str
    issue: str
    pages: str
    doi: str
