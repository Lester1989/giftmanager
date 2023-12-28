from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Form,Request,status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import Friend, GiftIdea
from app.schemas import Friend as FriendAPI, GiftIdea as GiftIdeaAPI
from fastapi import FastAPI, HTTPException
from app.models import Friend, GiftIdea
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from fastapi_sqlalchemy import db  # an object to provide global access to a database session
from ulid import new as new_ulid
from app.router_api import app as api


app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url="sqlite:///app.db")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(api)

@app.get("/", response_class=RedirectResponse)
def landing_redirect():
    return RedirectResponse(url='/home')


@app.get("/home", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/friends", response_class=HTMLResponse)
def get_friends(request: Request):
    friends = db.session.query(Friend).all()
    return templates.TemplateResponse("friend_overview.html", {"request": request, "friends": friends})

@app.post("/add_friend", response_class=RedirectResponse)
def add_friend(request: Request,first_name: str=Form(), last_name: Optional[str] = Form(""), address: Optional[str] = Form(""), phone_number: Optional[str] = Form(""), email: str = Form(""), birthday: datetime = Form(datetime.now()), notes: Optional[str] = Form(""), receives_christmas_gift: Optional[bool] = Form(False), receives_birthday_gift: Optional[bool] = Form(False)):
    friend = Friend(id=str(new_ulid()), first_name=first_name, last_name=last_name, address=address, phone_number=phone_number, email=email, birthday=birthday, notes=notes, receives_christmas_gift=receives_christmas_gift, receives_birthday_gift=receives_birthday_gift)
    db.session.add(friend)
    db.session.commit()
    return RedirectResponse(url='/friends', status_code=status.HTTP_302_FOUND)

@app.get("/delete_friend/{friend_id}", response_class=RedirectResponse)
def delete_friend(request: Request, friend_id: str):
    friend = db.session.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    db.session.delete(friend)
    db.session.commit()
    return RedirectResponse(url='/friends', status_code=status.HTTP_302_FOUND)

@app.get("/friends/{friend_id}", response_class=HTMLResponse)
def get_friend(request: Request, friend_id: str):
    if friend := db.session.query(Friend).get(friend_id):
        return templates.TemplateResponse("friend_detail.html", {"request": request, "friend": friend})
    else:
        raise HTTPException(status_code=404, detail="Friend not found")

@app.get("/calendar", response_class=HTMLResponse)
def get_calendar(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})



