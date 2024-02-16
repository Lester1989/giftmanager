
import os
from fastapi import Depends, FastAPI,Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from starlette.middleware.sessions import SessionMiddleware
from app.mail_sending import send_test_email
from app.template_loading import templates,get_translations
from app.models import User
import app.auth as auth
from app.router_account import app as account_router
from app.router_calendar import app as calendar_router
from app.router_friends import app as friends_router
from app.router_gift import app as gift_router
from app.router_important_event import app as important_event_router
from app.router_interactions import app as interactions_router
from app.router_settings import app as settings_router
from app.router_admin import app as admin_router
import random,string


app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.getenv('CONNECTIONSTRING',"sqlite:///app.db"),engine_args={"echo":False})

@app.middleware("http")
async def check_logged_in(request: Request, call_next):
    if request.url.path == '/login' or request.url.path.startswith('/static'):
        return await call_next(request)
    print('check_logged_in',request.url.path)
    try:
        user = await auth.get_current_user(request.cookies.get('access_token',None))
        request.session['logged_in'] = bool(user)
    except auth.NotAuthenticatedException:
        print('catching NotAuthenticatedException',flush=True)
        request.session['logged_in'] = False
    except HTTPException:
        print('catching HTTPException')
        request.session['logged_in'] = False
    except Exception as e:
        print('catching Exception',e)
        request.session['logged_in'] = False
    if not request.session['logged_in']:
        request.cookies['access_token'] = None
    return await call_next(request)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(auth.app)
app.include_router(account_router)
app.include_router(calendar_router)
app.include_router(friends_router)
app.include_router(gift_router)
app.include_router(important_event_router)
app.include_router(interactions_router)
app.include_router(settings_router)
app.include_router(admin_router)



@app.get("/", response_class=RedirectResponse)
def landing_redirect():
    return RedirectResponse(url='/home')

@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request}|get_translations(request))

@app.get("/home", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request}|get_translations(request))

@app.get("/test_mail")
def test_mail(request: Request,current_user: User = Depends(auth.get_current_active_user)):
    response = send_test_email(current_user.email)
    return templates.TemplateResponse("debug_message.html", {"request": request,"info_message":response}|get_translations(request))

@app.get("/test_exception")
def test_exception(request: Request):
    raise Exception('test_exception')

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print('general_exception_handler',exc)
    return templates.TemplateResponse("error.html", {"request": request,"error_message":exc}|get_translations(request),status_code=500)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url='/login')

    print('HTTPException handler',exc)
    return templates.TemplateResponse("error.html", {"request": request,"error_message":exc}|get_translations(request),status_code=500)


app.add_middleware(SessionMiddleware, secret_key=''.join(random.choice([string.ascii_letters, string.digits, string.punctuation]) for _ in range(50)))

