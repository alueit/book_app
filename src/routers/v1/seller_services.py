import bcrypt

def process_password(password: str):
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hash, salt

def verify_password(password: str, stored_hash: str, stored_salt:str):
    decrypted_password = bcrypt.hashpw(password.encode('utf-8'), stored_salt)
    return stored_hash == decrypted_password