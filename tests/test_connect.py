import getpass
import os

import psycopg2.extras

import soong


def test_connect(mocker, monkeypatch):
    """Tests that the function calls psycopg2.connect with the correct arguments.

    The call arguments come from a mix of the keyword arguments, environment variables
    and default values.
    """
    mock = mocker.Mock()
    mocker.patch('psycopg2.connect', new=mock)
    kwargs = {'host': 'pg.host.net', 'dbname': 'mydb',
              'cursor_factory': psycopg2.extras.DictCursor}
    with monkeypatch.context() as mp:
        mp.setattr(os, 'environ', {'SOONG_PASSWORD': 'secr3t', 'SOONG_HOST': 'error'})
        soong.connect(**kwargs)

    del kwargs['cursor_factory']
    kwargs.update({'hostaddr': None, 'port': None, 'password': 'secr3t', 'user': getpass.getuser()})
    mock.assert_called_with(kwargs, connection_factory=None, cursor_factory=psycopg2.extras.DictCursor)
