from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from app.pydantic_schematizer import create_pydantic,BaseModel


class Base(DeclarativeBase):
    pass

class FriendAPI(BaseModel):
    pass
@create_pydantic(globals())
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

class GiftIdeaAPI(BaseModel):
    pass
@create_pydantic(globals())
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

class ContactAPI(BaseModel):
    pass
@create_pydantic(globals())
class Contact(Base):
    __tablename__ = "contact"
    id: Mapped[str] = mapped_column(primary_key=True)
    friend_id: Mapped[str]
    date: Mapped[datetime]
    via_telephone: Mapped[bool]
    via_email: Mapped[bool]
    via_messenger: Mapped[bool]
    in_person: Mapped[bool]

class ImportantEventAPI(BaseModel):
    pass
@create_pydantic(globals())
class ImportantEvent(Base):
    __tablename__ = "important_event"
    id: Mapped[str] = mapped_column(primary_key=True)
    friend_id: Mapped[str]
    date: Mapped[datetime]
    name: Mapped[str]
    description: Mapped[Optional[str]]



