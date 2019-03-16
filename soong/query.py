"""SQL query helper functions that minimize boilerplate code.

For queries against a single table, there are functions that save you from writing boilerplate SQL.

For more elaborate queries (with joins, subselects, etc.), use the `query` funciton to avoid
writing the boilerplate code around connections and cursors.
"""

from typing import Any, Dict, Iterable, List, Tuple, Union

import psycopg2


def _build_query(table, qualifications, select_list, limit) -> Tuple[str, Tuple[Any, ...]]:
    """Construct a SQL select query using the given parameters.

    This is a module-internal function used by `select` and `select_one`.

    Args:
        table: The table name.
        qualifications: A dict of parameters for the WHERE clause.
        select_list: The columns to fetch. If empty, returns all columns (*).
        limit: The maximum number of rows to fetch.

    Returns:
        A query and parameters for use by `cursor.execute()`.
    """
    params = []
    query = ['SELECT', ', '.join(select_list or ['*']), 'FROM', table]
    if qualifications:
        quals = []
        for col, value in qualifications.items():
            if type(value) is list or type(value) is tuple:
                op = value[0]
                params.append(value[1])
            else:
                op = '='
                params.append(value)
            quals.append(f'{col} {op} %s')
        query += ['WHERE', ' AND '.join(quals)]
    if limit:
        query += ['LIMIT', str(limit)]
    return ' '.join(query), tuple(params)


def select(conn: psycopg2.extensions.connection,
           table: str,
           qualifications: Dict = {},
           select_list: List = [],
           limit: Union[int, None] = None,
           arraysize: int = 100) -> Iterable[Any]:
    """A generator method that runs a select query on the table and yields the results.

    Args:
        conn: An open database connection object.
        table: The table name.
        qualifications: A dict of parameters for the WHERE clause.
            The dict's keys are the column names.
            Each value is either a single native type (str, int, ..), in which case the condition is
            key = value, or a tuple in the format (operator, value), like ('<', 3) or ('>=', 15), in
            which case the operator is used between the key and value instead of a '=' sign.
        select_list: The columns to fetch. If empty, returns all columns (*).
        limit: The maximum number of rows to fetch.
        arraysize: The cursor arraysize (only used when limit is None).

    Yields:
        Rows from the table that matched the qualifications.
    """
    query, params = _build_query(table, qualifications, select_list, limit)
    with conn:
        with conn.cursor() as cursor:
            cursor.arraysize = arraysize
            cursor.execute(query, params)
            rows: List[Any]
            for rows in iter(cursor.fetchmany, []):
                yield from rows


def select_one(
    conn: psycopg2.extensions.connection, table: str, qualifications: Dict = {}, select_list: List = []
) -> Union[Any, None]:
    """Runs a select query on the table and returns a single row.

    Args:
        conn: An open database connection object.
        table: The table name.
        qualifications: A dict of parameters for the WHERE clause.
            The dict's keys are the column names.
            Each value is either a single native type (str, int, ..), in which case the condition is
            key = value, or a tuple in the format (operator, value), like ('<', 3) or ('>=', 15), in
            which case the operator is used between the key and value instead of a '=' sign.
        select_list: The columns to fetch. If empty, returns all columns (*).

    Returns:
        The first row that matched the query, or None if no row matched.
    """
    query, params = _build_query(table, qualifications, select_list, limit=1)
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()


def get(conn: psycopg2.extensions.connection, table: str, id: Any, select_list: List = []) -> Union[Any, None]:
    """Fetch the row with the given id from the table.

    Use this function on tables with an indexed column (like a primary key) called `id`,
    when you would like to retrieve a single row whose id you know.

    Args:
        conn: An open database connection object.
        table: The table name.
        id: Searches for this value in the `id` column.
        select_list: The columns to fetch. If empty, returns all columns (*).

    Returns:
        The row, or None if no row with that id was found.
    """
    return select_one(conn, table, {'id': id}, select_list)


def execute(
    conn: psycopg2.extensions.connection, sql: str, params: Tuple = (), arraysize: int = 100
) -> Iterable[Any]:
    """A generator method that executes the given SQL select query and yields the results.

    Use this function to execute an arbitrary select query.

    Args:
        conn: An open database connection object.
        sql: The SQL select query to execute.
        params: Parameters for the query.
        arraysize: The cursor arraysize (only used when limit is None).

    Yields:
        Rows from the table that matched the query.
    """
    with conn.cursor() as cursor:
        cursor.arraysize = arraysize
        cursor.execute(sql, params)
        rows: List[Any]
        for rows in iter(cursor.fetchmany, []):
            yield from rows
