from settings.db import database_connection
import os
# try connecting to different db
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST') or 'localhost',
        database='focusflow',
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor,
        connect_timeout=3
    )
    print('ok')
    conn.close()
except Exception as e:
    print(e)
