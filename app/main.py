from fastapi import FastAPI
from app.models import Friend, GiftIdea
from app.models_api import Friend as FriendAPI, GiftIdea as GiftIdeaAPI
from fastapi import FastAPI, HTTPException
from app.models import Friend, GiftIdea
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from fastapi_sqlalchemy import db  # an object to provide global access to a database session
from ulid import new as new_ulid


app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url="sqlite:///app.db")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/friends", response_model=list[FriendAPI])
def get_friends():
    return db.session.query(Friend).all()

@app.get("/friends/{friend_id}", response_model=FriendAPI)
def get_friend(friend_id: str):
    friend = db.session.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    return friend

@app.post("/friends", response_model=FriendAPI)
def create_friend(friend: FriendAPI):
    if not friend.id:
        friend.id = str(new_ulid())
    db.session.add(Friend(**friend.model_dump()))
    db.session.commit()
    return friend

@app.put("/friends/{friend_id}", response_model=FriendAPI)
def update_friend(friend_id: str, updated_friend: FriendAPI):
    friend:Friend = db.session.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    friend.first_name = updated_friend.first_name
    friend.last_name = updated_friend.last_name
    friend.address = updated_friend.address
    friend.phone_number = updated_friend.phone_number
    friend.email = updated_friend.email
    friend.birthday = updated_friend.birthday
    friend.notes = updated_friend.notes
    friend.receives_christmas_gift = updated_friend.receives_christmas_gift
    friend.receives_birthday_gift = updated_friend.receives_birthday_gift
    db.session.commit()
    return friend

@app.delete("/friends/{friend_id}", response_model=dict)
def delete_friend(friend_id: str):
    friend = db.session.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    db.session.delete(friend)
    db.session.commit()
    return {"message": "Friend deleted successfully"}

# CRUD routes for GiftIdea model
@app.get("/giftideas", response_model=list[GiftIdeaAPI])
def get_giftideas():
    return db.session.query(GiftIdea).all()

@app.get("/giftideas/{giftidea_id}", response_model=GiftIdeaAPI)
def get_giftidea(giftidea_id: str):
    giftidea = db.session.query(GiftIdea).get(giftidea_id)
    if not giftidea:
        raise HTTPException(status_code=404, detail="Gift idea not found")
    return giftidea

@app.post("/giftideas", response_model=GiftIdeaAPI)
def create_giftidea(giftidea: GiftIdeaAPI):
    if not giftidea.id:
        giftidea.id = str(new_ulid())
    db.session.add(GiftIdea(**giftidea.model_dump()))
    db.session.commit()
    return giftidea

@app.put("/giftideas/{giftidea_id}", response_model=GiftIdeaAPI)
def update_giftidea(giftidea_id: int, updated_giftidea: GiftIdeaAPI):
    giftidea:GiftIdea = db.session.query(GiftIdea).get(giftidea_id)
    if not giftidea:
        raise HTTPException(status_code=404, detail="Gift idea not found")
    giftidea.friend_id = updated_giftidea.friend_id
    giftidea.name = updated_giftidea.name
    giftidea.description = updated_giftidea.description
    giftidea.url = updated_giftidea.url
    giftidea.price = updated_giftidea.price
    giftidea.done = updated_giftidea.done
    giftidea.done_at = updated_giftidea.done_at

    db.session.commit()
    return giftidea

@app.delete("/giftideas/{giftidea_id}", response_model=dict)
def delete_giftidea(giftidea_id: str):
    giftidea = db.session.query(GiftIdea).get(giftidea_id)
    if not giftidea:
        raise HTTPException(status_code=404, detail="Gift idea not found")
    db.session.delete(giftidea)
    db.session.commit()
    return {"message": "Gift idea deleted successfully"}


