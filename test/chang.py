import bcrypt

new_password = "123456"
hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
print(hashed.decode())
