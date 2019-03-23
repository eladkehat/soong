"""
Soong
~~~~~
A PostgreSQL utility library for AWS Lambda.

:copyright: © 2019 by Elad Kehat.
:license: MIT, see LICENSE for more details.
"""

import getpass
import os

import boto3
import psycopg2


def connect(**kwargs) -> psycopg2.extensions.connection:
    """Connects to the PostgreSQL database and returns a new `psycopg2.connection` object.

    Attempts to load connection parameters from multiple sources, in the following order:
    1. keyword argumets
    2. environment variables
    3. sensible defaults defined in this function

    Environment variables must have the format PG_DBNAME - a PG_ prefix, followed by
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
        * connect_timeout: Database connection timeout

        In addition you may specify:
        * connection_factory: A subclass of psycopg2.extensions.connection
        * cursor_factory: A subclass of psycopg2.extensions.cursor

    Returns:
        An open connection to the database.
    """
    dsn = dict((param, kwargs.get(param, os.environ.get(f'PG_{param.upper()}', default)))
               for param, default in [
                    ('host', 'localhost'),
                    ('hostaddr', None),
                    ('port', 5432),
                    ('dbname', 'default'),
                    ('user', getpass.getuser()),
                    ('password', None),
                    ('connect_timeout', 30)])

    if is_running_in_lambda():
        dsn['password'] = get_iam_token(dsn)

    connf = kwargs.pop('connection_factory', None)
    cursf = kwargs.pop('cursor_factory', None)
    return psycopg2.connect(**dsn, connection_factory=connf, cursor_factory=cursf)


def is_running_in_lambda() -> bool:
    """Checks whether the code is running inside the Lambda environment.

    Uses an environment variable. See the docs for more information:
    https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html
    Also checks that it isn't running inside a Docker container invoked by SAM CLI. See:
    https://github.com/awslabs/aws-sam-cli/blob/develop/docs/advanced_usage.md#identifying-local-execution-from-lambda-function-code  # noqa
    """
    return os.environ.get('AWS_EXECUTION_ENV', '').startswith('AWS_Lambda_') and \
        not os.environ.get('AWS_SAM_LOCAL', '')


def get_iam_token(dsn: dict) -> str:
    """Gets an IAM authentication token used to connect to the database in place of a password.

    This is a one-time token that is valid for 15 minutes.
    For more information:
    https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.html
    """
    rds = boto3.client('rds')
    return rds.generate_db_auth_token(dsn['host'], dsn['port'], dsn['user'])
