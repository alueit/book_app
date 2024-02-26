import bcrypt

def process_password(password: str):
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hash, salt

def verify_password(password: str, salt:str):
    pass