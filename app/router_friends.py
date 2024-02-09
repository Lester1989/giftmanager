import json
import os
from typing import Optional
from fastapi import APIRouter, Form,Request
from fastapi import HTTPException,Depends,status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi_sqlalchemy import db
from datetime import datetime, timedelta,date
from ulid import new as new_ulid
from app.data_seeder import remove_demo_data,generate_demo_data
from app.models import User,Friend,UserFriend,GiftIdea,InteractionLog,ImportantEvent,InteractionViaType,DemoData,TalkingPoint
from app.template_loading import templates,get_translations
import app.auth as auth

app = APIRouter()


@app.get("/generate_demo_data", response_class=RedirectResponse)
async def generate_demo_data_get(request: Request, current_user: User = Depends(auth.get_current_active_user)):
    generate_demo_data(db.session,current_user.id)
    return RedirectResponse(url='/friends', status_code=status.HTTP_303_SEE_OTHER)

@app.get("/remove_demo_data", response_class=RedirectResponse)
async def remove_demo_data_get(request: Request, current_user: User = Depends(auth.get_current_active_user)):
    remove_demo_data(db.session,current_user.id)
    return RedirectResponse(url='/friends', status_code=status.HTTP_303_SEE_OTHER)

@app.get("/download_friends")
def download_friends(request: Request, current_user: User = Depends(auth.get_current_active_user)):
    friends = db.session.query(Friend).filter(Friend.id == UserFriend.friend_id,current_user.id == UserFriend.login_id).all()
    interactions = db.session.query(InteractionLog).filter(InteractionLog.friend_id == UserFriend.friend_id,current_user.id == UserFriend.login_id).all()
    important_events = db.session.query(ImportantEvent).filter(ImportantEvent.friend_id == UserFriend.friend_id,current_user.id == UserFriend.login_id).all()
    gift_ideas = db.session.query(GiftIdea).filter(GiftIdea.friend_id == UserFriend.friend_id,current_user.id == UserFriend.login_id).all()
    talking_points = db.session.query(TalkingPoint).filter(TalkingPoint.friend_id == UserFriend.friend_id,current_user.id == UserFriend.login_id).all()
    json_data = []
    for friend in friends:
        friend_json = friend.to_dict()
        friend_json['interactions'] = [interaction.to_dict() for interaction in interactions if interaction.friend_id == friend.id]
        friend_json['important_events'] = [important_event.to_dict() for important_event in important_events if important_event.friend_id == friend.id]
        friend_json['gift_ideas'] = [gift_idea.to_dict() for gift_idea in gift_ideas if gift_idea.friend_id == friend.id]
        friend_json['talking_points'] = [talking_point.to_dict() for talking_point in talking_points if talking_point.friend_id == friend.id]
        json_data.append(friend_json)
    return json_data
    
@app.get("/upload_friends")
def upload_friends(request: Request, current_user: User = Depends(auth.get_current_active_user)):
    return templates.TemplateResponse("upload_friends.html", {"request": request,"current_user":current_user}|get_translations(request))

@app.post("/upload_friends", response_class=RedirectResponse)
async def upload_friends_post(request: Request, current_user: User = Depends(auth.get_current_active_user)):
    form = await request.form()
    form_file = form.get('file')
    if not form_file:
        raise HTTPException(status_code=400, detail="No file provided")
    data = form_file.file.read().decode('utf-8')
    json_data:list[dict] = json.loads(data)
    for friend_data in json_data:
        interaction_datas = friend_data.pop('interactions',[])
        important_event_datas = friend_data.pop('important_events',[])
        gift_idea_datas = friend_data.pop('gift_ideas',[])
        talking_point_datas = friend_data.pop('talking_points',[])
        friend = Friend(**friend_data)
        db.session.add(friend)
        db.session.commit()
        db.session.refresh(friend)
        user_friend = UserFriend(login_id=current_user.id,friend_id=friend.id)
        db.session.add(user_friend)
        interactions = [InteractionLog(friend_id=friend.id,**interaction_data) for interaction_data in interaction_datas]
        db.session.add_all(interactions)
        important_events = [ImportantEvent(friend_id=friend.id,**important_event_data) for important_event_data in important_event_datas]
        db.session.add_all(important_events)
        gift_ideas = [GiftIdea(friend_id=friend.id,**gift_idea_data) for gift_idea_data in gift_idea_datas]
        db.session.add_all(gift_ideas)
        talking_points = [TalkingPoint(friend_id=friend.id,**talking_point_data) for talking_point_data in talking_point_datas]
        db.session.add_all(talking_points)
        db.session.commit()
    return RedirectResponse(url='/friends', status_code=status.HTTP_302_FOUND)

