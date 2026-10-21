import psycopg2
from psycopg2.extras import RealDictCursor
from settings.db import database_connection
from model.user import UserLogin, UserRegister
from service.users import register_user, login_user


def _connect():
    connection = database_connection()
    if connection is None:
        raise ConnectionError("Database connection failed.")
    return connection



def get_user_by_email(user:UserLogin):
    email = user.email
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_username(username: str) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            return cursor.fetchone()
    finally:
        connection.close()



def create_user(first_name, last_name, email, username, hash_password) -> None:
    connection = _connect()
    user = register_user()
    if user is None:
        raise ValueError("User registration failed.")
    first_name = user.first_name
    last_name = user.last_name
    email = user.email
    username = user.username
    hash_password = user.hash_password
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, username, password) "
                "VALUES (%s, %s, %s, %s, %s)",
                (first_name, last_name, email, username, hash_password),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise  # UniqueViolation etc. handled by the service
    finally:
        connection.close()