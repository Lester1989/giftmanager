from typing import Optional
from fastapi import APIRouter, Form,Request
from fastapi import HTTPException,Depends,status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_sqlalchemy import db
from datetime import datetime, timedelta,date
from ulid import new as new_ulid
from app.models import User,Friend,UserFriend,GiftIdea,InteractionLog,ImportantEvent,InteractionViaType,DemoData
from app.template_loading import templates,get_translations
import app.auth as auth

app = APIRouter()

@app.get("/friends", response_class=HTMLResponse)
def get_friends(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    friends = db.session.query(Friend).filter(Friend.id == UserFriend.friend_id,current_user.id == UserFriend.login_id).all()
    interactions = db.session.query(InteractionLog).filter(InteractionLog.friend_id == UserFriend.friend_id,current_user.id == UserFriend.login_id).order_by(InteractionLog.date).all()
    important_events = db.session.query(ImportantEvent).filter(ImportantEvent.friend_id == UserFriend.friend_id,current_user.id == UserFriend.login_id).all()
    gift_ideas = db.session.query(GiftIdea).filter(GiftIdea.friend_id == UserFriend.friend_id,current_user.id == UserFriend.login_id, not GiftIdea.done).all()
    days_until_christmas = (date(date.today().year,12,24)-date.today()).days
    has_demo_data = bool(list(db.session.query(DemoData).filter(DemoData.user_id == current_user.id).all()))
    friends_alerts = {
        friend.id:{
            'days_since_last_interaction':(date.today() -sorted([interaction for interaction in interactions if interaction.friend_id == friend.id],key=lambda x: x.date,reverse=True)[0].date) if interactions else 1000,
            'important_events': [(important_event.name,important_event.date) for important_event in important_events if important_event.friend_id == friend.id and abs(date.today()-important_event.date)<5],
            'gift_ideas': len([gift_idea for gift_idea in gift_ideas if gift_idea.friend_id == friend.id]),
            'days_until_christmas': days_until_christmas if friend.receives_christmas_gift else None,
            'days_until_birthday': (friend.birthday.date()-date.today()).days if friend.birthday and friend.receives_birthday_gift else None,
        }
        for friend in friends
    }
    return templates.TemplateResponse("friend_overview.html", {"request": request, "friends": friends, "friends_alerts": friends_alerts,'has_demo_data':has_demo_data}.update(get_translations(request)))


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
    friend:Friend = db.session.query(Friend).filter(UserFriend.friend_id == friend_id, UserFriend.login_id == current_user.id).get(friend_id)
    if not friend:
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
    user_friend = db.session.query(UserFriend).filter(UserFriend.login_id == current_user.id,UserFriend.friend_id == friend_id).first()
    friend = db.session.query(Friend).get(friend_id)
    if not friend or not user_friend:
        raise HTTPException(status_code=404, detail="Friend not found for this User")
    db.session.delete(friend)
    db.session.commit()
    return RedirectResponse(url='/friends', status_code=status.HTTP_302_FOUND)

@app.get("/friends/{friend_id}", response_class=HTMLResponse)
def get_friend(request: Request, friend_id: str,current_user: User = Depends(auth.get_current_active_user)):
    user_friend = db.session.query(UserFriend).filter(UserFriend.login_id == current_user.id,UserFriend.friend_id == friend_id).first()
    if not user_friend:
        raise HTTPException(status_code=404, detail="Friend not found for this User")
    if friend := db.session.query(Friend).get(friend_id):
        friend:Friend = friend # type hinting
        gift_ideas = db.session.query(GiftIdea).filter(GiftIdea.friend_id == friend.id).all() or [
                        GiftIdea(
                            friend_id=friend.id,
                            name="Item 1",
                            done=False),
                        GiftIdea(
                            friend_id=friend.id,
                            name="Item 2",
                            done=True)
                            ]
        interactions = db.session.query(InteractionLog).filter(InteractionLog.friend_id == friend.id).all() or [
                        InteractionLog(
                            friend_id=friend.id,
                            date=datetime.now(),
                            via=InteractionViaType.telephone,
                            talking_points="bla bla",
                            ask_again=True),
                        InteractionLog(
                            friend_id=friend.id,
                            date=datetime.now(),
                            via=InteractionViaType.email,
                            talking_points="blub blub",
                            ask_again=False),
                            ]
        important_events = db.session.query(ImportantEvent).filter(ImportantEvent.friend_id == friend.id).all() or [
                        ImportantEvent(
                            friend_id=friend.id,
                            date=datetime.now(),
                            name="bla bla",
                            description="bla bla"),
                        ImportantEvent(
                            friend_id=friend.id,
                            date=datetime.now()+timedelta(days=1),
                            name="bla bla",
                            description="bla bla"),
                            ]
        return templates.TemplateResponse(
            "friend_detail.html",
            {
                "request": request,
                "friend": friend,
                "InteractionViaType": InteractionViaType,
                "interactions": interactions,
                "gift_ideas": gift_ideas,
                'important_events': important_events,
            }.update(get_translations(request)))
    else:
        raise HTTPException(status_code=404, detail="Friend not found")