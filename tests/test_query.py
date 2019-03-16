import inspect

import soong.query


def test_build_query():
    query, params = soong.query._build_query(
        'my_table',
        {'hello': 'world', 'number': ('<', 42)},
        ['col1', 'col2', 'col3'],
        12)
    assert query == 'SELECT col1, col2, col3 FROM my_table WHERE hello = %s AND number < %s LIMIT 12'
    assert params == ('world', 42)


def test_select(conn):
    gen = soong.query.select(conn, 'test_table')
    assert inspect.isgenerator(gen)
    assert list(gen) == [(1, 'Eleven', 11), (2, 'Twelve', 12), (3, 'Thirteen', 13)]
    assert list(soong.query.select(conn, 'test_table', select_list=['num'], limit=2)) == [(11, ), (12, )]
    assert list(soong.query.select(conn, 'test_table', qualifications={'txt': 'Twelve'}, select_list=['num'])) == \
        [(12, )]
    assert list(soong.query.select(conn, 'test_table', qualifications={'num': ('>', 11)})) == \
        [(2, 'Twelve', 12), (3, 'Thirteen', 13)]


def test_select_one(conn):
    assert soong.query.select_one(conn, 'test_table', qualifications={'txt': 'Twelve'}, select_list=['num']) == \
        (12, )
    assert soong.query.select_one(conn, 'test_table', qualifications={'txt': 'Nope'}) is None
    assert soong.query.select_one(conn, 'test_table') == (1, 'Eleven', 11)


def test_get(conn):
    assert soong.query.get(conn, 'test_table', 1) == (1, 'Eleven', 11)
    assert soong.query.get(conn, 'test_table', 17) is None
    # With specific columns:
    assert soong.query.get(conn, 'test_table', 1, ['txt', 'num']) == ('Eleven', 11)


def test_execute(conn):
    sql = 'SELECT num FROM test_table WHERE txt = %s;'
    gen = soong.query.execute(conn, sql, ('Twelve', ))
    assert inspect.isgenerator(gen)
    assert list(gen) == [(12,)]
