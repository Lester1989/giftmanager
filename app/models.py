from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from app.pydantic_schematizer import create_pydantic,BaseModel
from enum import Enum as EnumClass
from sqlalchemy import Enum as EnumDB
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ulid import new as new_ulid

def new_uuid():
    return new_ulid().uuid

class Base(DeclarativeBase):
    __table_args__ = {'schema': 'public'}
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,default=new_uuid,type_=UUID(as_uuid=True))

class FriendAPI(BaseModel):
    pass
@create_pydantic(globals(),suffix='API',default_type=uuid.UUID)
class Friend(Base):
    __tablename__ = "user_account"
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
@create_pydantic(globals(),suffix='API',default_type=uuid.UUID)
class GiftIdea(Base):
    __tablename__ = "gift_idea"
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    name: Mapped[str]
    done: Mapped[bool]

class InteractionViaType(EnumClass):
    telephone = 'telephone'
    email = 'email'
    messenger = 'messenger'
    in_person = 'in_person'

class InteractionLogAPI(BaseModel):
    pass
@create_pydantic(globals(),suffix='API',default_type=uuid.UUID)
class InteractionLog(Base):
    __tablename__ = "interaction_log"
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    date: Mapped[datetime]
    via: Mapped[InteractionViaType] = mapped_column(type_=EnumDB(InteractionViaType))
    talking_points: Mapped[Optional[str]]
    ask_again: Mapped[bool]

class ImportantEventAPI(BaseModel):
    pass
@create_pydantic(globals(),suffix='API',default_type=uuid.UUID)
class ImportantEvent(Base):
    __tablename__ = "important_event"
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    date: Mapped[datetime]
    name: Mapped[str]
    description: Mapped[Optional[str]]

class TalkingPointAPI(BaseModel):
    pass
@create_pydantic(globals(),suffix='API',default_type=uuid.UUID)
class TalkingPoint(Base):
    __tablename__ = "talking_point"
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    point: Mapped[str]
    


