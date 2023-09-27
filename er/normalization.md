# Detalhes do modelo

## Descrição

O projeto em questão é referente a um acervo digital de obras científicas, que inclue livros e artigos.

Nessa plataforma, podem ser registrados livros e artigos, os autores relacionados a esses documentos e as editoras que produzem responsáveis por tais obras.

Como o acervo é gerado pela comunidade, um Usuário é responsável por cadastrar um novo documento no sistema, sendo cada documento associado a apenas um Usuário.

## Modelo Lógico

**Document**(<u>document_id</u>, title, language, year, created_at, type, (**FK**)<u>publisher_id</u>, (**FK**)<u>user_id</u>)

**Book**((**FK**)<u>document_id</u>, isbn, publication_place, edition)

**Paper**((**FK**)<u>document_id</u>, doi, journal, issue, volume, pages)

**Author**(<u>author_id</u>, last_name, remaining_names, birth_date, email,social_url, nationality, created_at)

**Publisher**(<u>publisher_id</u>, name, address, url, created_at)

**Writes**((**FK**)<u>document_id</u>, (**FK**)<u>author_id</u>)

**User**(<u>user_id</u>, username, password, email, date_joined)

## Dependências funcionais

## Normalização
