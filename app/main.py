from fastapi import FastAPI,Request
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

@app.get("/friends/{friend_id}", response_class=HTMLResponse)
def get_friend(request: Request, friend_id: str):
    friend = db.session.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    return templates.TemplateResponse("friend_detail.html", {"request": request, "friend": friend})

@app.get("/calendar", response_class=HTMLResponse)
def get_calendar(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})



