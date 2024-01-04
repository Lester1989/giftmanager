from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Form,Request,status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from app.models import Friend, GiftIdea,InteractionLogAPI,InteractionViaType,InteractionLog,ImportantEvent
from fastapi import FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from fastapi_sqlalchemy import db  # an object to provide global access to a database session
from ulid import new as new_ulid
from app.router_api import app as api


app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.getenv('CONNECTIONSTRING',"sqlite:///app.db"))

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
    friend = Friend(first_name=first_name, last_name=last_name, address=address, phone_number=phone_number, email=email, birthday=birthday, notes=notes, receives_christmas_gift=receives_christmas_gift, receives_birthday_gift=receives_birthday_gift)
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
        friend:Friend = friend # type hinting
        gift_ideas = db.session.query(GiftIdea).filter(GiftIdea.friend_id == friend.id).all() or [
                        GiftIdea(
                            friend_id=friend.id,
                            name="Item 1",
                            description="bla bla bla",
                            url="",
                            price=0.0,
                            done=False,
                            done_at=datetime.now()),
                        GiftIdea(
                            friend_id=friend.id,
                            name="Item 2",
                            description="blib blib blib",
                            url="",
                            price=0.0,
                            done=True,
                            done_at=datetime.now())
                            ]
        interactions = db.session.query(InteractionLog).filter(InteractionLog.friend_id == friend.id).all() or [
                        InteractionLog(
                            friend_id=friend.id,
                            date=datetime.now(),
                            via=InteractionViaType.telephone,
                            talking_points="bla bla",
                            ask_again=True),
                        InteractionLog(
                            friend_id=friend.id,
                            date=datetime.now(),
                            via=InteractionViaType.email,
                            talking_points="blub blub",
                            ask_again=False),
                            ]
        important_events = db.session.query(ImportantEvent).filter(ImportantEvent.friend_id == friend.id).all() or [
                        ImportantEvent(
                            friend_id=friend.id,
                            date=datetime.now(),
                            name="bla bla",
                            description="bla bla"),
                        ImportantEvent(
                            friend_id=friend.id,
                            date=datetime.now()+timedelta(days=1),
                            name="bla bla",
                            description="bla bla"),
                            ]
        return templates.TemplateResponse(
            "friend_detail.html",
            {
                "request": request,
                "friend": friend,
                "InteractionViaType": InteractionViaType,
                "interactions": interactions,
                "gift_ideas": gift_ideas,
                'important_events': important_events,
            })
    else:
        raise HTTPException(status_code=404, detail="Friend not found")

@app.get("/new_interaction/{friend_id}", response_class=HTMLResponse)
def new_interaction(request: Request, friend_id: str):
    if friend := db.session.query(Friend).get(friend_id):
        return templates.TemplateResponse(
            "new_interaction.html", 
            {
                "request": request, 
                "friend": friend, 
                "date": datetime.now().strftime("%Y-%m-%dT%H:%M"),
                "InteractionViaType": InteractionViaType,
                "talking_point_suggstions": [
                    "Hobbies",
                    "Kinder",
                    "Beziehung",
                    "berufliche Situation",
                ]
            })
    else:
        raise HTTPException(status_code=404, detail="Friend not found")
    
@app.post("/add_interaction/{friend_id}", response_class=RedirectResponse)
def add_interaction(request: Request, friend_id: str, date: datetime = Form(datetime.now()), via: InteractionViaType = Form(InteractionViaType.telephone), talking_points: str = Form(""), ask_again: bool = Form(False)):
    interaction = InteractionLogAPI(friend_id=friend_id, date=date, via=via, talking_points=talking_points, ask_again=ask_again)
    db.session.add(interaction)
    db.session.commit()
    return RedirectResponse(url=f'/friends/{friend_id}', status_code=status.HTTP_302_FOUND)

@app.get("/calendar", response_class=HTMLResponse)
def get_calendar(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})



