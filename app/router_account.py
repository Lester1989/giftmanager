from fastapi import APIRouter, Depends,Request
from fastapi import HTTPException,status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_sqlalchemy import db
from ulid import new as new_ulid
from app.models import User,UserRegistration,UserPasswordReset
from app.template_loading import get_translations, templates
import app.auth as auth
from app.mail_sending import send_registration_mail,send_password_reset_mail
from app.data_seeder import generate_demo_data,remove_demo_data

app = APIRouter()


def new_uuid():
    return new_ulid().uuid

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request}|get_translations(request))

@app.post("/login")
async def login_post(request: Request):
    form = await request.form()
    email = form.get('email')
    password = form.get('password')
    db_user = db.session.query(User).filter(User.email == email).first()
    if not db_user:
        # add delay to prevent timing attack
        await auth.fake_delay()
        raise HTTPException(status_code=404, detail="User not found")
    if not auth.authenticate_user(email, password):
        # add delay to prevent timing attack
        await auth.fake_delay()
        raise HTTPException(status_code=401, detail="Wrong password")
    access_token = auth.create_access_token(data={"sub": db_user.email})
    response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}")
    return response

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url='/login')
    response.delete_cookie(key="access_token")
    request.session.clear()
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request}|get_translations(request))

@app.post("/register")
async def register_post(request: Request):
    form = await request.form()
    email = form.get('email')
    password = form.get('password')
    if db_user := db.session.query(User).filter(User.email == email).first():
        # add delay to prevent timing attack
        await auth.fake_delay()
        raise HTTPException(status_code=400, detail="User already exists, please use passwort reset")
    new_user = User(email=email,password_hash=auth.get_password_hash(password))
    registration = UserRegistration(id=new_uuid(),email=email)
    db.session.add(new_user)
    db.session.add(registration)
    db.session.commit()
    db.session.refresh(new_user)
    db.session.refresh(registration)
    send_registration_mail(email,registration.id,new_user.id)

    return templates.TemplateResponse("register_done.html", {"request": request}|get_translations(request))

@app.get("/confirm_registration/{registration_id}/{user_id}", response_class=HTMLResponse)
async def confirm_registration_get(request: Request,registration_id:str,user_id:str):
    db_registration = db.session.query(UserRegistration).filter(UserRegistration.id == registration_id).first()
    if not db_registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    db_user = db.session.query(User).filter(User.id == user_id,User.email==db_registration.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.is_activated = True
    db.session.delete(db_registration)
    db.session.commit()
    generate_demo_data(db.session,db_user.id)
    return templates.TemplateResponse("register_activated.html", {"request": request}|get_translations(request))

@app.get("/password_reset", response_class=HTMLResponse)
async def password_reset_get(request: Request):
    return templates.TemplateResponse("password_reset.html", {"request": request}|get_translations(request))

@app.post("/password_reset")
async def password_reset_post(request: Request):
    form = await request.form()
    email = form.get('email')
    if db_user:= db.session.query(User).filter(User.email == email).first():
        reset = UserPasswordReset(id=new_uuid(),email=email)
        db.session.add(reset)
        db.session.commit()
        db.session.refresh(reset)
        send_password_reset_mail(email,reset.id,db_user.id)

    return templates.TemplateResponse("login.html", {"request": request}|get_translations(request))

@app.get("/password_reset/{reset_id}/{user_id}", response_class=HTMLResponse)
async def password_reset_confirm_get(request: Request,reset_id:str,user_id:str):
    db_reset = db.session.query(UserPasswordReset).filter(UserPasswordReset.id == reset_id).first()
    if not db_reset or not db_reset.accessible_by(user_id,db.session):
        raise HTTPException(status_code=404, detail="Reset not found")
    return templates.TemplateResponse("password_change.html", {"request": request}|get_translations(request))

@app.post("/password_reset/{reset_id}/{user_id}")
async def password_reset_confirm_post(request: Request,reset_id:str,user_id:str):
    form = await request.form()
    password = form.get('password')
    db_reset = db.session.query(UserPasswordReset).filter(UserPasswordReset.id == reset_id).first()
    if not db_reset:
        raise HTTPException(status_code=404, detail="Reset not found")
    db_user = db.session.query(User).filter(User.id == user_id,User.email==db_reset.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.password_hash = auth.get_password_hash(password)
    db.session.delete(db_reset)
    db.session.commit()
    return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)