import logging
from datetime import datetime, timezone
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
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,),)
            return cursor.fetchone()
    finally:
       connection.close()


def get_user_by_username(username: str) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,),)
            return cursor.fetchone()
    finally:
        connection.close()


def create_user(first_name, last_name, email, username, hash_password) -> None:
    connection = _connect()
    user = register_user()
    if user is None:
        raise ValueError("User registration failed.")
   
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, username, password) "
                "VALUES (%s, %s, %s, %s, %s)",
                (user.first_name, user.last_name, user.email, user.username, user.hash_password),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise  
    finally:
       connection.close()


def get_user_otp(email: str) -> dict:
    connection = None
    try:
        connection = _connect()
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT hash_otp,created_at, expired_at, attempts,total_attempts FROM otp_table WHERE email = %s", (email,),)
            return cursor.fetchone()
            
    except Exception:
        logging.exception("otp_request failed")
        raise
    finally:
        if connection:
            connection.close()


def verify_user_otp(email: str, otp: str) -> dict:
    connection = None
    try:
        connection = _connect()
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT hash_otp,created_at, expired_at, attempts,total_attempts FROM otp_table WHERE email = %s", 
                            (email,),)
            row = cursor.fetchone()
            if not row:
                return {"error": "Invalid OTP."}
           
        created = row['created_at']
        expiry = row['expired_at']

        if created >= expiry:
            return {"error": "OTP has expired."}

        if datetime.now(timezone.utc) >= expiry.replace(
                tzinfo=timezone.utc
            ) if expiry.tzinfo is None else datetime.now(timezone.utc) >= expiry:
                return {"error": "OTP has expired."}

        total_attempts = row['total_attempts']
        attempts = row['attempts']

        if attempts >= total_attempts:
            return {"error": "Too many failed attempts."}
        

        hashed_otp = row['hash_otp']
        if not hashed_otp:
            return {"error": "No OTP found for this email."}

        return {
            "hash_otp": row["hash_otp"],
            "created_at": row["created_at"],
            "expired_at": expiry,
            "attempts": attempts,
            "total_attempts": total_attempts,
        }

      
        return {"success": "OTP verified successfully."}
        
    except Exception:
        logging.exception("verify_user_otp failed")
        raise

    finally:
        if connection:
            connection.close()

def increment_attempts(email: str) -> None:
    """Increments failed verification attempts counter by 1."""
    connection = None
    try:
        connection = _connect()
        with connection:  # Automatically commits the transaction
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE otp_table 
                    SET attempts = attempts + 1 
                    WHERE email = %s
                    """,
                    (email,),
                )
    except Exception as e:
        logging.error("Failed to increment OTP attempts")
    finally:
        if connection:
            connection.close()


def clear_otp(email: str) -> None:
    """Clears OTP fields and resets attempts upon successful verification."""
    connection = None
    try:
        connection = _connect()
        with connection:  # Automatically commits the transaction
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE otp_table 
                    SET hash_otp = NULL, 
                        expired_at = NULL, 
                        attempts = 0 
                    WHERE email = %s
                    """,
                    (email,),
                )
    except Exception as e:
        logging.error("Failed to clear OTP ")
        raise
    finally:
        if connection:
            connection.close()