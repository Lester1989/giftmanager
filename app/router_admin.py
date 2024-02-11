from typing import Optional
from fastapi import APIRouter, Form,Request
from fastapi import HTTPException,Depends,status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_sqlalchemy import db
from datetime import datetime, timedelta,date
from ulid import new as new_ulid
import uuid
from app.models import User,Friend,UserFriend,GiftIdea,InteractionLog,ImportantEvent,InteractionViaType,TalkingPoint
from app.template_loading import templates,get_translations
import app.auth as auth
import os

app = APIRouter()

@app.get("/usage_overview", response_class=HTMLResponse)
def get_usage(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    if current_user.email not in os.environ.get("ADMIN_EMAILS","").split(","):
        raise HTTPException(status_code=403, detail="Not authorized")
    user_ids:list[User] = db.session.query(User).all()
    user_friends = db.session.query(UserFriend).all()
    gift_ideas = db.session.query(GiftIdea).all()
    interaction_logs = db.session.query(InteractionLog).all()
    important_events = db.session.query(ImportantEvent).all()
    talking_points = db.session.query(TalkingPoint).all()
    # group by user_id and count
    friends_count = { }
    for user in user_ids:
        user_id = user.id
        friend_ids = {user_friend.friend_id for user_friend in user_friends if user_friend.login_id == user_id}
        gift_idea_count = len([ 1 for gift_idea in gift_ideas if gift_idea.friend_id in friend_ids ])
        interaction_log_count = len([ 1 for interaction_log in interaction_logs if interaction_log.friend_id in friend_ids ])
        important_event_count = len([ 1 for important_event in important_events if important_event.friend_id in friend_ids ])
        talking_point_count = len([ 1 for talking_point in talking_points if talking_point.friend_id in friend_ids ])
        friends_count[user_id] = {
            "friends":len(friend_ids),
            "gift_ideas":gift_idea_count,
            "interaction_logs":interaction_log_count,
            "important_events":important_event_count,
            "talking_points":talking_point_count,
            "is_activated":user.is_activated
        }

    return templates.TemplateResponse("admin.html", {"request": request, 'friends_count':friends_count, "current_user":current_user}|get_translations(request))

@app.get("/activate/{user_id}", response_class=RedirectResponse)
async def activate_get(request: Request,user_id:str):
    db_user = db.session.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.is_activated = True
    db.session.commit()
    return RedirectResponse(url='/usage_overview', status_code=status.HTTP_303_SEE_OTHER)

@app.get("/deactivate/{user_id}", response_class=RedirectResponse)
async def deactivate_get(request: Request,user_id:str):
    db_user = db.session.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.is_activated = False
    db.session.commit()
    return RedirectResponse(url='/usage_overview', status_code=status.HTTP_303_SEE_OTHER)