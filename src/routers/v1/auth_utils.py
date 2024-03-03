import bcrypt
import time
from fastapi import status, HTTPException
from jose import JWTError, jwt
from src.schemas.auth import Token


SECRET_KEY = 'Secret Key'

# 15 минут
TOKEN_EXPIRATION = 15 * 60

def process_password(password: str):
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hash, salt

def verify_password(password: str, stored_hash: str, stored_salt:str):
    decrypted_password = bcrypt.hashpw(password.encode('utf-8'), stored_salt)
    return stored_hash == decrypted_password

def create_jwt_token(data: dict):
    expiration_datetime = time.time() + TOKEN_EXPIRATION

    data_to_encode = {"expires": expiration_datetime, **data}
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm="HS256")

    return Token(token=encoded_jwt)

def return_id_from_jwt_token(encoded_token: str):
    if not encoded_token or not encoded_token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    encoded_token = encoded_token.split()[1]
    print(encoded_token)
    try:
        token = jwt.decode(encoded_token, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    else:
        if token['expires'] <= time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired token",
            )
        print(token["id"])
        return token["id"]