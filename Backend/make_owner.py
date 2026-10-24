from settings.db import database_connection
c = database_connection()
cur = c.cursor()
cur.execute("ALTER DATABASE postgres OWNER TO focusflow")
c.commit()
print('ok')
cur.close()
c.close()
