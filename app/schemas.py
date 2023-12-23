from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Friend(BaseModel):
    __tablename__ = "user_account"
    first_name: str
    last_name: Optional[str]
    address: Optional[str]
    phone_number: Optional[str]
    email: str
    birthday: Optional[datetime]
    notes: Optional[str]
    receives_christmas_gift: bool
    receives_birthday_gift: bool
    id: Optional[str] = None

    class Config:
        orm_mode = True

class GiftIdea(BaseModel):
    __tablename__ = "gift_idea"
    friend_id: str
    name: str
    description: Optional[str]
    url: Optional[str]
    price: Optional[float]
    done: bool
    done_at: Optional[datetime]
    id: Optional[str] = None



