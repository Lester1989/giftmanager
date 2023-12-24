from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Friend(BaseModel):
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
        from_attributes = True

class GiftIdea(BaseModel):
    friend_id: str
    name: str
    description: Optional[str]
    url: Optional[str]
    price: Optional[float]
    done: bool
    done_at: Optional[datetime]
    id: Optional[str] = None

    class Config:
        from_attributes = True

class Contact(BaseModel):
    friend_id: str
    date: datetime
    via_telephone: bool
    via_email: bool
    via_messenger: bool
    in_person: bool
    id: Optional[str] = None

    class Config:
        from_attributes = True



