from settings.db import database_connection
c = database_connection()
cur = c.cursor()
try:
    cur.execute("CREATE TABLE users2 (id SERIAL PRIMARY KEY)")
    c.commit()
    print('ok')
except Exception as e:
    print(e)
cur.close()
c.close()
