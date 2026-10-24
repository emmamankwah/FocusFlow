from settings.db import database_connection
c = database_connection()
if c is None:
    print('NONE')
else:
    print('OK')
    c.close()
