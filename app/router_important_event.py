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
    friend = db.session.query(Friend).filter(Friend.id == friend_id).first()
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found")
    return templates.TemplateResponse("new_important_event.html", {"request": request, "friend": friend,"current_user":current_user}|get_translations(request))

@app.post("/add_important_event/{friend_id}", response_class=RedirectResponse)
def add_important_event_post(request: Request, friend_id: str, new_important_event_date: date = Form(date.today()), new_important_event: str = Form(""), new_important_event_details: str = Form(""), requires_gift:bool=Form(False), current_user: User = Depends(auth.get_current_active_user)):
    friend = db.session.query(Friend).filter(Friend.id == friend_id).first()
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found")
    important_event = ImportantEvent(friend_id=friend_id, date=new_important_event_date, name=new_important_event, description=new_important_event_details, requires_gift=requires_gift)
    db.session.add(important_event)
    db.session.commit()
    return RedirectResponse(url=f'/friends/{friend_id}', status_code=status.HTTP_302_FOUND)

@app.get("/delete_important_event/{important_event_id}", response_class=RedirectResponse)
def delete_important_event(request: Request, important_event_id: str,current_user: User = Depends(auth.get_current_active_user)):
    important_event:ImportantEvent = db.session.query(ImportantEvent).get(important_event_id)
    if not important_event or not important_event.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Important Event not found")
    db.session.delete(important_event)
    db.session.commit()
    return RedirectResponse(url=f'/friends/{important_event.friend_id}', status_code=status.HTTP_302_FOUND)
