from fastapi import APIRouter, Form,Request
from fastapi import HTTPException,Depends,status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_sqlalchemy import db
from datetime import date
from ulid import new as new_ulid
from app.models import User,Friend,UserFriend,ImportantEvent
from app.template_loading import templates,get_translations
import app.auth as auth

app = APIRouter()

@app.get("/new_important_event", response_class=HTMLResponse)
def add_important_event(request: Request, friend_id: str,current_user: User = Depends(auth.get_current_active_user)):
    friend = db.session.query(Friend).filter(UserFriend.friend_id == Friend.id, UserFriend.login_id == current_user.id).get(friend_id)
    return templates.TemplateResponse("new_important_event.html", {"request": request, "friend": friend}|get_translations(request))

@app.post("/add_important_event/{friend_id}", response_class=RedirectResponse)
def add_important_event_post(request: Request, friend_id: str, new_important_event_date: date = Form(date.today()), new_important_event: str = Form(""), new_important_event_details: str = Form(""),current_user: User = Depends(auth.get_current_active_user)):
    user_friend = db.session.query(UserFriend).filter(UserFriend.login_id == current_user.id,UserFriend.friend_id == friend_id).first()
    if not user_friend:
        raise HTTPException(status_code=404, detail="Friend not found for this User")
    important_event = ImportantEvent(friend_id=friend_id, date=new_important_event_date, name=new_important_event, description=new_important_event_details)
    db.session.add(important_event)
    db.session.commit()
    return RedirectResponse(url=f'/friends/{friend_id}', status_code=status.HTTP_302_FOUND)

@app.get("/delete_important_event/{important_event_id}", response_class=RedirectResponse)
def delete_important_event(request: Request, important_event_id: str,current_user: User = Depends(auth.get_current_active_user)):
    important_event:ImportantEvent = db.session.query(ImportantEvent).get(important_event_id)
    if not important_event:
        raise HTTPException(status_code=404, detail="Important Event not found")
    user_friend = db.session.query(UserFriend).filter(UserFriend.login_id == current_user.id,UserFriend.friend_id == important_event.friend_id).first()
    if not user_friend:
        raise HTTPException(status_code=404, detail="Friend not found for this User")
    db.session.delete(important_event)
    db.session.commit()
    return RedirectResponse(url=f'/friends/{important_event.friend_id}', status_code=status.HTTP_302_FOUND)
