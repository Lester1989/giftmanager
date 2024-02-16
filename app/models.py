from sqlalchemy.orm import DeclarativeBase,Session
from datetime import date
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

    def to_dict(self):
        return {
            "first_name":self.first_name,
            "last_name":self.last_name,
            "address":self.address,
            "phone_number":self.phone_number,
            "email":self.email,
            "birthday":self.birthday,
            "notes":self.notes,
            "receives_christmas_gift":self.receives_christmas_gift,
            "receives_birthday_gift":self.receives_birthday_gift,
        }

    @property
    def next_birthday(self):
        if not self.birthday:
            return None
        today = date.today()
        next_birthday_date = self.birthday.replace(year=today.year)
        if next_birthday_date < today:
            next_birthday_date = next_birthday_date.replace(year=today.year+1)
        return next_birthday_date

    def special_events(self)->list['ImportantEvent']:
        events = []
        if self.birthday:
            events.append(
                ImportantEvent(
                    friend_id=self.id,
                    date=self.next_birthday,
                    name=f"{self.first_name}'s Birthday",
                    description="",
                    requires_gift=self.receives_birthday_gift
                )
            )
        if self.receives_christmas_gift:
            events.append(
                ImportantEvent(
                    friend_id=self.id,
                    date=date(date.today().year,12,24),
                    name=f"{self.first_name}'s Christmas",
                    description="",
                    requires_gift=True
                )
            )
        return events

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(UserFriend).filter(UserFriend.login_id == user_id,UserFriend.friend_id == self.id).first())

class GiftIdea(Base):
    __tablename__ = "gift_idea"
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    name: Mapped[str]
    used_on: Mapped[Optional[date]] = mapped_column(default=None,nullable=True)
    obtained: Mapped[bool] = mapped_column(default=False,server_default='false')

    def to_dict(self):
        return {
            "name":self.name,
            "obtained":self.obtained,
            "used_on":self.used_on.isoformat() if self.used_on else "",
        }

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
    date: Mapped[date]
    via: Mapped[InteractionViaType] = mapped_column(type_=EnumDB(InteractionViaType))
    talking_points: Mapped[Optional[str]]
    ask_again: Mapped[bool]

    def to_dict(self):
        return {
            "date":self.date,
            "via":self.via.value,
            "talking_points":self.talking_points,
            "ask_again":self.ask_again,
        }

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(UserFriend).filter(UserFriend.login_id == user_id,UserFriend.friend_id == self.friend_id).first())


class ImportantEvent(Base):
    __tablename__ = "important_event"
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    date: Mapped[date]
    name: Mapped[str]
    description: Mapped[Optional[str]]
    requires_gift: Mapped[bool] = mapped_column(default=False,server_default='false')

    def to_dict(self):
        return {
            "date":self.date,
            "name":self.name,
            "description":self.description,
            "requires_gift":self.requires_gift,
        }

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

    def to_dict(self):
        return {
            "point":self.point,
        }

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(UserFriend).filter(UserFriend.login_id == user_id,UserFriend.friend_id == self.friend_id).first())


class DemoData(Base):
    __tablename__ = "demo_data"
    user_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))
    friend_id: Mapped[uuid.UUID] = mapped_column(type_=UUID(as_uuid=True))

    def accessible_by(self,user_id:uuid.UUID,session:Session):
        return bool(session.query(UserFriend).filter(UserFriend.login_id == user_id,UserFriend.friend_id == self.friend_id).first())



