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
    return templates.TemplateResponse("new_gift_idea.html", {"request": request, "friend": friend,"current_user":current_user}|get_translations(request))

@app.post("/add_gift_idea/{friend_id}", response_class=RedirectResponse)
def add_gift_idea_post(request: Request, friend_id: str, new_gift_idea: str = Form(""),current_user: User = Depends(auth.get_current_active_user)):
    friend:Friend = db.session.query(Friend).filter(Friend.id == friend_id).first()
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found for this User")
    gift_idea = GiftIdea(friend_id=friend_id, name=new_gift_idea, obtained=False, used_on=None)
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

@app.get("/edit_gift_idea/{gift_idea_id}/for/{friend_id}", response_class=HTMLResponse)
async def edit_gift_idea(request: Request, gift_idea_id: str, friend_id: str,current_user: User = Depends(auth.get_current_active_user)):
    gift_idea:GiftIdea = db.session.query(GiftIdea).get(gift_idea_id)
    if not gift_idea or not gift_idea.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Gift Idea not found")
    friend:Friend = db.session.query(Friend).filter(Friend.id == friend_id).first()
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found")
    impporant_events:list[ImportantEvent] = db.session.query(ImportantEvent).filter(ImportantEvent.friend_id == friend_id).order_by(ImportantEvent.date.desc()).all()
    return templates.TemplateResponse(
        "gift_idea_details.html",
        {
            "request": request,
            "gift_idea": gift_idea,
            "friend": friend,
            "important_events":[imp_event for imp_event in impporant_events+friend.special_events() if imp_event.is_upcoming],
            "current_user":current_user
        }|get_translations(request))

@app.post("/edit_gift_idea/{gift_idea_id}/for/{friend_id}", response_class=RedirectResponse)
async def edit_gift_idea_post(request: Request, gift_idea_id: str, friend_id: str, current_user: User = Depends(auth.get_current_active_user)):
    gift_idea:GiftIdea = db.session.query(GiftIdea).get(gift_idea_id)
    if not gift_idea or not gift_idea.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Gift Idea not found")
    friend:Friend = db.session.query(Friend).filter(Friend.id == friend_id).first()
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found")
    form = await request.form()
    gift_idea.name = form.get('name')
    gift_idea.obtained = bool(form.get('obtained'))
    gift_idea.used_on = datetime.strptime(form.get('used_on'),"%Y-%m-%d") if form.get('used_on') else None
    db.session.commit()
    return RedirectResponse(url=f'/friends/{friend_id}', status_code=status.HTTP_302_FOUND)
