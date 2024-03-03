from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["Token", "User"]

# Базовый класс "Продавец", содержащий поля, которые есть во всех классах-наследниках.
class Token(BaseModel):
    token: str

# Класс для валидации входящих данных
class User(BaseModel):
    email: str
    password: str

