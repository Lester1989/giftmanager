from typing import Optional
from fastapi import APIRouter, Form,Request
from fastapi import HTTPException,Depends,status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_sqlalchemy import db
from datetime import datetime, timedelta,date
from ulid import new as new_ulid
from app.models import User,Friend,UserFriend,GiftIdea,InteractionLog,ImportantEvent,InteractionViaType,TalkingPoint
from app.template_loading import templates,get_translations
import app.auth as auth

app = APIRouter()


@app.get("/calendar", response_class=HTMLResponse)
def get_calendar(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    friend_names = {
        friend.id: f"{friend.first_name} {friend.last_name}"
        for friend in db.session.query(Friend).filter(UserFriend.friend_id == Friend.id, UserFriend.login_id == current_user.id).all()
    }
    important_events = db.session.query(ImportantEvent).filter(UserFriend.friend_id == ImportantEvent.friend_id, UserFriend.login_id == current_user.id).all()
    return templates.TemplateResponse("calendar.html", {"request": request, "important_events": important_events, "friend_names": friend_names}|get_translations(request))

