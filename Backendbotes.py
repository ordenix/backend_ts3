import re
from datetime import datetime, timedelta
from typing import Optional
import time
from typing import List
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
import json
import bans
from pydantic import BaseModel
import random
import string
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
import login
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
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


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
@app.get("/data")
async def data(current_user: schemas.User = Depends(get_auth_user)):
    return {"message": "Hello World","hu": current_user.email}

@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]



############################################### Na czsto############################
@app.get("/isonline", response_model=List[schemas.UserInfo])
def read_is_online(request: Request, db: Session = Depends(get_db)):
    ip = request.headers.get('X-Forwarded-For')
    #ip='51.83.179.240'
    return webDeamon.now_list_on_line(ip)
# @app.get("/set_temp_token/{DBID}")
# def create_temp_token(DBID: str, db: Session = Depends(get_db)):
#     data=crud.get_user_temp_token(db, DBID)
#     letters = string.ascii_letters
#     temp_token=( ''.join(random.choice(letters) for i in range(10)) )
#     credentials=schemas.Temp_Token(DBID=DBID,token=temp_token)
#     if data:
#         crud.update_user_temp_token(db,credentials)
#     else:
#         crud.create_user_temp_token(db,credentials)
#     webDeamon.send_token_to_user(DBID,temp_token)
#     return
@app.post("/register/nonaccount/")
def login_for_token(data: schemas.Temp_Token, db: Session = Depends(get_db)):
    if verify_token(db, data.DBID, data.token):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        userdata = crud.get_user_data_by_DBID(db, data.DBID)
        ##############################################################################################ROLE HERE DEFINED  staff(only user who can acces to staff panel) guest(non register user) register (register user in panel with offline account)
        access_token = function.create_access_token(
            data={"UID": userdata.UID, "DBID": data.DBID, "Role": "Guest"}, expires_delta=access_token_expires)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect auth token")
    #atoken="e"
    #UID,DBID,Role=decode_auth_token(atoken)
    return {"token": access_token, "token_type": "bearer"}
@app.get("/get_siedbar/account/",response_model=List[schemas.navMenu])
async def get_siedbar(current_user: schemas.current_user = Depends(function.decode_auth_token), db: Session = Depends(get_db)):
    dbid = int(current_user[1])
    user_data = crud.get_user_rank_on_ts(db, dbid)
    nav_elements = []
    register_not = {
              "icon": 'fa-user-tag',
              "route_link_name": 'userregisterrank',
              "name": 'Rejestracja',
              "status": 'fa-exclamation',
              "color_status": ''
            }
    register = {
              "icon": 'fa-user-tag',
              "route_link_name": 'userregisterrank',
              "name": 'Rejestracja',
              "status": 'fa-check',
              "color_status": ''
            }
    rank_game = {
                "icon": 'fa-tachometer-alt',
                "route_link_name": 'gamerank',
                "name": 'Rangi Gier',
                "status": '',
                "color_status": ''
            }
    if current_user[2] == 'Staff':

        navElements= [
            {
              "icon": 'fa-user-tag',
              "route_link_name": 'userregisterrank',
              "name": 'Rejestracja',
              "status": 'fa-times',
              "color_status": ''
            },
            {
              "icon": 'fa-tachometer-alt',
              "route_link_name": 'gamerank',
              "name": 'Rangi Gier',
              "status": '',
              "color_status": ''
            },
          ]
    elif current_user[2] == 'Guest':
        if not user_data.is_register:
            nav_elements.append(register_not)
        else:
            nav_elements.append(register)
            nav_elements.append(rank_game)
        return nav_elements
    elif current_user[2] == 'Register':
        if not user_data.is_register:
            nav_elements.append(register_not)
        else:
            nav_elements.append(register)
            nav_elements.append(rank_game)
        return nav_elements
    else:
        navElements=[];
    return navElements
