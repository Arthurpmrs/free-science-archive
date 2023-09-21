import json
from datetime import datetime
from fsa.db.base import DatabaseConnector
from fsa.db.document_handler import DocumentHandler
from fsa.domain import Publisher, Document, Book, Paper, Author


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


if __name__ == "__main__":
    test_query()
