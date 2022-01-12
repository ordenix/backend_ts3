from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
import crud
import ts3
import modelsdb
import schemas
from database import *
import function
import config
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List
import time

SECRET_KEY = config.jwt['SECRET_KEY']
ALGORITHM = config.jwt['ALGORITHM']

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

router = APIRouter(
    prefix="/bans",
    tags=["bans"],
    responses={404: {"description": "Not found"}},
)


@router.put("/put_data_ban_action_type/")
async def put_data_ban_action_type(data: schemas.PayloadActionBanType,
                                   user: schemas.current_user = Depends(function.decode_auth_token),
                                   db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    crud.put_data_ban_action_type(db, data)
    return


@router.delete("/delete_ban_action_type/")
async def delete_ban_action_type(data: schemas.PayloadActionBanType,
                                 user: schemas.current_user = Depends(function.decode_auth_token),
                                 db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    crud.delete_ban_action_type(db, data)
    return


@router.get("/get_ban_action_type/")
async def get_ban_action_type(user: schemas.current_user = Depends(function.decode_auth_token),
                              db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    return crud.get_ban_action_type(db)


@router.get("/get_current_settings/", response_model=schemas.SettingsToBanModule)
async def get_current_settings(user: schemas.current_user = Depends(function.decode_auth_token),
                               db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    response = schemas.SettingsToBanModule(active=False, auto_ban=False, two_factor=False)
    active = crud.return_module_settings(db, 'ban_active')
    auto_ban = crud.return_module_settings(db, 'ban_auto_ban')
    two_factor = crud.return_module_settings(db, 'ban_two_factor')
    if active is None:
        crud.update_settings(db, 'ban_active', False)
    else:
        response.active = active.status
    if auto_ban is None:
        crud.update_settings(db, 'ban_auto_ban', False)
    else:
        response.auto_ban = auto_ban.status
    if two_factor is None:
        crud.update_settings(db, 'ban_two_factor', False)
    else:
        response.two_factor = two_factor.status
    return response


@router.put("/update_settings/")
async def update_settings(data: schemas.SettingsToBanModule,
                          user: schemas.current_user = Depends(function.decode_auth_token),
                          db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    crud.update_settings(db, 'ban_active', data.active)
    crud.update_settings(db, 'ban_auto_ban', data.auto_ban)
    crud.update_settings(db, 'ban_two_factor', data.two_factor)
    return


@router.put("/update_permissions/")
async def update_permissions(data: schemas.BanPermissions,
                             user: schemas.current_user = Depends(function.decode_auth_token),
                             db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    crud.update_ban_permissions(db, data)
    return

@router.get("/get_permissions/{rank_id}")
async def get_permissions(rank_id: int,
                          user: schemas.current_user = Depends(function.decode_auth_token),
                          db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    table_permissions_data = crud.get_ban_permissions(db)
    ban_actions = crud.get_ban_action_type(db)
    grant_ranks = crud.get_staff_rank(db)
    # remove old
    if table_permissions_data:
        table_data_full = crud.get_ban_permissions_simple(db)
        for element in table_data_full:
            status_find = False
            for element_table_permissions in table_permissions_data:
                if element.rank_grant_id == element_table_permissions.grant_rank.rank_id and element.action_ban_id == element_table_permissions.ActionBanType.id:
                    status_find = True
            if not status_find:
                crud.delete_ban_permissions(db, element)
        # adding new items
        for element_grant_ranks in grant_ranks:
            for element_ban in ban_actions:
                status_find = False
                data = schemas.BanPermissions(id=0, rank_grant_id=element_grant_ranks.rank_id,
                                              action_ban_id=element_ban.id, max_time_to_action=-1,
                                              two_factor_auth=False, add=False, limit_per_10m=0,  limit_per_1d=0,
                                              overflow=False, commit=False, commit_auto=False, delete=False)

                for element_table_permissions in table_permissions_data:
                    if element_table_permissions.grant_rank.rank_id == element_grant_ranks.rank_id and element_table_permissions.ActionBanType.id == element_ban.id:
                        status_find = True
                        break
                if not status_find:
                    crud.update_ban_permissions(db, data)
    else:
        for element_grant_ranks in grant_ranks:
            for element_ban in ban_actions:
                data = schemas.BanPermissions(id=0, rank_grant_id=element_grant_ranks.rank_id,
                                              action_ban_id=element_ban.id, max_time_to_action=-1,
                                              two_factor_auth=False, add=False, limit_per_10m=0, overflow=False,
                                              limit_per_1d=0, commit=False, commit_auto=False, delete=False)
                crud.update_ban_permissions(db, data)
    return crud.get_ban_permissions_by_group_rank_id(db, rank_id)


@router.get("/get_ban_table/")
async def get_ban_table(user: schemas.current_user = Depends(function.decode_auth_token),
                        db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    return crud.get_ban_table(db)


@router.put("/put_ban_table/")
async def put_ban_table(data: schemas.BanTableData,
                        user: schemas.current_user = Depends(function.decode_auth_token),
                        db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    crud.update_ban_table(db, data)
    return


@router.delete("/delete_ban_table/")
async def delete_ban_table(data: schemas.BanTableData,
                           user: schemas.current_user = Depends(function.decode_auth_token),
                           db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    crud.delete_ban_table(db, data)
    return


@router.get("/get_ban_times_by_ban_id/{ban_id}")
async def get_ban_times_by_ban_id(ban_id: int,
                                  user: schemas.current_user = Depends(function.decode_auth_token),
                                  db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    return crud.get_ban_times_by_ban_id(db, ban_id)


@router.put("/put_ban_times_by_ban_id/")
async def put_ban_times_by_ban_id(data: schemas.BanTimesData,
                                  user: schemas.current_user = Depends(function.decode_auth_token),
                                  db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    crud.update_ban_times(db, data)
    return


@router.delete("/delete_ban_times_by_ban_id/")
async def delete_ban_times_by_ban_id(data: schemas.BanTimesData,
                                     user: schemas.current_user = Depends(function.decode_auth_token),
                                     db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    crud.delete_ban_times(db, data)
    return


@router.get("/get_ban_history/")
async def get_ban_history(
                                  db: Session = Depends(function.get_db)):
    return crud.get_ban_history(db)


@router.put("/get_ban_add_parameters_to_add/")
async def put_ban_add_parameters_to_add(data: schemas.BanTimeParameterToCalculateAdd,
                                        user: schemas.current_user = Depends(function.decode_auth_token),
                                        db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    response = schemas.BanTimeParameterToAdd(time_from=0, time_to=0, times_this=0, times_all=0, action_name='',
                                             action_id=0, time_from_setting='', time_to_setting='', timing=False,
                                             ignore_ban=False)
    response.times_all = len(crud.get_ban_history_by_user_dbid(db, data.dbid))
    response.times_this = len(crud.get_ban_history_by_user_dbid_ban_id(db, data.dbid, data.ban_id))
    ban_action_times_table = crud.get_ban_times_by_ban_id(db, data.ban_id)
    response.ignore_ban = False
    if data.dbid == 2:
        response.ignore_ban = True
    # TODO SKIP parameters rank
    if ban_action_times_table:
        for element in ban_action_times_table:
            if element.times_from <= response.times_this and (element.times_to >= response.times_this):
                response.action_id = element.action_id
                response.time_from = element.time_from
                response.time_from_setting = element.time_from_setting
                response.time_to = element.time_to
                response.time_to_setting = element.time_to_setting
            if element.times_from <= response.times_this and (element.times_to == -1):
                response.action_id = element.action_id
                response.time_from = element.time_from
                response.time_from_setting = element.time_from_setting
                response.time_to = element.time_to
                response.time_to_setting = element.time_to_setting
        response.action_name = crud.get_ban_action_type_by_id(db, response.action_id).name
        response.timing = crud.get_ban_action_type_by_id(db, response.action_id).time
    return response


@router.put("/get_action_permission/")
async def get_action_permission(data: schemas.DataActionPermissions,
                                user: schemas.current_user = Depends(function.decode_auth_token),
                                db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    return crud.get_ban_permissions_by_grant_rank_by_action_id(db, crud.check_role_to_staff(db, user[1]).rank_id, data.action_id)


@router.put("/add_ban/")
async def add_ban(data: schemas.DataToAddBan,
                  user: schemas.current_user = Depends(function.decode_auth_token),
                  db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    reached_day_limit = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Reached day limit"
    )
    reached_10m_limit = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Reached 10m limit"
    )
    overflow = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Overflow error"
    )
    user_is_admin = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="You can't add ban to admin"
    )
    user_have_ignore_ban = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User have ignore ban"
    )
    user_is_offline = HTTPException(
        status_code=status.HTTP_200_OK,
        detail="User is offline"
    )
    offline_user = False
    current_time = int(time.time())
    action = crud.get_ban_action_type_by_id(db, data.action_id)
    creator_data = crud.get_user_data_by_DBID(db, user[1])
    ban_ts3_time = 0
    ban_user_data = crud.get_user_data_by_DBID(db, data.ban_client_dbid)
    ban_permission = crud.get_ban_permissions_by_grant_rank_by_action_id(db,
                                                                         crud.check_role_to_staff(db, user[1]).rank_id,
                                                                         data.action_id)
    ban = schemas.BanHistoryData(id=0, ban_client_dbid=0, ban_id=0, action_id=0, additional_info='',
                                 add_admin_dbid=0, time_add=0, time_to=0, active=False, time_to_overflow=0,
                                 to_commit=False, commit=False, commit_admin_dbid=0, time_commit=0, auto_ban=False,
                                 removed=False, removed_dbid=0, time_removed=0)
    history_creator = crud.get_ban_history_by_creator_id_and_action_id(db, user[1], data.action_id)
    times_per_10m = 0
    times_per_1d = 0
    for element in history_creator:
        if element.BanHistoryTable.time_add >= (current_time-600):
            times_per_10m += 1
        if element.BanHistoryTable.time_add >= (current_time-86400):
            times_per_1d += 1
    if ban_permission.limit_per_10m < times_per_10m and not ban_permission.limit_per_10m == -1:
        raise reached_10m_limit
    if ban_permission.limit_per_1d < times_per_1d and not ban_permission.limit_per_1d == -1:
        raise reached_day_limit

    ban.ban_client_dbid = data.ban_client_dbid
    ban.ban_id = data.ban_id
    ban.action_id = data.action_id
    ban.additional_info = data.additional_info
    ban.add_admin_dbid = user[1]
    ban.time_add = current_time
    if data.time == 0:
        ban.time_to = 0
        ban.removed = True
        ban.active = False
    elif data.time == -1:
        if not ban_permission.max_time_to_action == -1:
            if ban_permission.overflow:
                ban.time_to = current_time + (ban_permission.max_time_to_action * 60)
                ban_ts3_time = ban_permission.max_time_to_action * 60
                ban.to_commit = True
                ban.active = True
                ban.time_to_overflow = -1
            else:
                raise overflow
        else:
            ban.time_to = -1
    else:
        if data.time > ban_permission.max_time_to_action and not ban_permission.max_time_to_action == -1:
            if ban_permission.overflow:
                ban.time_to = current_time + (ban_permission.max_time_to_action * 60)
                ban_ts3_time = ban_permission.max_time_to_action * 60
                ban.to_commit = True
                ban.active = True
                ban.time_to_overflow = (data.time - ban_permission.max_time_to_action) * 60
            else:
                raise overflow
        else:
            ban.time_to = current_time + (data.time * 60)
            ban_ts3_time = data.time * 60
            ban.active = True

    with ts3.query.TS3Connection(config.query_ts3['host'], 10011) as ts3conn:
        ts3conn.login(client_login_name=config.query_ts3['login'], client_login_password=config.query_ts3['pass'])
        ts3conn.use(sid=1)
        try:
            ts3conn.clientupdate(client_nickname="Sauron TS3|Boska ręka")
        except:
            pass
        try:
            user_info = ts3conn.clientdbinfo(cldbid=data.ban_client_dbid)
            clid = ts3conn.clientgetids(cluid=user_info[0]['client_unique_identifier'])
            clid = clid[0]['clid']


            client_info = ts3conn.clientinfo(clid=clid)
            list_server_group = list(client_info[0]['client_servergroups'].split(","))
            for group in list_server_group:
                if int(group) == 109:
                    raise user_is_admin
                # TODO user is admin ths only for dev and test
                group_info = ts3conn.servergrouppermlist(sgid=int(group), permsid=True)
                for permission in group_info:
                    if permission['permsid'] == 'b_client_ignore_bans' and permission['permvalue'] == '1':
                        print('ss')
                        # TODO ignore bans and ignorebans above (send to frontend)
                        raise user_have_ignore_ban
            # non raise
            try:
                ban_description = crud.get_ban_by_id(db, data.ban_id).description
                msg = "[b]Drogi/a:  [COLOR=#ff0000][U]" + client_info[0]['client_nickname']
                ts3conn.sendtextmessage(targetmode=1, target=clid, msg="[B]-------------- UWAGA!! --------------")
                ts3conn.sendtextmessage(targetmode=1, target=clid, msg=msg)
                msg = "[B]" + ban_description
                ts3conn.sendtextmessage(targetmode=1, target=clid, msg=msg)
                msg = "[B]Twoja kara to:  [color=green]" + action.name
                ts3conn.sendtextmessage(targetmode=1, target=clid, msg=msg)
                if not (action.action == 'kick_channel' or action.action == 'kick_server'):
                    human_date = datetime.utcfromtimestamp(current_time + data.time * 60).strftime('%Y-%m-%d %H:%M:%S') + "[/color] czasu UTC"
                    msg = "[B]Kara będzie trwać do:  [color=green]" + human_date
                    ts3conn.sendtextmessage(targetmode=1, target=clid, msg=msg)
                msg = "[B]Administrator nakładający karę to: [color=#FF8000]" + creator_data.Nick
                ts3conn.sendtextmessage(targetmode=1, target=clid, msg=msg)
                msg = "[B]Aby odwołać się skorzystaj z supportu otavi.pl i powołaj się na id kary: " + str(len(crud.get_ban_history(db))+1)
                ts3conn.sendtextmessage(targetmode=1, target=clid, msg=msg)
            except:
                pass
            # execute ban
            if action.action == 'kick_channel':
                try:
                    reasonmsg = crud.get_ban_by_id(db, data.ban_id).name + " || id: " + str(len(crud.get_ban_history(db))+1)
                    ts3conn.clientkick(reasonid=4, reasonmsg=reasonmsg, clid=clid)
                except:
                    pass
            if action.action == 'kick_server':
                try:
                    reasonmsg = crud.get_ban_by_id(db, data.ban_id).name + " || id: " + str(len(crud.get_ban_history(db)) + 1)
                    ts3conn.clientkick(reasonid=5, reasonmsg=reasonmsg, clid=clid)
                except:
                    pass
        except:
            offline_user = True
        if ban.active:
            if action.action == 'add_server_group':
                try:
                    ts3conn.servergroupaddclient(sgid=action.group_id, cldbid=ban.ban_client_dbid)
                except:
                    pass
            if action.action == 'ban':
                try:
                    ts3conn.banadd(uid=ban_user_data.UID, banreason=crud.get_ban_by_id(db, data.ban_id).name,
                                   time=ban_ts3_time)
                except:
                    pass
    crud.update_ban_history_table(db, ban)
    if offline_user:
        raise user_is_offline
    return


@router.get("/get_ban_history/{dbid}")
async def add_ban(dbid: int,
                  user: schemas.current_user = Depends(function.decode_auth_token),
                  db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    return crud.get_ban_history_by_user_dbid(db, dbid)





     # active=None, time_to_overflow=None
     # to_commit=None, commit=None, commit_admin_dbid=None, time_commit=None,
      # removed=None, removed_dbid=None, time_removed=None)