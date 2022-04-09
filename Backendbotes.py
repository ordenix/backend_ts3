from datetime import datetime, timedelta
from typing import Optional
import time
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import bans
from pydantic import BaseModel
from typing import List
import webDeamon
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, modelsdb, schemas
from database import *
from starlette.middleware.cors import CORSMiddleware
import public
import function
import admin
import ts3
import config
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

url = config.influx_db['url']
token = config.influx_db['token']
org = config.influx_db['org']
bucket = config.influx_db['bucket']

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

send_to_influx = client.write_api(write_options=SYNCHRONOUS)



modelsdb.Base.metadata.create_all(bind=engine)


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = config.jwt['SECRET_KEY']
ALGORITHM = config.jwt['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = config.jwt['ACCESS_TOKEN_EXPIRE_MINUTES'] # zmień to potem bo zapomnisz !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



app = FastAPI()
app.include_router(public.router)
app.include_router(admin.router)
app.include_router(login.router)
app.include_router(bans.router)
origins = [
    "*"
]
unauthorized_operation_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="UNAUTHORIZED OPERATION",
        )
fake_users_db = {
    "johndoe": {
        "username": "a@wp.pl",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_password(plain_password, hashed_password):

    return pwd_context.verify(plain_password, hashed_password)




def get_password_hash(password):

    return pwd_context.hash(password)



def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


############################################
def verify_token(db,DBID,token):
    data=crud.get_user_temp_token(db,DBID)
    if not data:
        return False
    if not data.token==token:
        return False
    else:
        return True


############################################
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVSUQiOiJ1a…TgxfQ.a4RoENxA_EMFHrIqri0tc83TwtekAs9QXQhVVZ72FAQ
#    print (user.password)

def authenticate_user(fake_db, username: str, password: str):

    user = get_user(fake_db, username)

    if not user:

        return False

    if not verify_password(password, user.hashed_password):

        return False

    return user






async def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(username=email)
    except JWTError:
        raise credentials_exception
    user2=crud.get_user_by_email(db,email)
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_auth_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user=crud.get_user_by_email(db,email)
    if user is None:
        raise credentials_exception
    return user




async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/group_name/",response_model=schemas.name_rank)
async def get_name_rank(id: int = 0, user: schemas.current_user=Depends(function.decode_auth_token), db: Session = Depends(get_db)):
    if user[2]=='Staff':
        data=schemas.name_rank
        data.name=webDeamon.get_group_name(id)
        return data
    return

uvicorn.run(app, host="0.0.0.0", port=7798)
#uvicorn.run(app)
#uvicorn.run(app,host="0.0.0.0", port=8000)
#<21:15:35> "inż. Kanister10l": E87538
#<21:15:41> "inż. Kanister10l": A3871F
#<21:15:42> "inż. Kanister10l": 273033
#<21:15:45> "inż. Kanister10l": 294952
#2c3e50