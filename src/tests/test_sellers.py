import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers
from src.routers.v1.auth_utils import create_jwt_token

#Чтобы эффективно добавлять книги, приходится использовать некрасивые методы для добавления продавцов из-за ограничений

result = {
    "books": [
        {"author": "fdhgdh", "title": "jdhdj", "year": 1997},
        {"author": "fdhgdfgfrh", "title": "jrrgdhdj", "year": 2001},
    ]
}
seller = {
    "first_name": "Name",
    "last_name": "Last Name",
    "email": "example@gmail.com",
    "password": "fFdf!j3456"
}
seller_no_pass = {
    "first_name": "Name",
    "last_name": "Last Name",
    "email": "example@gmail.com",
}

seller_no_pass_2 = {
    "first_name": "Name 2",
    "last_name": "Last Name 2",
    "email": "example2@gmail.com",
}

# создать продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):

    response = await async_client.post("/api/v1/seller/", json=seller)
    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    # не проверяется id из-за состояния гонки тестов
    assert result_data["first_name"] == seller_no_pass["first_name"]
    assert result_data["last_name"] == seller_no_pass["last_name"]
    assert result_data["email"] == seller_no_pass["email"]



# получить список продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):

    seller1 = sellers.Seller(**seller_no_pass)
    seller2 = sellers.Seller(**seller_no_pass_2)

    db_session.add_all([seller1, seller2])
    await db_session.flush()
    
    response = await async_client.get("/api/v1/seller/")
    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2

    assert response.json() == {
        "sellers": [
            {**seller_no_pass, "id": seller1.id},
            {**seller_no_pass_2, "id": seller2.id},
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    seller1 = sellers.Seller(**seller_no_pass)
    seller2 = sellers.Seller(**seller_no_pass_2)

    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller1.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = await async_client.get(f"/api/v1/seller/{seller1.id}", headers={
                            "Authorization": "Bearer " + create_jwt_token({"id": seller1.id}).token
                        })
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {"id": seller1.id, **seller_no_pass, "books": []}

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller1.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller1.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller1.id}", headers={
                            "Authorization": "Bearer " + create_jwt_token({"id": seller1.id}).token
                        })
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {"id": seller1.id, **seller_no_pass, "books": [
            {"title": "Eugeny Onegin", "author": "Pushkin", "year": 2001, "id": book.id, "count_pages": 104, 'seller_id': seller1.id},
            {"title": "Mziri", "author": "Lermontov", "year": 1997, "id": book_2.id, "count_pages": 104, 'seller_id': seller1.id},
        ]}


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller1 = sellers.Seller(**seller_no_pass)

    db_session.add(seller1)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller1.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller1 = sellers.Seller(**seller_no_pass)

    db_session.add(seller1)
    await db_session.flush()


    response = await async_client.put(
        f"/api/v1/seller/{seller1.id}",
        json={**seller_no_pass_2, "id": seller1.id}
    )
    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller1.id)
    assert res.email == seller_no_pass_2["email"]
    assert res.first_name == seller_no_pass_2["first_name"]
    assert res.last_name == seller_no_pass_2["last_name"]
    assert res.id == seller1.id
