from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
import os
from sqlalchemy.orm import Session
import crud, modelsdb, schemas
from fastapi.responses import FileResponse
from database import *
import function
import requests
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import config
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
query_api = client.query_api()
SECRET_KEY = config.jwt['SECRET_KEY']
ALGORITHM = config.jwt['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = config.jwt['ACCESS_TOKEN_EXPIRE_MINUTES']

router = APIRouter(
    prefix="/public",
    tags=["pub"],
    responses={404: {"description": "Not found"}},
)
path = "icons"


########################################################################## REGISTER ##########################################################################
@router.post("/register")
async def create_user(user: schemas.User_Create_Incomong, db: Session = Depends(function.get_db)):
    db_user = crud.get_user_by_login(db, login=user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    db_user = None
    db_user = crud.get_user_by_dbid(db, dbid=user.dbid)
    if db_user:
        raise HTTPException(status_code=400, detail="DBID already registered")
    data=crud.get_user_temp_token(db,user.dbid)
    if not data:
        raise HTTPException(status_code=400, detail="Token was'n created")
    if not data.token == user.token:
        raise HTTPException(status_code=400, detail="Token is invalid")
    else:
        crud.create_register_user(db=db, user=user)
        #TODO token delete
    return {"Status": "succes"}
########################################################################## LOGIN ##########################################################################
@router.post("/login")
async def login_for_token(userlogin: schemas.UserLogin,db: Session = Depends(function.get_db)):
    user=function.auth(db,userlogin.login, userlogin.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    user = crud.get_user_by_login(db, userlogin.login)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = function.create_access_token(
     data={"UID": user.uid,"DBID": user.dbid,"Role":user.role}, expires_delta=access_token_expires)
    crud.update_last_login(db,userlogin.login)
    return {"token": access_token, "token_type": "bearer"}
########################################################################## GET ICON ##########################################################################
@router.get("/icon/{icon_id}")
async def icon(icon_id:str):
    file_path = path+"/"+icon_id
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error" : "File not found!"}
########################################################################## GET IP ##########################################################################
@router.get("/get_ip")
def read_root(request: Request):
    client_host = request.client.host
    print(request.headers.get('X-Forwarded-For'))
    return {"client_host": request.headers.get('X-Forwarded-For')}

# ######################################################################### GET IP ##########################################################################

@router.get("/rank_games_list/{group_name}")
async def get_rank_games_list(group_name: str, db: Session = Depends(function.get_db),
                              user: schemas.current_user = Depends(function.decode_auth_token)):
    return crud.get_list_rank_games_by_group_name(db, group_name)

@router.get("/rank_game_group_list/")
async def get_rank_game_group_list(db: Session = Depends(function.get_db),
                                   user: schemas.current_user = Depends(function.decode_auth_token)):
    return crud.get_list_rank_games_name(db)

# ######################################################################### GET LAST PING PACK LOSS PING ##############

@router.get("/last_stats/")
async def get_last_stats():
    result = schemas.CurrentServerHealthInfo(ping=0, current_user=0, pack_loss=0)
    query = 'from(bucket:"ts_3")\
    |> range(start: -5m)\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_ping")\
    |>last()\
    |> yield(name: "last")'
    tables = query_api.query(org=org, query=query)
    result.ping = query_api.query(org=org, query=query)[0].records[0].values["_value"]
    query = 'from(bucket:"ts_3")\
    |> range(start: -5m)\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_packet_loss")\
    |>last()\
    |> yield(name: "last")'
    result.pack_loss = query_api.query(org=org, query=query)[0].records[0].values["_value"]
    query = 'from(bucket:"ts_3")\
    |> range(start: -5m)\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_user_online")\
    |>last()\
    |> yield(name: "last")'
    result.current_user = query_api.query(org=org, query=query)[0].records[0].values["_value"]
    return result

# ######################################################################### GET FOR CHARTS PING PACK LOSS PING #########
@router.get("/stats/")
async def get_stats():
    result = schemas.ServerHealthInfo(pack_loss=[],current_user=[],ping=[])
    pack_loss = []
    current_user = []
    ping = []
    query = 'from(bucket: "ts_3")\
    |> range(start: -1d, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_packet_loss")\
    |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    pack_loss.append(float(format(query_api.query(org=org, query=query)[0].records[0].values["_value"], '.2f')))
    query = 'from(bucket: "ts_3")\
    |> range(start: -12h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_packet_loss")\
    |> aggregateWindow(every: 12h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    pack_loss.append(float(format(query_api.query(org=org, query=query)[0].records[0].values["_value"], '.2f')))
    query = 'from(bucket: "ts_3")\
    |> range(start: -5h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_packet_loss")\
    |> aggregateWindow(every: 5h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    pack_loss.append(float(format(query_api.query(org=org, query=query)[0].records[0].values["_value"], '.2f')))
    query = 'from(bucket: "ts_3")\
    |> range(start: -2h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_packet_loss")\
    |> aggregateWindow(every: 2h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    pack_loss.append(float(format(query_api.query(org=org, query=query)[0].records[0].values["_value"], '.2f')))
    query = 'from(bucket: "ts_3")\
    |> range(start: -1h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_packet_loss")\
    |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    pack_loss.append(float(format(query_api.query(org=org, query=query)[0].records[0].values["_value"], '.2f')))
    query = 'from(bucket: "ts_3")\
    |> range(start: -30m, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_packet_loss")\
    |> aggregateWindow(every: 30m, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    pack_loss.append(float(format(query_api.query(org=org, query=query)[0].records[0].values["_value"], '.2f')))
    query = 'from(bucket: "ts_3")\
    |> range(start: -10m, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_packet_loss")\
    |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    pack_loss.append(float(format(query_api.query(org=org, query=query)[0].records[0].values["_value"], '.2f')))
    query = 'from(bucket: "ts_3")\
    |> range(start: -10s, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_packet_loss")\
    |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    pack_loss.append(float(format(query_api.query(org=org, query=query)[0].records[0].values["_value"], '.2f')))

    # ####### ping
    query = 'from(bucket: "ts_3")\
    |> range(start: -1d, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_ping")\
    |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    ping.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -12h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_ping")\
    |> aggregateWindow(every: 12h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    ping.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -5h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_ping")\
    |> aggregateWindow(every: 5h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    ping.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -2h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_ping")\
    |> aggregateWindow(every: 2h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    ping.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -1h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_ping")\
    |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    ping.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -30m, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_ping")\
    |> aggregateWindow(every: 30m, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    ping.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -10m, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_ping")\
    |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    ping.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -10s, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_ping")\
    |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    ping.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))




    # current user
    query = 'from(bucket: "ts_3")\
    |> range(start: -1d, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_user_online")\
    |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    current_user.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -12h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_user_online")\
    |> aggregateWindow(every: 12h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    current_user.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -5h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_user_online")\
    |> aggregateWindow(every: 5h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    current_user.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -2h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_user_online")\
    |> aggregateWindow(every: 2h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    current_user.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -1h, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_user_online")\
    |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    current_user.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -30m, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_user_online")\
    |> aggregateWindow(every: 30m, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    current_user.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -10m, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_user_online")\
    |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    current_user.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))
    query = 'from(bucket: "ts_3")\
    |> range(start: -10s, stop: now())\
    |> filter(fn: (r) => r["_measurement"] == "online_on_ts")\
    |> filter(fn: (r) => r["_field"] == "current_user_online")\
    |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)\
    |> first()\
    |> yield(name: "mean")'
    current_user.append(int(round(query_api.query(org=org, query=query)[0].records[0].values["_value"])))

    result.pack_loss = pack_loss
    result.ping = ping
    result.current_user = current_user
    return result

@router.get("/rank_user/")
async def get_rank_user(db: Session = Depends(function.get_db)):
    return crud.get_user_rank(db)


@router.get("/list_user_search/")
async def get_list_user_search(db: Session = Depends(function.get_db)):
    data = schemas.UserList(users=[])
    user = schemas.UserDataForSearch(DBID=0, Nick='')
    result = crud.get_user_for_search_all(db)
    list_user = []
    for element in result:
        url = 'https://avatars.dicebear.com/api/male/' + element.Nick + '.svg'
        #response = requests.get(url)
        user.DBID = element.DBID
        user.Nick = element.Nick
        data.users.append(user)
        user = schemas.UserDataForSearch(DBID=0, Nick='')
    return data