@app.get("/friends", response_class=HTMLResponse)
def get_friends(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    friends = db.session.query(Friend).filter(Friend.id == UserFriend.friend_id,current_user.id == UserFriend.login_id).all()
    interactions = db.session.query(InteractionLog).filter(InteractionLog.friend_id == UserFriend.friend_id,current_user.id == UserFriend.login_id).all()
    important_events = db.session.query(ImportantEvent).filter(ImportantEvent.friend_id == UserFriend.friend_id,current_user.id == UserFriend.login_id).order_by(ImportantEvent.date.desc()).all()
    gift_ideas = db.session.query(GiftIdea).filter(GiftIdea.friend_id == UserFriend.friend_id,current_user.id == UserFriend.login_id).all()
    days_until_christmas = (date(date.today().year,12,24)-date.today()).days
    has_demo_data = bool(list(db.session.query(DemoData).filter(DemoData.user_id == current_user.id).all()))
    friends_alerts = {
        friend.id:{
            'days_since_last_interaction':(date.today() -sorted([interaction for interaction in interactions if interaction.friend_id == friend.id],key=lambda x: x.date,reverse=True)[0].date).days if interactions else 1000,
            'important_events': [(important_event.name,important_event.date) for important_event in important_events if important_event.friend_id == friend.id and abs(important_event.days_until)<=current_user.settings.get('flag_important_event_days',5)],
            'gift_ideas': len([gift_idea for gift_idea in gift_ideas if gift_idea.friend_id == friend.id]),
            'days_until_christmas': days_until_christmas if friend.receives_christmas_gift else None,
            'days_until_birthday': (friend.birthday-date.today()).days if friend.birthday and friend.receives_birthday_gift else None,
        }
        for friend in friends
    }
    return templates.TemplateResponse("friend_overview.html", {"request": request,"current_user":current_user, "friends": friends, "friends_alerts": friends_alerts,'has_demo_data':has_demo_data}|get_translations(request))


@app.post("/add_friend", response_class=RedirectResponse)
async def add_friend(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    form = await request.form()
    first_name:str = form.get('first_name') or ""
    last_name:str = form.get('last_name') or ""
    address:str = form.get('address') or ""
    phone_number:str = form.get('phone_number') or ""
    email:str = form.get('email') or ""
    birthday:str = form.get('birthday') or ""
    notes:str = form.get('notes') or ""
    receives_christmas_gift:str = bool(form.get('receives_christmas_gift'))
    receives_birthday_gift:str = bool(form.get('receives_birthday_gift'))

    friend = Friend(first_name=first_name, last_name=last_name, address=address, phone_number=phone_number, email=email, birthday=birthday, notes=notes, receives_christmas_gift=receives_christmas_gift, receives_birthday_gift=receives_birthday_gift)
    db.session.add(friend)
    db.session.commit()
    db.session.refresh(friend)
    user_friend = UserFriend(login_id=current_user.id,friend_id=friend.id)
    db.session.add(user_friend)
    db.session.commit()
    return RedirectResponse(url='/friends', status_code=status.HTTP_302_FOUND)

@app.post("/edit_friend/{friend_id}", response_class=RedirectResponse)
async def edit_friend(request: Request, friend_id: str,current_user: User = Depends(auth.get_current_active_user)):
    friend:Friend = db.session.query(Friend).filter(Friend.id == friend_id).first()
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found")
    form = await request.form()
    friend.first_name = form.get('first_name') or friend.first_name
    friend.last_name = form.get('last_name') or friend.last_name
    friend.address = form.get('address') or friend.address
    friend.phone_number = form.get('phone_number') or friend.phone_number
    friend.email = form.get('email') or friend.email
    friend.birthday = form.get('birthday') or friend.birthday
    friend.notes = form.get('notes') or friend.notes
    friend.receives_christmas_gift = bool(form.get('receives_christmas_gift'))
    friend.receives_birthday_gift = bool(form.get('receives_birthday_gift'))
    db.session.commit()
    return RedirectResponse(url='/friends', status_code=status.HTTP_302_FOUND)

@app.get("/delete_friend/{friend_id}", response_class=RedirectResponse)
def delete_friend(request: Request, friend_id: str,current_user: User = Depends(auth.get_current_active_user)):
    friend:Friend = db.session.query(Friend).get(friend_id)
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found for this User")
    user_friend = db.session.query(UserFriend).filter(UserFriend.login_id == current_user.id,UserFriend.friend_id == friend_id).first()
    db.session.delete(user_friend)
    db.session.delete(friend)
    db.session.commit()
    return RedirectResponse(url='/friends', status_code=status.HTTP_302_FOUND)

@app.get("/friends/{friend_id}", response_class=HTMLResponse)
def get_friend(request: Request, friend_id: str,current_user: User = Depends(auth.get_current_active_user)):
    friend:Friend = db.session.query(Friend).get(friend_id)
    if not friend or not friend.accessible_by(current_user.id,db.session):
        raise HTTPException(status_code=404, detail="Friend not found for this User")
    gift_ideas = db.session.query(GiftIdea).filter(GiftIdea.friend_id == friend.id).all()
    interactions = db.session.query(InteractionLog).filter(InteractionLog.friend_id == friend.id).order_by(InteractionLog.date.desc()).all()
    important_events = db.session.query(ImportantEvent).filter(ImportantEvent.friend_id == friend.id).all()
    return templates.TemplateResponse(
        "friend_detail.html",
        {
            "request": request,
            "current_user":current_user,
            "friend": friend,
            "InteractionViaType": InteractionViaType,
            "interactions": interactions,
            "gift_ideas": gift_ideas,
            'important_events': sorted(
                [imp_event for imp_event in important_events if current_user.settings.get('days_advance',50) >= imp_event.days_until >= -current_user.settings.get('flag_important_event_days',5)],
                key=lambda x: x.date,reverse=True),
        }|get_translations(request))