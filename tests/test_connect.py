import getpass
import os

import psycopg2.extras

import soong


def test_connect_args(mocker, monkeypatch):
    """Tests that the function calls psycopg2.connect with the correct arguments.

    The call arguments come from a mix of the keyword arguments, environment variables
    and default values.
    """
    mock = mocker.Mock()
    mocker.patch('psycopg2.connect', new=mock)
    kwargs = {'host': 'pg.host.net', 'dbname': 'mydb',
              'cursor_factory': psycopg2.extras.DictCursor}
    with monkeypatch.context() as mp:
        mp.setattr(os, 'environ', {'PG_PASSWORD': 'secr3t', 'PG_HOST': 'error'})
        soong.connect(**kwargs)

    mock.assert_called_with(
        host='pg.host.net', hostaddr=None, port=5432, connect_timeout=30,
        dbname='mydb', user=getpass.getuser(), password='secr3t',
        connection_factory=None, cursor_factory=psycopg2.extras.DictCursor)


def test_connect_temp_pg(pg):
    """Tests the connect function using a temporary database."""
    dsn = pg.dsn()
    dsn['dbname'] = dsn.pop('database')
    conn = soong.connect(**dsn, cursor_factory=psycopg2.extras.NamedTupleCursor)
    with conn.cursor() as cursor:
        cursor.execute("SELECT 'Hello, world!' AS hello;")
        assert cursor.fetchone().hello == 'Hello, world!'


def test_new_connection(pg):
    """Tests that the connection function initializes the global connection object."""
    # Verify that the global connection object exists after module load, and is None
    assert soong._conn is None
    dsn = pg.dsn()
    dsn['dbname'] = dsn.pop('database')
    connection = soong.connection(**dsn)
    with connection.cursor() as cursor:
        cursor.execute("SELECT 'Hello, world!';")
        assert cursor.fetchone() == ('Hello, world!', )
    # Verify that the global connection object is now initialized
    assert soong._conn == connection


def test_connection_reconnects_closed(pg):
    """Tests that the connection function reconnects the global connection if closed."""
    dsn = pg.dsn()
    dsn['dbname'] = dsn.pop('database')
    connection = soong.connection(**dsn)
    assert not soong._conn.closed
    connection.close()
    assert soong._conn.closed
    connection = soong.connection(**dsn)
    assert not soong._conn.closed
    with connection.cursor() as cursor:
        cursor.execute("SELECT 'I am open';")
        assert cursor.fetchone() == ('I am open', )
