from typing import Any
from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# from datetime import datetime

class Base(DeclarativeBase):
    pass

class Settings(Base):
    __tablename__ = "settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(Text, unique=True)
    value: Mapped[str] = mapped_column(Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value