from typing import Annotated

from fastapi import APIRouter, Depends, Response, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
import time
from src.configurations.database import get_async_session
from src.models.sellers import Seller, SellerPassword
from src.schemas.auth import Token, User
from src.routers.v1.seller_services import verify_password

token_router = APIRouter(tags=["token"], prefix="/token")


SECRET_KEY = 'Secret Key'

# 15 минут
TOKEN_EXPIRATION = 60 * 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


def create_jwt_token(data: dict):
    expiration_datetime = time.time() + TOKEN_EXPIRATION

    data_to_encode = {"expires": expiration_datetime, **data}
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm="HS256")

    return Token(token=encoded_jwt)

def return_id_from_jwt_token(encoded_token: str):
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
        return token["id"]

# Route to obtain a JWT token (login)
@token_router.post("/", response_model=Token, status_code=status.HTTP_200_OK)
async def create_token(user: User, session: DBSession):
    print(user.email, user.password)
    query = select(Seller).where(Seller.email == user.email)
    res = await session.execute(query)
    seller = res.scalars().one()
    if seller:
        seller_pass = await session.get(SellerPassword, seller.id)
        if verify_password(user.password, seller_pass.hash, seller_pass.salt):
            return create_jwt_token({"id": seller.id})
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

