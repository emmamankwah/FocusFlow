from model.user import UserLogin,UserRegister
from settings.db import database_connection

def register_user(user: UserRegister):
    password = user.password
    confirm_password = user.confirm_password
    if password != confirm_password:
        return {"error": "Passwords do not match."}
    try:
        connection = database_connection()
        if connection is None:
            return {"error": "Database connection failed."}

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s", (user.email, user.username))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            connection.close()
            return {"error": "Email or username already exists."}

        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, username, password) VALUES (%s, %s, %s, %s, %s)",
            (user.first_name, user.last_name, user.email, user.username, user.password)
        )
        connection.commit()

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}    

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
    return {"message": "User registered successfully."}
   



def login_user(user: UserLogin):
    try:
        connection = database_connection()
        if connection is None:
            return {"error": "Database connection failed."}

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE email = %s AND username = %s", (user.email, user.username))
        existing_user = cursor.fetchone()
        if not existing_user:
            cursor.close()
            connection.close()
            return {"error": "User not found."}

        if existing_user['password'] != user.password:
            cursor.close()
            connection.close()
            return {"error": "Incorrect password."}
        
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

        return {"message": "Login successful."}