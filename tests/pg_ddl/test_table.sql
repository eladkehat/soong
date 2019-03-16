/*
A table used in unit tests.
*/
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    txt TEXT,
    num INT
);

/*
When we use COPY to insert data to the table, the id is not updated.
Here we manully set the sequence to avoid primary key violations.
*/
ALTER SEQUENCE test_table_id_seq RESTART WITH 100;
