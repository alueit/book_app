from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

import re

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "UpdatedSeller"]

# Базовый класс "Продавец", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str# = Field(alias="e-mail")     # переменные в питоне не могут содержать дефис # TODO: check this

# Класс для валидации входящих данных
class IncomingSeller(BaseSeller):
    password: str

    # Корректность введённого email
    @field_validator("email")
    @staticmethod
    def validate_email(val: str):
        res = re.match(r"([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)", val)
        if not res:
            raise PydanticCustomError("Validation error", "Incorrect email!")
        return val

    # Сила пароля: 8-20 символов латиницы, цифр или спецсимволов !@#$%^&*-_
    # Обязательно использовать оба регистра и хотя бы одну цифру
    @field_validator("password")
    @staticmethod
    def validate_password(val: str):
        res = re.match(r"(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*\-_]{8,}", val)
        if not res:
            raise PydanticCustomError("Validation error", "Weak password")
        if len(val) > 20:
            raise PydanticCustomError("Validation error", "Password too long")
        return val

# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int

# Класс для метода put, чтобы не передавать ему id два раза. Различие с BaseSeller чисто концептуальное
class UpdatedSeller(BaseSeller):
    pass

# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
