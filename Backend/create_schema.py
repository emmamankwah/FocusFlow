from settings.db import database_connection

conn = database_connection()
if not conn:
    raise SystemExit('no conn')
cur = conn.cursor()
# Create users table
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
''')
# Create otp table
cur.execute('''
CREATE TABLE IF NOT EXISTS otp_table (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    hash_otp VARCHAR(255),
    created_at TIMESTAMP,
    expired_at TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    total_attempts INTEGER DEFAULT 5
);
''')
conn.commit()
cur.close()
conn.close()
print('done')