@app.get("/get_siedbar/server/",response_model=List[schemas.navMenu])
async def get_siedbar(user: schemas.current_user=Depends(function.decode_auth_token),db: Session = Depends(get_db)):
    navElements= []
    if user[2]=='Staff':

        register={
              "icon": 'fa-user-tag',
              "route_link_name": 'manageregisterrank',
              "name": '[Rejestracja]',
              "status": 'fa-cogs',
              "color_status": ''
            }
        gamerank={
              "icon": 'fa-dice',
              "route_link_name": 'rankgameslist',
              "name": '[Rangi Gier]',
              "status": 'fa-cogs',
              "color_status": ''
            }
        rank_staff={
              "icon": 'fa-code-branch',
              "route_link_name": 'managestaffform',
              "name": '[Rangi ADM]',
              "status": 'fa-cogs',
              "color_status": ''
            }
        user_staff={
              "icon": 'fa-user-tie',
              "route_link_name": 'stafflist',
              "name": '[Administratorzy]',
              "status": 'fa-toolbox',
              "color_status": ''
            }
        user_list={
              "icon": 'fas fa-users',
              "route_link_name": 'UserList',
              "name": '[Użytkownicy]',
              "status": 'fa-toolbox',
              "color_status": ''
            }
        if crud.check_staff_grants(db,user[1],"acces_to_register"):
            navElements.append(register)
        if crud.check_staff_grants(db, user[1], "access_to_game_rank"):
            navElements.append(gamerank)
        if crud.check_staff_grants(db,user[1],"acces_to_grant_rank"):
            navElements.append(rank_staff)
        if crud.check_staff_grants(db,user[1],"acces_to_staff_user"):
            navElements.append(user_staff)
        # TODO permissions
        navElements.append(user_list)

    else:
        navElements=[];
    return navElements
@app.get("/rank/")
async def read_item(type: str = 'none', action: str = 'none', id: int = 0, rank_name: str= 'none', group_id: int = 0, path: str = 'none', db: Session = Depends(get_db),current_use: schemas.current_user=Depends(function.decode_auth_token)):
    #akcje get add remove modify
    if type=='rank_gender':
        DB_NAME=modelsdb.register_rank_gender
    elif type=='rank_province':
        DB_NAME=modelsdb.register_rank_province
    else:
        return
    data=crud.get_rank_list(db, DB_NAME)
    return data


@app.get("/group_name/",response_model=schemas.name_rank)
async def get_name_rank(id: int = 0, user: schemas.current_user=Depends(function.decode_auth_token), db: Session = Depends(get_db)):
    if user[2]=='Staff':
        data=schemas.name_rank
        data.name=webDeamon.get_group_name(id)
        return data
    return
@app.post("/get_DBID_by_uid/")
async def get(data: schemas.uid,db: Session = Depends(get_db)):

    DBID =int(webDeamon.get_DBID_by_UID(data.uid))
    data=crud.get_user_temp_token(db, DBID)
    letters = string.ascii_letters
    temp_token=( ''.join(random.choice(letters) for i in range(10)) )
    credentials=schemas.Temp_Token(DBID=DBID,token=temp_token)
    if data:
        crud.update_user_temp_token(db,credentials)
    else:
        crud.create_user_temp_token(db,credentials)
    webDeamon.send_token_to_user(DBID,temp_token)
    return {"DBID": DBID }
@app.get("/status_rule_user/")
async def get_status(db: Session = Depends(get_db), user: schemas.current_user = Depends(function.decode_auth_token)):
    #od 1 dbid
    data = schemas.staus_rules(connect=False, time=False, ban=False, rules=False, status_register=False)
    CRR_minimum_connect = int(crud.return_settings(db, "CRR_minimum_connect"))
    CRR_minimum_time_online = int(crud.return_settings(db, "CRR_minimum_time_online"))
    CRR_minimum_connect_ratio = int(crud.return_settings(db, "CRR_minimum_connect_ratio"))
    DBID = int(user[1])
    user_data = crud.get_user_rank_on_ts(db, DBID)
    with ts3.query.TS3Connection(config.query_ts3['host'], 10011) as ts3conn:
        ts3conn.login(client_login_name=config.query_ts3['login'], client_login_password=config.query_ts3['pass'])
        ts3conn.use(sid=1)
        try:
            ts3conn.clientupdate(client_nickname="Sauron TS3|WEB")
        except:
            pass
        rank_list = function.return_current_rank_list(ts3conn, DBID, db)
    register_on_ts = False
    for rank in rank_list:
        if crud.return_rank_by_id(db, modelsdb.register_rank_gender, rank):
            register_on_ts = True
    if register_on_ts and not user_data.is_register:
        crud.accept_rules_and_register(db, DBID)
        data.status_register = True
        data.connect = True
        data.time = True
        data.ban = True
        data.rules = True
        return data

    if user_data.is_register:
        data.status_register = True
        data.connect = True
        data.time = True
        data.ban = True
        data.rules = True
        return data
    data_user = crud.get_user_data_by_DBID(db, DBID)
    if data_user:
        data.connect = True
    else:
        return data
    timing = crud.get_user_timing(db, DBID)
    try:
        if timing.TIME_ONLINE < CRR_minimum_time_online:
            return data
        total_afk_time = timing.TIME_AWAY+timing.TIME_MIC_DISABLED+timing.TIME_IDLE
        ratio = total_afk_time/timing.TIME_TOTAL
        CRR_minimum_connect_ratio = 1-(CRR_minimum_connect_ratio*0.01)
        real_connection = crud.get_base_users_info_on_teamsepak(db, DBID).real_total_connections
        if ratio > CRR_minimum_connect_ratio:
            return data
        else:
            if real_connection > CRR_minimum_connect:
                data.time = True
            else:
                return data
        current_time = int(time.time())
        ban_history = crud.get_ban_last_history_by_user_dbid(db, DBID, current_time - (int(crud.return_settings(db, "CRR_hour_no_ban")) * 3600))
        if len(ban_history) == 0:
            data.ban = True

        if user_data.check_rules == True:
            data.rules = True
    except: pass
    return data
