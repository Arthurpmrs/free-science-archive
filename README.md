# Free Science Archive

Trabalho destinado à disciplina de Banco de Dados, feito em Python e SQLite3.

## Descrição

O projeto em questão tenta simular um acervo digital de obras científicas, que inclue livros e artigos.

Nessa plataforma, podem ser registrados livros e artigos, os autores relacionados a esses documentos e as editoras que produzem responsáveis por tais obras.

Como o acervo é gerado pela comunidade, um Usuário é responsável por cadastrar um novo documento no sistema, sendo cada documento associado a apenas um Usuário.

## Modelo Conceitual

![modelo coceitual](https://github.com/Arthurpmrs/free-science-archive/blob/main/er/projeto-db-1-modelo.jpg)

## Modelo Lógico

**Document**(<u>document_id</u>, title, language, year, created_at, type, (**FK**)<u>publisher_id</u>, (**FK**)<u>user_id</u>)

**Book**((**FK**)<u>document_id</u>, isbn, publication_place, edition)

**Paper**((**FK**)<u>document_id</u>, doi, journal, issue, volume, pages)

**Author**(<u>author_id</u>, last_name, remaining_names, birth_date, email,social_url, nationality, created_at)

**Publisher**(<u>publisher_id</u>, name, address, url, created_at)

**Writes**((**FK**)<u>document_id</u>, (**FK**)<u>author_id</u>)

**User**(<u>user_id</u>, username, password, email, date_joined)

## Dependências funcionais

Para normalizar um modelo é necessário conhecer as dependências funcionais de cada tabela.

Se A e B são atributos de uma relação R, diz-se que B é dependente funcionalmente ou é dependência funcional de A ou A -> B, se para quaisquer tuplas $t_i$ e $t_j$ pertencentes a R, é válida a seguinte relação:

-   Se $t_i[A] = t_j[A]$
-   Então $t_i[B] = t_j[B]$

Ou seja, sempre que que buscarmos na tabela por uma linha com determinado valor de A, o valor de B será sempre o mesmo.

As dependências funcionais do modelo proposto são apresentadas a seguir.

### Document

document_id -> { title, language, year, created_at, type }

### Book

document_id -> { publication_place, isbn, edition }

### Paper

document_id -> { doi, volume, issue, journal, paages }

### Publisher

publisher_id -> { name, address, url, created_at }

### Author

author_id -> { last_name, remaining_names, birth_date, social_url, nationality, email, created_at }

### Writes (tabela de relacionamento)

Nada, pois a tabela só possui chave.

### User

user_id -> { date_joined, username, password, email }

## Normalização

### 1NF

A 1ª forma normal especifica que uma tabela deve ter ao menos uma _candidate key_ e que seus atributos devem ser atômicos, ou seja, não podem ser compostos, nem podem ser multivalorados.

Tendo em vista esta definição e o modelo lógico apresentado acima, não há violação da 1NF, exceto quanto ao campo _address_ da tabela Publisher. Entretanto, como a granularidade do endereço não é necessária ao negócio, não será dividido em mais tabelas.

## 2NF

A 2ª forma normal especifica que todos os atributos não-chave de uma tabela dependam de forma total da **Primary Key**, ou seja, que não haja dependência funcional parcial com a chave.

Observando o modelo lógico e a listagem de dependências funcionais listadas anteriormente, é possível perceber que não há violação da 2NF.

## 3NF

Já a 3ª forma normal especifica que não pode haver dependências funcionais transitivas entre a **Primary Key** e os outros atributos não-chave, ou seja, um atributo não-chave não pode depender funcionalmente de outro atributo não-chave.

Observando a descrição do modelo e das dependências funcionais, é possível dizer que não há dependências funcionais transitivas, e portanto, não há violação da 3NF.

É importante destacar que em algumas das tabelas, existem campos que dependem funcionamente de outros campos que não foram especificados como **Primary Key**, por exemplo, o campo _email_ da tabela Author. Como o _email_ é único, é possível dizer que:

email -> { last_name, remaining_names, birth_date, social_url, nationality, created_at}

Entretanto, como o email é único e é capaz de especificar a tupla inteira, ele pode ser considerado uma **Candidate Key** e, portanto, não é incluido na checagem da 3NF, que diz respeito a dependências funcionais transitivas em atributos **não-chave**.
