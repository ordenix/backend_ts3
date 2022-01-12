import bcrypt
import crud
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, FastAPI, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
import crud, modelsdb, schemas
from database import *
import config
import webDeamon
SECRET_KEY = config.jwt['SECRET_KEY']
ALGORITHM = config.jwt['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = config.jwt['ACCESS_TOKEN_EXPIRE_MINUTES']

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)
def auth(db, login, password):
    user = crud.get_user_by_login(db, login)
    if not user:
        return False
    return check_password(password.encode('utf-8'),user.password.encode('utf-8'))
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_auth_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        UID: str = payload.get("UID")
        DBID: int = payload.get("DBID")
        Role: str = payload.get("Role") 
        if UID is None:
            raise credentials_exception
        if DBID is None:
            raise credentials_exception
        if Role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return UID, DBID, Role


def return_current_rank_list(ts3conn, dbid: int, db: Session):
# here !
    user_info = webDeamon.online_info_user(ts3conn, dbid)
    if user_info:
        rank_list = list(user_info[0]['client_servergroups'].split(","))
    else:
        user_data = crud.get_user_rank_on_ts(db, dbid)
        rank_list = list(user_data.server_groups.split(","))
    return rank_list


def current_limit_rank_games(ts3conn, dbid: int, db: Session = Depends(get_db)):
    user_info = webDeamon.online_info_user(ts3conn, dbid)
    if user_info:
        rank_list = list(user_info[0]['client_servergroups'].split(","))
    else:
        user_data = crud.get_user_rank_on_ts(db, dbid)
        rank_list = list(user_data.server_groups.split(","))
    limits_rank = crud.get_limits(db)
    current_limit = 0
    for i in limits_rank:
        for x in rank_list:
            if i.rank_id == int(x) and current_limit == 0:
                current_limit = i.limit_register_rank
    return current_limit


def verify_token(db, dbid, token):
    data = crud.get_user_temp_token(db, dbid)
    if not data:
        return False
    if not data.token == token:
        return False
    else:
        return True

