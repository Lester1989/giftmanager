from app.models import InteractionViaType, User, Friend,UserFriend, GiftIdea, InteractionLog, ImportantEvent, TalkingPoint,DemoData
from faker import Faker
from sqlalchemy.orm import Session
import random
import uuid
from ulid import new as new_ulid

def new_uuid():
    return new_ulid().uuid

fake = Faker()

def generate_friends(session:Session, user_id:uuid.UUID):
    friend_ids = []
    for i in range(5):
        friend = Friend(
            first_name=fake.first_name(),
            last_name=f"DEMO_{i}",
            address=fake.address(),
            phone_number=fake.phone_number(),
            email=fake.email(),
            birthday=fake.date_of_birth(minimum_age=18, maximum_age=100),
            notes=fake.text()+"\nnot real data, just for demo purposes.",
            receives_christmas_gift=random.choice([True, False]),
            receives_birthday_gift=random.choice([True, False]),
        )
        session.add(friend)
        session.commit()
        session.refresh(friend)
        user_friend = UserFriend(login_id=user_id, friend_id=friend.id)
        session.add(user_friend)
        session.commit()

    session.add_all([
        DemoData(data_id=friend_id,user_id=user_id)
        for friend_id in friend_ids
    ])
    session.commit()
    return friend_ids

def generate_gift_ideas(session:Session, friend_ids:list[uuid.UUID]):
    session.add_all([
        GiftIdea(
            friend_id=friend_id,
            name=fake.text(),
            done=random.choice([True, False, False, False])
        )
        for _ in range(random.choice([0,1,1,1,2,3]))
        for friend_id in friend_ids
    ])
    session.commit()

def generate_interaction_logs(session:Session, friend_ids:list[uuid.UUID]):
    session.add_all([
        InteractionLog(
            friend_id=friend_id,
            date=fake.date_this_year(),
            via=random.choice(list(InteractionViaType)),
            talking_points=fake.text(),
            ask_again=random.choice([True, False])
        )
        for _ in range(random.choice([0,1,1,1,2,3]))
        for friend_id in friend_ids
    ])
    session.commit()

def generate_important_events(session:Session, friend_ids:list[uuid.UUID]):
    session.add_all([
        ImportantEvent(
            friend_id=friend_id,
            date=fake.date_this_year(after_today=True),
            name=fake.text(),
            description=fake.text(),
        )
        for _ in range(random.choice([0,1,1,1,2,3]))
        for friend_id in friend_ids
    ])
    session.commit()

def generate_talking_points(session:Session, friend_ids:list[uuid.UUID]):
    session.add_all([
        TalkingPoint(
            friend_id=friend_id,
            point=fake.text()
        )
        for _ in range(random.choice([0,1,1,1,2,3]))
        for friend_id in friend_ids
    ])
    session.commit()

def generate_demo_data(session:Session, user_id:uuid.UUID):
    friend_ids = generate_friends(session, user_id)
    generate_gift_ideas(session, friend_ids)
    generate_interaction_logs(session, friend_ids)
    generate_important_events(session, friend_ids)
    generate_talking_points(session, friend_ids)

def remove_demo_data(session:Session, user_id:uuid.UUID):
    demo_data:list[DemoData] = session.query(DemoData).filter(DemoData.user_id == user_id).all()
    for data in demo_data:
        session.query(Friend).filter(Friend.id == data.friend_id).delete()
        session.query(UserFriend).filter(UserFriend.friend_id == data.friend_id).delete()
        session.query(GiftIdea).filter(GiftIdea.friend_id == data.friend_id).delete()
        session.query(InteractionLog).filter(InteractionLog.friend_id == data.friend_id).delete()
        session.query(ImportantEvent).filter(ImportantEvent.friend_id == data.friend_id).delete()
        session.query(TalkingPoint).filter(TalkingPoint.friend_id == data.friend_id).delete()
    session.query(DemoData).filter(DemoData.user_id == user_id).delete()
    session.commit()

