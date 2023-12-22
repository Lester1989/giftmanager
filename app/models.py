from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from ulid import new as new_ulid

class Base(DeclarativeBase):
    pass

class Friend(Base):
    __tablename__ = "user_account"
    id: Mapped[str] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[Optional[str]]
    address: Mapped[Optional[str]]
    phone_number: Mapped[Optional[str]]
    email: Mapped[str]
    birthday: Mapped[Optional[datetime]]
    notes: Mapped[Optional[str]]
    receives_christmas_gift: Mapped[bool]
    receives_birthday_gift: Mapped[bool]

class GiftIdea(Base):
    __tablename__ = "gift_idea"
    id: Mapped[str] = mapped_column(primary_key=True)
    friend_id: Mapped[str]
    name: Mapped[str]
    description: Mapped[Optional[str]]
    url: Mapped[Optional[str]]
    price: Mapped[Optional[float]]
    done: Mapped[bool]
    done_at: Mapped[Optional[datetime]]



