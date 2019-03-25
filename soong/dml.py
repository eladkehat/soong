"""SQL DML (data manipulation language) helper functions that minimize boilerplate code.

These functions support the most common scenarios of data manipulation - insert, update and delete,
while saving you from writing the boilerplate code around connections and cursors, or even writing
the SQL itself.
"""

from typing import Any, Dict, List, Tuple, Union

import psycopg2


def insert(conn: psycopg2.extensions.connection,
           table: str,
           values: Dict[str, Any],
           returning: Union[None, str, List[str]] = None) -> Union[None, Any, Tuple[Any]]:
    """Insert a new row into the table.

    Args:
        conn: An open database connection object.
        table: The table name.
        values: A dict that maps column names to their new values.
        returning: The name of a column whose new value you wish to return,
            or a list of of such column names.

    Returns:
        A row with the columns specified in `returning` and their values,
        or None if `returning` is None.
    """
    result = None
    keys = list(values.keys())
    interpolations = dict(
        table=table,
        cols=', '.join(keys),
        values=', '.join([f'%({key})s' for key in keys]))

    if returning:
        returning_clause = 'RETURNING {}'.format(
            returning if isinstance(returning, str)
            else ', '.join(str(col) for col in returning))
        interpolations['returning'] = returning_clause
    else:
        interpolations['returning'] = ''

    sql = 'INSERT INTO {table} ({cols}) VALUES ({values}) {returning};'.format(**interpolations)

    with conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, values)
            if returning:
                result = cursor.fetchone()
    if result and len(result) == 1:
        result = result[0]
    return result


def update(conn: psycopg2.extensions.connection, table: str, id: Any, values: Dict[str, Any]) -> None:
    """Update the row with the given id using the values.

    Use this function on tables with an indexed column (like a primary key) called `id`,
    when you would like to update some columns in a row whose id you know.

    Args:
        conn: An open database connection object.
        table: The table name.
        id: Searches for this value in the `id` column.
        values: A dict that maps column names for update to their new values.
    """
    keys = list(values.keys())
    sql = 'UPDATE {table} SET {values} WHERE id = %s;'.format(
        table=table,
        values=', '.join(f'{key} = %s' for key in keys))
    params = tuple([values[key] for key in keys] + [id])

    with conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)


def execute(
    conn: psycopg2.extensions.connection, sql: str, params: Tuple, returning: bool = False
) -> Union[Any, None]:
    """Execute an arbitrary SQL statement.

    Args:
        conn: An open database connection object.
        sql: The DML SQL statement to execute.
        params: Parameters that go with the SQL.
        returning: Whether the SQL statements contains a RETURNING clause.

    Returns:
        If returning is True, returns the row with the values that the SQL specified.
    """
    result = None
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            if returning:
                result = cursor.fetchone()
    return result
