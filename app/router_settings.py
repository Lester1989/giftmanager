from fastapi import APIRouter, Depends,Request
from fastapi import HTTPException,status
from fastapi.responses import HTMLResponse, RedirectResponse,JSONResponse
from fastapi_sqlalchemy import db
from ulid import new as new_ulid
from app.models import User,UserRegistration,UserPasswordReset
from app.template_loading import get_translations, templates
import app.auth as auth
from app.mail_sending import send_registration_mail,send_password_reset_mail
from app.data_seeder import generate_demo_data,remove_demo_data

app = APIRouter()

@app.get("/activate_tutorial")
async def activate_tutorial(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    db_user = db.session.query(User).filter(User.id == current_user.id).first()
    db_user.settings = dict(db_user.settings or {}) | { 'show_tutorial': True, 'tutorial_step': "sheperd-welcome" }
    db.session.commit()
    return RedirectResponse(url='/friends', status_code=status.HTTP_303_SEE_OTHER)

@app.get("/deactivate_tutorial")
async def deactivate_tutorial(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    db_user = db.session.query(User).filter(User.id == current_user.id).first()
    db_user.settings = dict(db_user.settings or {})|{'show_tutorial':False}
    db.session.commit()
    return JSONResponse(content={"status":"ok"},status_code=status.HTTP_200_OK)

@app.get("/set_tutorial_step/{step}")
async def set_tutorial_step(request: Request,current_user: User = Depends(auth.get_current_active_user),step:str=''):
    db_user = db.session.query(User).filter(User.id == current_user.id).first()
    db_user.settings = dict(db_user.settings or {}) | {'tutorial_step': step}
    db.session.commit()
    return JSONResponse(content={"status":"ok"},status_code=status.HTTP_200_OK)

@app.get("/settings", response_class=HTMLResponse)
def settings_get(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    return templates.TemplateResponse("settings.html", {"request": request, "current_user": current_user}|get_translations(request))

@app.post("/settings", response_class=RedirectResponse)
async def settings_post(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    form = await request.form()
    db_user = db.session.query(User).filter(User.id == current_user.id).first()
    db_user.settings = dict(db_user.settings or {}) | {
        'christmas_reminder': bool(form.get('christmas_reminder')),
        'christmas_reminder_days': int(
            form.get('christmas_reminder_days') or 5
        ),
        'days_advance': int(form.get('days_advance') or 50),
        'days_late_reminder': int(form.get('days_late_reminder') or -3),
        'birthday_reminder_days': int(form.get('birthday_reminder_days') or 5),
        'keep_in_touch_interval': int(
            form.get('keep_in_touch_interval') or 30
        ),
        'minimum_gift_ideas': int(form.get('minimum_gift_ideas') or 1),
        'flag_important_event_days': int(
            form.get('flag_important_event_days') or 5
        ),
    }
    db.session.commit()
    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)