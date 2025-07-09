import bcrypt

def hash(password=""):

    return my_hash(password)

    
def my_hash(password=""):

    salt = b'$2b$12$0i/EJp.8Ti8UOBjDK4zoRe'
    password_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    return hashed_password.decode('utf-8')

