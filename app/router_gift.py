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


@app.get("/new_gift_idea", response_class=HTMLResponse)
def add_gift_idea(request: Request, friend_id: str,current_user: User = Depends(auth.get_current_active_user)):
    friend:Friend = db.session.query(Friend).filter(Friend.id == friend_id).first()
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found")
    return templates.TemplateResponse("new_gift_idea.html", {"request": request, "friend": friend}|get_translations(request))

@app.post("/add_gift_idea/{friend_id}", response_class=RedirectResponse)
def add_gift_idea_post(request: Request, friend_id: str, new_gift_idea: str = Form(""),current_user: User = Depends(auth.get_current_active_user)):
    friend:Friend = db.session.query(Friend).filter(Friend.id == friend_id).first()
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found for this User")
    gift_idea = GiftIdea(friend_id=friend_id, name=new_gift_idea, done=False)
    db.session.add(gift_idea)
    db.session.commit()
    return RedirectResponse(url=f'/friends/{friend_id}', status_code=status.HTTP_302_FOUND)

@app.get("/delete_gift_idea/{gift_idea_id}", response_class=RedirectResponse)
def delete_gift_idea(request: Request, gift_idea_id: str,current_user: User = Depends(auth.get_current_active_user)):
    gift_idea:GiftIdea = db.session.query(GiftIdea).get(gift_idea_id)
    if not gift_idea or not gift_idea.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Gift Idea not found")
    db.session.delete(gift_idea)
    db.session.commit()
    return RedirectResponse(url=f'/friends/{gift_idea.friend_id}', status_code=status.HTTP_302_FOUND)

@app.get("/complete_gift_idea/{gift_idea_id}", response_class=RedirectResponse)
def complete_gift_idea(request: Request, gift_idea_id: str,current_user: User = Depends(auth.get_current_active_user)):
    gift_idea:GiftIdea = db.session.query(GiftIdea).get(gift_idea_id)
    if not gift_idea or not gift_idea.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Gift Idea not found")
    gift_idea.done = True
    db.session.commit()
    return RedirectResponse(url=f'/friends/{gift_idea.friend_id}', status_code=status.HTTP_302_FOUND)
