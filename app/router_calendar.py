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
def get_calendar(request: Request,current_user: User = Depends(auth.get_current_active_user),days_advance:int=-1):
    friends = db.session.query(Friend).filter(UserFriend.friend_id == Friend.id, UserFriend.login_id == current_user.id).all()
    friend_names = {
        friend.id: f"{friend.first_name} {friend.last_name}"
        for friend in friends
    }
    important_events = db.session.query(ImportantEvent).filter(UserFriend.friend_id == ImportantEvent.friend_id, UserFriend.login_id == current_user.id).all()
    translations = get_translations(request)
    for friend in friends:
        important_events.extend(friend.special_events())
    if days_advance == -1:
        days_advance = current_user.settings.get('days_advance',50)
    important_events = [event for event in important_events if event.days_until < days_advance and event.days_until >= current_user.settings.get('days_late_reminder',-3)]
    return templates.TemplateResponse("calendar.html", {"request": request, "current_user":current_user, "important_events": sorted(important_events,key=lambda event:event.days_until), "friend_names": friend_names}|translations)

