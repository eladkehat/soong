"""
Soong
~~~~~
A PostgreSQL utility library for AWS Lambda.

:copyright: © 2019 by Elad Kehat.
:license: MIT, see LICENSE for more details.
"""

import getpass
import os

import psycopg2


def connect(**kwargs) -> psycopg2.extensions.connection:
    """Connects to the PostgreSQL database and returns a new `psycopg2.connection` object.

    Attempts to load connection parameters from multiple sources, in the following order:
    1. keyword argumets
    2. environment variables
    3. sensible defaults defined in this function

    Environment variables must have the format SOONG_DBNAME - a SOONG_ prefix, followed by
    the uppercase name of the parameter.

    You can also pass values for the connection_factory and cursor_factory that go to
    `psycopg.connect`.

    Args:
        The valid kwargs are:
        * host: Name of the host
        * hostaddr: Numeric IP address, use instead of host to avoid DNS lookup
        * port: Port number
        * dbname: The database name
        * user: User name to connect as
        * password: The user's password

        In addition you may specify:
        * connection_factory: A subclass of psycopg2.extensions.connection
        * cursor_factory: A subclass of psycopg2.extensions.cursor

    Returns:
        An open connection to the database.
    """
    dsn = dict((param, kwargs.get(param, os.environ.get(f'SOONG_{param.upper()}', default)))
               for param, default in [
                    ('host', 'localhost'),
                    ('hostaddr', None),
                    ('port', None),  # defaults to 5432
                    ('dbname', 'default'),
                    ('user', getpass.getuser()),
                    ('password', None)])

    connf = kwargs.pop('connection_factory', None)
    cursf = kwargs.pop('cursor_factory', None)
    return psycopg2.connect(dsn, connection_factory=connf, cursor_factory=cursf)
