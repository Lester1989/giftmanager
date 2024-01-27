import os
import random
import string
# get secret from environment variable
JWT_KEY =  os.environ.get("JWT_KEY",''.join(string.ascii_letters + string.digits for _ in range(32)))
from sqlalchemy import create_engine, or_

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from enum import Enum
from fastapi import APIRouter
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from sqlalchemy import Column, String, JSON, Integer
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, status,Request
from fastapi.security import OAuth2, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Annotated,Optional,Dict
from app.models import User,UserStatus
from fastapi import Body
from uuid import UUID
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180


class UserResponse(BaseModel):
    id:UUID
    email:str
    password_hash:str
    is_activated:bool
    access_token:str

class UserRequest(BaseModel):
    email:str
    password:str

class NotAuthenticatedException(Exception):
    pass

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")  #changed to accept access token from httpOnly Cookie

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param
    
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")


app = APIRouter()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user( email: str)-> User|None:
    with db():
        if (user := db.session.query(User)
                .filter(User.email == email)
                .first()):
            return user


def authenticate_user(email: str, password: str):
    if user := get_user(email):
        return user if verify_password(password, user.password_hash) else False
    else:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, JWT_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme))-> User:
    if token is None:
        return None
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email: str = ""
    try:
        if token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
        payload = jwt.decode(token, JWT_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") # type: ignore
        if email is None:
            raise NotAuthenticatedException
    except JWTError as e:
        print('JWTError',e)
        raise credentials_exception from e
    user = get_user(email) # type: ignore
    if user is None:
        raise NotAuthenticatedException
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user))-> User:
    if not current_user.is_activated:
        raise HTTPException(status_code=400, detail="User is not active!")
    return current_user


@app.post("/token", response_model=UserResponse,tags=["auth"],description="coming soon")
async def login_for_access_token(request: Request,form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return UserResponse(
        id=user.id,
        email=user.email,
        password_hash=user.password_hash,
        is_activated=user.is_activated,
        access_token=access_token,
    )


@app.post("/create_user",tags=["auth"],description="coming soon")
async def create_user( request: Request, user:UserRequest ):
    hashed_password = get_password_hash(user.password) 
    existing = db.session.query(User).all() 
    if existing_user := next((x for x in existing if user.email == x.email), False):
        return {'success':False,'message':'User already exists','login_id':existing_user.id} 
    db_login = User(
        email=user.email,
        password_hash=hashed_password,
        is_activated=False,
        settings={},
    )
    db.session.add(db_login)
    db.session.commit()
    db.session.refresh(db_login)
    return {'success':True,'message':'User created','login_id':db_login.id}
