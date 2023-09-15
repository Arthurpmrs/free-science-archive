# Normalização

## Modelo Lógico

**Document**(<u>document_id</u>, title, language, year, n_pages, tags, created_at, \[FK\]<u>publisher_id</u>)

**Book**(\[FK\]<u>document_id</u>, isbn, publication_place, edition)

**Paper**(\[FK\]<u>document_id</u>, doi, journal, issue, volume, pages)

**Author**(<u>author_id</u>, last_name, remaining_names, birth_date, email,social_url, nationality, created_at)

**Publisher**(<u>publisher_id</u>, trade_name, company_name, address, url, created_at)

**Writes**(\[FK\]<u>document_id</u>, \[FK\]<u>author_id</u>)

**File**(<u>file_id</u>, name, extension, size, cover_url, storage_url, \[FK\]<u>document_id</u>, \[FK\]<u>user_id</u>)

**User**(<u>user_id</u>, username, password, email, birth_date, nationality, created_at)

**Follows**(\[FK\]<u>user_id</u>, \[FK\]<u>another_user_id</u>)

**Downloads**(\[FK\]<u>user_id</u>, \[FK\]<u>file_id</u>)