##################################################################################### PRZXELICZ NA NOWO PUTA!
@app.put("/register_user_on_ts3/")
async def register_user_on_ts3(data: schemas.register_user_form, db: Session = Depends(get_db), user: schemas.current_user = Depends(function.decode_auth_token)):
    CRR_minimum_connect = int(crud.return_settings(db, "CRR_minimum_connect"))
    CRR_minimum_time_online = int(crud.return_settings(db, "CRR_minimum_time_online"))
    CRR_minimum_connect_ratio = int(crud.return_settings(db, "CRR_minimum_connect_ratio"))
    DBID = int(user[1])

    with ts3.query.TS3Connection("PASSWORD", 10011) as ts3conn:
        ts3conn.login(client_login_name="BOT_WEB", client_login_password="PASSWORD")
        ts3conn.use(sid=1)
        try:
            ts3conn.clientupdate(client_nickname="Sauron TS3|WEB")
        except:
            pass
        user_data = crud.get_user_rank_on_ts(db, DBID)
        if user_data.is_register == False:
            data_user = crud.get_user_data_by_DBID(db, DBID)
            if not data_user:
                raise unauthorized_operation_exception
            timing = crud.get_user_timing(db, DBID)
            if timing.TIME_ONLINE < CRR_minimum_time_online:
                raise unauthorized_operation_exception
            total_afk_time = timing.TIME_AWAY + timing.TIME_MIC_DISABLED + timing.TIME_IDLE
            ratio = total_afk_time / timing.TIME_TOTAL
            CRR_minimum_connect_ratio = 1 - (CRR_minimum_connect_ratio * 0.01)
            real_connection = crud.get_base_users_info_on_teamsepak(db, DBID).real_total_connections

            current_time = int(time.time())
            ban_history = crud.get_ban_last_history_by_user_dbid(db, DBID, current_time - (
                        int(crud.return_settings(db, "CRR_hour_no_ban")) * 3600))
            if not len(ban_history) == 0:
                raise unauthorized_operation_exception
            if ratio > CRR_minimum_connect_ratio:
                raise unauthorized_operation_exception
            else:
                if not real_connection > CRR_minimum_connect:
                    raise unauthorized_operation_exception

        # TODO ban rules set
        # SECURITY TEST IS RANK EXIST ANT CORRECTLY
        rank_gender = crud.return_rank_by_id(db, modelsdb.register_rank_gender, data.gender_id)
        rank_province = crud.return_rank_by_id(db, modelsdb.register_rank_province, data.province_id)
        if rank_gender and rank_province:
            crud.accept_rules_and_register(db, DBID)
            rank_list = function.return_current_rank_list(ts3conn, DBID, db)
            for i in rank_list:
                if crud.return_rank_by_id(db, modelsdb.register_rank_gender, int(i)) or crud.return_rank_by_id(db, modelsdb.register_rank_province, int(i)):
                    webDeamon.delete_rank(ts3conn, int(i), DBID)
                    crud.update_rank_in_db(db, DBID, int(i), "DELETE")

            webDeamon.add_rank(ts3conn, int(data.gender_id),  DBID)
            webDeamon.add_rank(ts3conn, int(data.province_id), DBID)
            crud.update_rank_in_db(db, DBID, data.gender_id, "ADD")
            crud.update_rank_in_db(db, DBID, data.province_id, "ADD")

        else:
            raise unauthorized_operation_exception
    #client_server_group_on_ts3=

    return


uvicorn.run(app, host="0.0.0.0", port=7798)
#uvicorn.run(app)
#uvicorn.run(app,host="0.0.0.0", port=8000)
#<21:15:35> "inż. Kanister10l": E87538
#<21:15:41> "inż. Kanister10l": A3871F
#<21:15:42> "inż. Kanister10l": 273033
#<21:15:45> "inż. Kanister10l": 294952
#2c3e50