
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def database_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            cursor_factory=RealDictCursor,
            connect_timeout=5
        )
        return connection

    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None


if __name__ == "__main__":
    conn = database_connection()

    if conn:
        try:
            print("Database connection successful.")
        finally:
            conn.close()
            print("Database connection closed.")
    else:
        print("Database connection failed.")
