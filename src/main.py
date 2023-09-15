from datetime import datetime
from fsa.database import DatabaseConnector
from fsa.domain import Publisher, Document, Book, Paper, Author


def main():
    new_publisher = Publisher(
        publisher_id=None,
        trade_name="Editora Abril",
        company_name="Abril",
        address="Av. das Nações Unidas, 7221 - Pinheiros, São Paulo - SP, 05425-902",
        url="https://www.abril.com.br/",
        document_ids=[],
    )

    print(new_publisher.get_parsed_dict())

    new_author = Author(
        author_id=None,
        remaining_name="Machado de",
        last_name="Assis",
        birth_date=datetime.strptime("1839-06-21", '%Y-%m-%d'),
        email="machadao_das_massas@yahoo.com",
        social_url="@machadao",
        nationality="brazilian",
        document_ids=[],
    )
    print(new_author.get_parsed_dict())
    with DatabaseConnector() as con:
        cur = con.cursor()
        cur.execute("""
                    INSERT INTO Publisher
                    VALUES(:publisher_id, :trade_name, :company_name, :address, :url, :created_at)
                    """, new_publisher.get_parsed_dict())

        cur.execute("""
                    INSERT INTO Author
                    VALUES(:author_id, :remaining_name, :last_name, :birth_date,
                    :email, :social_url, :nationality, :created_at)
                    """, new_author.get_parsed_dict())
        con.commit()
        res = cur.execute("SELECT * FROM Publisher")

        for row in res.fetchall():
            print(row[0], row[1], row[2], row[3], row[4], row[5])


if __name__ == "__main__":
    main()
