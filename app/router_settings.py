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


@app.get("/settings", response_class=HTMLResponse)
def settings_get(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    return templates.TemplateResponse("settings.html", {"request": request, "current_user": current_user}|get_translations(request))

@app.post("/settings", response_class=RedirectResponse)
async def settings_post(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    form = await request.form()
    current_user.settings = {
        'christmas_reminder': bool(form.get('christmas_reminder')),
        'christmas_reminder_days': int(form.get('christmas_reminder_days') or 5),
        'days_advance': int(form.get('days_advance') or 50),
        'days_late_reminder': int(form.get('days_late_reminder') or -3),
        'birthday_reminder_days': int(form.get('birthday_reminder_days') or 5),
        'keep_in_touch_interval': int(form.get('keep_in_touch_interval') or 30),
        'minimum_gift_ideas': int(form.get('minimum_gift_ideas') or 1),
        'flag_important_event_days': int(form.get('flag_important_event_days') or 5),
    }
    db.session.commit()
    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)