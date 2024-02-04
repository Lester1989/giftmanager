from sqlalchemy.orm import DeclarativeBase,Session
from datetime import datetime,date
from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from app.pydantic_schematizer import create_pydantic,BaseModel
from enum import Enum as EnumClass
from sqlalchemy import Enum as EnumDB
from sqlalchemy.dialects.postgresql import UUID,JSONB
import uuid
from ulid import new as new_ulid

def new_uuid():
    return new_ulid().uuid

class Base(DeclarativeBase):
    __table_args__ = {'schema': 'public'}
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,default=new_uuid,type_=UUID(as_uuid=True))

class UserRegistration(Base):
    __tablename__ = "user_registration"
    email: Mapped[str]

class UserPasswordReset(Base):
    __tablename__ = "user_password_reset"
    email: Mapped[str]

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(User).filter(User.id == user_id,User.email==self.email).first())

class User(Base):
    __tablename__ = "user"
    email: Mapped[str]
    password_hash: Mapped[str] # hashed
    settings: Mapped[dict] = mapped_column(type_=JSONB,server_default='{}')
    is_activated: Mapped[bool] = mapped_column(default=False)


class UserFriend(Base):
    __tablename__ = "user_friend"
    login_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True),primary_key=True)
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True),primary_key=True)

class Friend(Base):
    __tablename__ = "user_account"
    first_name: Mapped[str]
    last_name: Mapped[Optional[str]]
    address: Mapped[Optional[str]]
    phone_number: Mapped[Optional[str]]
    email: Mapped[str]
    birthday: Mapped[Optional[date]]
    notes: Mapped[Optional[str]]
    receives_christmas_gift: Mapped[bool]
    receives_birthday_gift: Mapped[bool]

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(UserFriend).filter(UserFriend.login_id == user_id,UserFriend.friend_id == self.id).first())

class GiftIdea(Base):
    __tablename__ = "gift_idea"
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    name: Mapped[str]
    done: Mapped[bool]

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(UserFriend).filter(UserFriend.login_id == user_id,UserFriend.friend_id == self.friend_id).first())

class InteractionViaType(EnumClass):
    telephone = 'telephone'
    email = 'email'
    messenger = 'messenger'
    in_person = 'in_person'


class InteractionLog(Base):
    __tablename__ = "interaction_log"
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    date: Mapped[datetime]
    via: Mapped[InteractionViaType] = mapped_column(type_=EnumDB(InteractionViaType))
    talking_points: Mapped[Optional[str]]
    ask_again: Mapped[bool]

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(UserFriend).filter(UserFriend.login_id == user_id,UserFriend.friend_id == self.friend_id).first())


class ImportantEvent(Base):
    __tablename__ = "important_event"
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    date: Mapped[date]
    name: Mapped[str]
    description: Mapped[Optional[str]]

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(UserFriend).filter(UserFriend.login_id == user_id,UserFriend.friend_id == self.friend_id).first())

    @property
    def is_upcoming(self):
        return self.date > date.today()

    @property
    def days_until(self):
        return (self.date - date.today()).days


class TalkingPoint(Base):
    __tablename__ = "talking_point"
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    point: Mapped[str]

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(UserFriend).filter(UserFriend.login_id == user_id,UserFriend.friend_id == self.friend_id).first())


class DemoData(Base):
    __tablename__ = "demo_data"
    user_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(UserFriend).filter(UserFriend.login_id == user_id,UserFriend.friend_id == self.friend_id).first())



