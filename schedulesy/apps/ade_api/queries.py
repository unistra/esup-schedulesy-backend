from django.db import connection


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_results(query):
    result = []
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = dictfetchall(cursor)
    return result


def get_hierarchical_classrooms_by_depth(depth: int = 0):
    condition = f'WHERE depth = {depth}' if depth else ''
    query = f"""
        WITH RECURSIVE parent_resource AS (
            SELECT r.id, r.ext_id, r.fields->>'code' AS code, r.fields->>'name' as name, 1 AS depth, ARRAY[r.id] AS path
            FROM ade_api_resource r where ext_id='classroom'
              UNION ALL
            SELECT r.id, r.ext_id, r.fields->>'code', r.fields->>'name', pr.depth + 1, pr.path || r.id
            FROM ade_api_resource r, parent_resource pr
            WHERE r.parent_id = pr.id
        )
        SELECT * from parent_resource
        {condition}
        ORDER BY PATH;
    """
    return get_results(query)


def get_trainees_size():
    # Fastest query without an index on "fields"
    query = """
        WITH RECURSIVE parent_resource(id) AS (
            SELECT r.id, r.ext_id, 0 as size, r.parent_id
            FROM ade_api_resource r where ext_id = 'trainee'
              UNION ALL
            SELECT r.id, r.ext_id::varchar, (r.fields->>'size')::integer, r.parent_id
            FROM ade_api_resource r, parent_resource pr
            WHERE r.parent_id = pr.id
        )
        SELECT * from parent_resource;
    """
    return get_results(query)