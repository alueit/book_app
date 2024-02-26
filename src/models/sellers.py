from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import LargeBinary

from .base import BaseModel


class Seller(BaseModel):
    __tablename__ = "sellers_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)      # переменные в питоне не могут содержать дефис

class SellerPassword(BaseModel):
    __tablename__ = "sellers_pass_table"
    id: Mapped[int] = mapped_column(ForeignKey("sellers_table.id", ondelete="CASCADE"), primary_key=True)
    hash: Mapped[bytes] = mapped_column(LargeBinary(100), nullable=False)
    salt: Mapped[bytes] = mapped_column(LargeBinary(100), nullable=False)