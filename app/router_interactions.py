from typing import Optional
from fastapi import APIRouter, Form,Request
from fastapi import HTTPException,Depends,status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_sqlalchemy import db
from datetime import date
from ulid import new as new_ulid
from app.models import User,Friend,UserFriend,GiftIdea,InteractionLog,ImportantEvent,InteractionViaType,TalkingPoint
from app.template_loading import templates,get_translations
import app.auth as auth

app = APIRouter()


@app.post("/add_talking_point/{friend_id}", response_class=RedirectResponse)
def add_talking_point(request: Request, friend_id: str, new_talking_point: str = Form(""),current_user: User = Depends(auth.get_current_active_user)):
    friend = db.session.query(Friend).filter(Friend.id == friend_id).first()
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found")
    talking_point = TalkingPoint(friend_id=friend_id, point=new_talking_point)
    db.session.add(talking_point)
    db.session.commit()
    return RedirectResponse(url=f'/friends/{friend_id}', status_code=status.HTTP_302_FOUND)

@app.get("/delete_talking_point/{talking_point_id}", response_class=RedirectResponse)
def delete_talking_point(request: Request, talking_point_id: str,current_user: User = Depends(auth.get_current_active_user)):
    talking_point:TalkingPoint = db.session.query(TalkingPoint).get(talking_point_id)
    if not talking_point or not talking_point.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Talking Point not found")
    db.session.delete(talking_point)
    db.session.commit()
    return RedirectResponse(url=f'/friends/{talking_point.friend_id}', status_code=status.HTTP_302_FOUND)


@app.get("/new_interaction/{friend_id}", response_class=HTMLResponse)
def new_interaction(request: Request, friend_id: str,current_user: User = Depends(auth.get_current_active_user)):
    friend:Friend = db.session.query(Friend).get(friend_id)
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found for this User")
    gift_ideas = db.session.query(GiftIdea).filter(GiftIdea.friend_id == friend.id).all()
    important_events = db.session.query(ImportantEvent).filter(ImportantEvent.friend_id == friend.id).all()
    talking_points = db.session.query(TalkingPoint).filter(TalkingPoint.friend_id == friend.id).all()
    return templates.TemplateResponse(
        "interaction_new.html", 
        {
            "request": request, 
            "friend": friend, 
            "current_user":current_user,
            "date_arg": date.today(),
            "InteractionViaType": InteractionViaType,
            "talking_point_suggstions": talking_points,
            "gift_ideas": gift_ideas,
            "important_events": important_events
        }|get_translations(request))

@app.post("/add_interaction/{friend_id}", response_class=RedirectResponse)
async def add_interaction(request: Request, friend_id: str, date_arg: date = Form(date.today()), via: InteractionViaType = Form(InteractionViaType.telephone), talking_points: str = Form(""), ask_again: bool = Form(False),current_user: User = Depends(auth.get_current_active_user)):
    friend:Friend = db.session.query(Friend).get(friend_id)
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found for this User")
    interaction = InteractionLog(friend_id=friend_id, date=date_arg, via=via, talking_points=talking_points, ask_again=ask_again)
    db.session.add(interaction)
    db.session.commit()
    return RedirectResponse(url=f'/friends/{friend_id}', status_code=status.HTTP_302_FOUND)

@app.get("/edit_interaction/{interaction_id}", response_class=RedirectResponse)
async def edit_interaction_get(request: Request, interaction_id: str,current_user: User = Depends(auth.get_current_active_user)):
    interaction:InteractionLog = db.session.query(InteractionLog).get(interaction_id)
    if not interaction or not interaction.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Interaction not found")
    friend:Friend = db.session.query(Friend).filter(Friend.id == interaction.friend_id).first()
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found")
    gift_ideas = db.session.query(GiftIdea).filter(GiftIdea.friend_id == friend.id).all()
    important_events = db.session.query(ImportantEvent).filter(ImportantEvent.friend_id == friend.id).all()
    talking_points = db.session.query(TalkingPoint).filter(TalkingPoint.friend_id == friend.id).all()
    return templates.TemplateResponse(
        "interaction_detail.html",
        {
            "request": request,
            "interaction": interaction,
            "friend": friend,
            "current_user":current_user,
            "InteractionViaType": InteractionViaType,
            "talking_point_suggstions": talking_points,
            "gift_ideas": gift_ideas,
            "important_events": important_events
        }|get_translations(request))

@app.post("/edit_interaction/{interaction_id}", response_class=RedirectResponse)
async def edit_interaction(request: Request, interaction_id: str, date_arg: date = Form(date.today()), via: InteractionViaType = Form(InteractionViaType.telephone), talking_points: str = Form(""), ask_again: bool = Form(False),current_user: User = Depends(auth.get_current_active_user)):
    interaction:InteractionLog = db.session.query(InteractionLog).get(interaction_id)
    if not interaction or not interaction.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Interaction not found")
    interaction.date = date_arg
    interaction.via = via
    interaction.talking_points = talking_points
    interaction.ask_again = ask_again
    db.session.commit()
    return RedirectResponse(url=f'/friends/{interaction.friend_id}', status_code=status.HTTP_302_FOUND)