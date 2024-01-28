from fastapi import APIRouter,Request
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_sqlalchemy import db
from ulid import new as new_ulid
from app.models import User,UserRegistration,UserPasswordReset
from app.template_loading import templates
import app.auth as auth

app = APIRouter()

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

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
    response = RedirectResponse(url='/')
    response.set_cookie(key="access_token", value=f"Bearer {access_token}")
    return response

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url='/login')
    response.delete_cookie(key="access_token")
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_post(request: Request):
    form = await request.form()
    email = form.get('email')
    password = form.get('password')
    db_user = db.session.query(User).filter(User.email == email).first()
    if db_user:
        # add delay to prevent timing attack
        await auth.fake_delay()
        raise HTTPException(status_code=400, detail="User already exists, please use passwort reset")
    db.session.add(User(email=email,password_hash=auth.get_password_hash(password)))
    db.session.add(UserRegistration(email=email))
    db.session.commit()
    return templates.TemplateResponse("register_done.html", {"request": request})

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
    return templates.TemplateResponse("register_activated.html", {"request": request})

@app.get("/password_reset", response_class=HTMLResponse)
async def password_reset_get(request: Request):
    return templates.TemplateResponse("password_reset.html", {"request": request})

@app.post("/password_reset")
async def password_reset_post(request: Request):
    form = await request.form()
    email = form.get('email')
    if db_user:= db.session.query(User).filter(User.email == email).first():
        db.session.add(UserPasswordReset(email=email))
        db.session.commit()
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/password_reset/{reset_id}/{user_id}", response_class=HTMLResponse)
async def password_reset_confirm_get(request: Request,reset_id:str,user_id:str):
    db_reset = db.session.query(UserPasswordReset).filter(UserPasswordReset.id == reset_id).first()
    if not db_reset:
        raise HTTPException(status_code=404, detail="Reset not found")
    db_user = db.session.query(User).filter(User.id == user_id,User.email==db_reset.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("password_change.html", {"request": request})

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
    return RedirectResponse(url='/login')