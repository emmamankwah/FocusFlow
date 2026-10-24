from settings.db import database_connection
c = database_connection()
cur = c.cursor()
cur.execute("SELECT has_schema_privilege('focusflow', 'public', 'CREATE')")
print(cur.fetchone())
cur.close()
c.close()
