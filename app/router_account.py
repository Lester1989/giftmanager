from fastapi import APIRouter,Request
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_sqlalchemy import db
from ulid import new as new_ulid
from app.models import User
from app.template_loading import templates
import app.auth as auth
import random

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
    db.session.commit()
    access_token = auth.create_access_token(data={"sub": email})
    response = RedirectResponse(url='/')
    response.set_cookie(key="access_token", value=f"Bearer {access_token}")
    return response