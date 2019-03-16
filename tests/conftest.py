import pathlib

import pytest

# Import the fixtures to make them available to the tests
from lathorp.fixtures import load_schema_definitions
from lathorp.fixtures import pg  # noqa: F401
from lathorp.fixtures import pg_connect  # noqa: F401


@pytest.fixture(scope='session')
def init_schema(pg):  # noqa: F811
    """Loads the schema definition."""
    path = pathlib.Path(__file__).parent / 'pg_ddl'
    assert path.is_dir()
    load_schema_definitions(pg, path)


@pytest.fixture(scope='function')
def conn(init_schema, pg_connect):  # noqa: F811
    data_path = pathlib.Path(__file__).parent / 'pg_data'
    return pg_connect(data_path)
