from repository.authentication.user_repo import create_user
try:
    create_user('Test','User','test@example.com','testuser','hashedpass')
    print('ok')
except Exception as e:
    print('err')
    print(e)
