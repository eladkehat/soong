import soong.dml
import soong.query


def test_insert(conn):
    assert soong.query.select_one(conn, 'test_table', qualifications={'num': 14}) is None
    returned = soong.dml.insert(conn, 'test_table', dict(txt='Fourteen', num=14))
    assert returned is None
    new_row = soong.query.select_one(conn, 'test_table', qualifications={'num': 14})
    assert new_row[1:] == ('Fourteen', 14)


def test_insert_returning_single(conn):
    assert soong.query.select_one(conn, 'test_table', qualifications={'num': 15}) is None
    returned = soong.dml.insert(conn, 'test_table', dict(txt='Fifteen', num=15), returning='num')
    assert returned == (15, )


def test_insert_returning_many(conn):
    assert soong.query.select_one(conn, 'test_table', qualifications={'num': 16}) is None
    returned = soong.dml.insert(conn, 'test_table', dict(txt='Sixteen', num=16), returning=('txt', 'num'))
    assert returned == ('Sixteen', 16)


def test_update_one_value(conn):
    assert soong.query.get(conn, 'test_table', 1) == (1, 'Eleven', 11)
    soong.dml.update(conn, 'test_table', 1, dict(txt='updated'))
    assert soong.query.get(conn, 'test_table', 1) == (1, 'updated', 11)


def test_update_many_values(conn):
    assert soong.query.get(conn, 'test_table', 2) == (2, 'Twelve', 12)
    soong.dml.update(conn, 'test_table', 2, dict(txt='updated', num=99))
    assert soong.query.get(conn, 'test_table', 2) == (2, 'updated', 99)


def test_execute(conn):
    assert soong.query.get(conn, 'test_table', 2) is not None
    sql = 'DELETE FROM test_table WHERE id = %s;'
    returned = soong.dml.execute(conn, sql, (2, ))
    assert returned is None
    assert soong.query.get(conn, 'test_table', 2) is None


def test_execute_returning(conn):
    assert soong.query.get(conn, 'test_table', 3) == (3, 'Thirteen', 13)
    sql = 'DELETE FROM test_table WHERE id = %s RETURNING txt, num;'
    returned = soong.dml.execute(conn, sql, (3, ), returning=True)
    assert returned == ('Thirteen', 13)
    assert soong.query.get(conn, 'test_table', 3) is None
