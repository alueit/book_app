from typing import Annotated

from fastapi import APIRouter, Depends, Response, status, Header
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.books import Book
from src.models.sellers import Seller, SellerPassword
from src.schemas import IncomingSeller, ReturnedAllSellers, UpdatedSeller, ReturnedSeller, ReturnedSellerWithBooks

from src.routers.v1.auth_utils import process_password, return_id_from_jwt_token

sellers_router = APIRouter(tags=["seller"], prefix="/seller")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# POST seller
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller, session: DBSession
): 
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
    )
    session.add(new_seller)
    await session.flush()

    new_hash, new_salt = process_password(seller.password)
    new_seller_password = SellerPassword(
        id=new_seller.id,
        hash=new_hash,
        salt=new_salt,
    )

    session.add(new_seller_password)
    await session.flush()
    new_seller.books=[]
    return new_seller

@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()

    return {"sellers": sellers}

@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(seller_id: int, session: DBSession, authorization: str = Header(None)):
    token_id = return_id_from_jwt_token(authorization)
    if token_id and token_id==seller_id:
        if seller := await session.get(Seller, seller_id):
            query = select(Book).where(Book.seller_id == seller_id)
            res = await session.execute(query)
            seller.books = res.scalars().all()
            return seller
    return Response(status_code=status.HTTP_401_UNAUTHORIZED)

@sellers_router.delete("/{seller_id}", response_model=ReturnedSeller)
async def delete_seller(seller_id: int, session: DBSession):
    if deleted_seller:= await session.get(Seller, seller_id):
        await session.delete(deleted_seller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@sellers_router.put("/{seller_id}", response_model=UpdatedSeller)
async def update_sellers(seller_id: int, updated_seller: UpdatedSeller, session: DBSession):
    if cur_seller:= await session.get(Seller, seller_id):
        cur_seller.first_name = updated_seller.first_name
        cur_seller.last_name = updated_seller.last_name
        cur_seller.email = updated_seller.email

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)