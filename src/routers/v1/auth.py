from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations.database import get_async_session
from src.models.sellers import Seller, SellerPassword
from src.routers.v1.auth_utils import verify_password, create_jwt_token
from src.schemas.auth import Token, User

token_router = APIRouter(tags=["token"], prefix="/token")



DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# Route to obtain a JWT token (login)
@token_router.post("/", response_model=Token, status_code=status.HTTP_200_OK)
async def create_token(user: User, session: DBSession):
    query = select(Seller).where(Seller.email == user.email)
    res = await session.execute(query)
    seller = res.scalars().one()
    if seller:
        seller_pass = await session.get(SellerPassword, seller.id)
        if verify_password(user.password, seller_pass.hash, seller_pass.salt):
            return create_jwt_token({"id": seller.id})
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

