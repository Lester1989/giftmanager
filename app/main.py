from datetime import datetime, timedelta,date
from typing import Optional
from fastapi import Depends, FastAPI, Form,Request,status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from app.models import Friend, GiftIdea,InteractionLogAPI,InteractionViaType,InteractionLog,ImportantEvent,TalkingPoint
from fastapi import FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from fastapi_sqlalchemy import db  # an object to provide global access to a database session
from ulid import new as new_ulid
from app.router_api import app as api
from app.mail_sending import send_test_email
from app.template_loading import templates,get_translations
from app.models import User
import app.auth as auth
from app.router_account import app as account_router
from app.router_calendar import app as calendar_router
from app.router_friends import app as friends_router
from app.router_gift import app as gift_router
from app.router_important_event import app as important_event_router
from app.router_interactions import app as interactions_router


app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.getenv('CONNECTIONSTRING',"sqlite:///app.db"))

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api)
app.include_router(auth.app)
app.include_router(account_router)
app.include_router(calendar_router)
app.include_router(friends_router)
app.include_router(gift_router)
app.include_router(important_event_router)
app.include_router(interactions_router)


@app.get("/", response_class=RedirectResponse)
def landing_redirect():
    return RedirectResponse(url='/home')


@app.get("/home", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request}|get_translations(request))

@app.get("/test_mail")
def test_mail(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    response = send_test_email()
    return str(response)



