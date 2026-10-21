from psycopg2.extras import RealDictCursor
from settings.db import database_connection
from model.user import UserRegister, UserLogin


Login = UserLogin
def get_user_by_email(Register:UserRegister):
    email = Register.email
    

    try:
        connection = database_connection()
        if connection is None:  
            return {"error": "Database connection failed."}
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            return result
            
    except Exception:
        print("Account not found")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


# def register_user(Register:UserRegister):
#     try:
#         connection = database_connection()
#         if connection is None:
#             return {"error": "Database connection failed."}
#         cursor = connection.cursor()
#         cursor.execute(
#             "INSERT INTO users (first_name, last_name, email, username, password) VALUES (%s, %s, %s, %s, %s)",
#             (Register.first_name, Register.last_name, Register.email, Register.username, Register.password)
#         )
#         connection.commit()
#     except Exception as e:
#         return {"error": f"An error occurred: {str(e)}"}
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'connection' in locals():
#             connection.close()
#     return {"message": "User registered successfully."}