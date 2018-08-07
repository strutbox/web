from django.db import connection


def last_query():
    try:
        return connection.queries[-1]["sql"]
    except IndexError:
        return None


def explain(sql, analyze=False):
    dbc = connection
    with dbc.get_new_connection(dbc.get_connection_params()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"EXPLAIN {'ANALYZE' if analyze else ''} {sql}")
            return "\n".join(c[0] for c in cursor.fetchall())
