from settings.db import database_connection
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database="focusflow",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    cursor_factory=RealDictCursor,
    connect_timeout=3
)
cur = conn.cursor()
# create tables
cur.execute('''CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
)''')
cur.execute('''CREATE TABLE IF NOT EXISTS otp_table (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    hash_otp VARCHAR(255),
    created_at TIMESTAMP,
    expired_at TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    total_attempts INTEGER DEFAULT 5
)''')
conn.commit()
cur.close()
conn.close()
print('done')
