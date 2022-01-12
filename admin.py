from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
import crud, modelsdb, schemas
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
    prefix="/staff",
    tags=["staff"],
    responses={404: {"description": "Not found"}},
)


# #########################################################################   SHOW STAFF LIST
@router.get("/staff_list/", response_model=List[schemas.List_Staff])
async def get_staff(user: schemas.current_user = Depends(function.decode_auth_token),
                    db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "acces_to_staff_user"):
        staff_list = crud.get_user_staff(db)
        return staff_list
    else:
        raise credentials_exception
    return


# ######################################################################### SHOW STAFF RANK ###########################
@router.get("/staff_rank/", response_model=List[schemas.staff_rank_base_append])
async def rank_staff(user: schemas.current_user = Depends(function.decode_auth_token),
                     db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "acces_to_grant_rank"):
        return crud.get_staff_rank(db)
    else:
        raise credentials_exception
    return


# ######################################################################### ADD/MODIFY STAFF RANK #####################
@router.put("/staff_rank/")
async def rank_staff_put(data: schemas.staff_rank_base_append,
                         user: schemas.current_user = Depends(function.decode_auth_token),
                         db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "acces_to_grant_rank"):
        crud.update_staff_rank(db, data)
        return
    else:
        raise credentials_exception
    return


########################################################################## ADD NEW STAFF USER #########################
@router.put("/add_staff_user/")
async def add_staf_rank(dbid: schemas.dbid, user: schemas.current_user = Depends(function.decode_auth_token),
                        db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "acces_to_staff_user"):
        crud.set_role_staff(db, dbid.dbid, "Staff")
        return
    else:
        raise credentials_exception
    return


########################################################################## SHOW USER LIST #############################
@router.get("/user_list/", response_model=List[schemas.List_Staff])
async def get_staff(user: schemas.current_user = Depends(function.decode_auth_token),
                    db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "acces_to_staff_user"):
        staff_list = crud.get_user_register(db)
        return staff_list
    else:
        raise credentials_exception
    return


# ######################################################################### UPDATE/DELETE ACCES TO RANK ###############
@router.put("/privilage_to_rank/", response_model=List[schemas.List_Staff])
async def privilege_to_rank_put(data: schemas.set_privilage,
                                user: schemas.current_user = Depends(function.decode_auth_token),
                                db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "acces_to_staff_user"):
        crud.set_role_to_staf(db, data.dbid, data.rank_id)
        return
    else:
        raise credentials_exception
    return


@router.delete("/privilage_to_rank/", response_model=List[schemas.List_Staff])
async def privilege_to_rank(data: schemas.set_privilage,
                            user: schemas.current_user = Depends(function.decode_auth_token),
                            db: Session = Depends(function.get_db)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "acces_to_staff_user"):
        crud.delete_role_to_staf(db, data.dbid)
        return
    else:
        raise credentials_exception
    return


# ######################################################################### UPDATE/DELETE RANK REGISTER ###############
@router.delete("/rank/rank_register")
async def rank_gender(rank: schemas.rank_ts3_append, db: Session = Depends(function.get_db),
                      user: schemas.current_user = Depends(function.decode_auth_token)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "acces_to_grant_rank"):
        if rank.type == 'rank_gender':
            DB_NAME = modelsdb.register_rank_gender
            table_name = 'register_rank_gender'
        elif rank.type == 'rank_province':
            DB_NAME = modelsdb.register_rank_province
            table_name = 'register_rank_province'
        else:
            return
        crud.delete_rank_list(db, DB_NAME, rank.id, table_name)
        return
    else:
        raise credentials_exception


@router.put("/rank/rank_register")
async def rank_gender(rank: schemas.rank_ts3_append, db: Session = Depends(function.get_db),
                      user: schemas.current_user = Depends(function.decode_auth_token)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "acces_to_grant_rank"):
        if rank.type == 'rank_gender':
            DB_NAME = modelsdb.register_rank_gender
        elif rank.type == 'rank_province':
            DB_NAME = modelsdb.register_rank_province
        else:
            return
        if rank.id == 0:
            data = schemas.rank_ts3_basic(rank_name=rank.rank_name, group_id=rank.group_id, path=rank.path)
            crud.add_rank_list(db, DB_NAME, data)
        else:
            data = schemas.rank_ts3_basic(rank_name=rank.rank_name, group_id=rank.group_id, path=rank.path)
            crud.update_rank_list(db, DB_NAME, data, rank.id)
            return
    else:
        raise credentials_exception


# #########################################################################  RANK GAME ################################
# user: schemas.current_user = Depends(function.decode_auth_token)

@router.put("/rank_game/")
async def put_rank_game(rank: schemas.RankGames, db: Session = Depends(function.get_db),
                        user: schemas.current_user = Depends(function.decode_auth_token)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "access_to_game_rank"):
        crud.update_rank_games(db, rank)
    else:
        raise credentials_exception


@router.delete("/rank_game/")
async def delete_rank_game(rank: schemas.RankGames, db: Session = Depends(function.get_db),
                           user: schemas.current_user = Depends(function.decode_auth_token)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "access_to_game_rank"):
        crud.delete_rank_games(db, rank)
    else:
        raise credentials_exception


@router.put("/rank_game_group_list/")
async def put_rank_game_group(rank: schemas.RankGamesList, db: Session = Depends(function.get_db),
                              user: schemas.current_user = Depends(function.decode_auth_token)):
    if not user[2] == "Staff":
        raise credentials_exception
    if crud.check_staff_grants(db, user[1], "access_to_game_rank"):
        crud.update_list_rank_games(db, rank)
    else:
        raise credentials_exception


@router.delete("/rank_game_group_list/")
async def delete_rank_game(rank: schemas.RankGamesList, db: Session = Depends(function.get_db),
                           user: schemas.current_user = Depends(function.decode_auth_token)):
    if not user[2] == "Staff":
        raise credentials_exception
    # TODO grants
    if crud.check_staff_grants(db, user[1], "access_to_game_rank"):
        crud.delete_list_rank_games(db, rank)
    else:
        raise credentials_exception


# recive message payload
@router.put("/message/")
async def put_message(message: schemas.Message, db: Session = Depends(function.get_db),
                      user: schemas.current_user = Depends(function.decode_auth_token)):
    if not user[2] == "Staff":
        raise credentials_exception
    #TODO grants
    try:
        message.date_auto_pub = time.mktime(datetime.strptime(message.date_auto_pub, "%Y-%m-%d").timetuple())
    except:
        message.date_auto_pub = -1
    try:
        message.date_auto_arch = time.mktime(datetime.strptime(message.date_auto_arch, "%Y-%m-%d").timetuple())
    except:
        message.date_auto_arch = -1
    crud.put_message(db, message, user[1])
    return


#get id message non arch
@router.get("/get_ids_message_non_arch/")
async def get_all_message(db: Session = Depends(function.get_db),
                      user: schemas.current_user = Depends(function.decode_auth_token)):
    if not user[2] == "Staff":
        raise credentials_exception
    response = []
    query = crud.get_ids_message_non_arch(db)
    for element in query:
        response.append(element.id)
    return response


@router.get("/get_all_user_list/")
async def get_all_user_list(db: Session = Depends(function.get_db),
                            user: schemas.current_user = Depends(function.decode_auth_token)):
    # TODO permissions
    if not user[2] == "Staff":
        raise credentials_exception
    inte = 0
    list_online = crud.return_list_online_dbid(db)
    join_table_data = crud.return_join_table_to_list_users(db)
    data = schemas.UserList(users=[])
    user = schemas.UserDataToTable(DBID=0, Nick='', UID='', Last_ip='', Last_login=0, Status='', IsOnline=False)
    for element in join_table_data:
        if str(element.base_users_on_teamsepak.DBID) in list_online:
            user.IsOnline = True
        inte = inte + 1
        user.DBID = element.base_users_on_teamsepak.DBID
        user.UID = element.base_users_on_teamsepak.UID
        user.Last_login = element.base_users_info_on_teamsepak.last_connect
        user.Nick = element.base_users_on_teamsepak.Nick
        user.Last_ip = element.base_users_on_teamsepak.IP
        data.users.append(user)
        user = schemas.UserDataToTable(DBID=0, Nick='', UID='', Last_ip='', Last_login=0, Status='', IsOnline=False)
    print(inte)
    return data


@router.get("/get_user_info_dash_board_base_/{dbid}")
async def get_user_info_dash_board_base(dbid: int, db: Session = Depends(function.get_db),
                                        user: schemas.current_user = Depends(function.decode_auth_token)):
    # TODO permissions
    if not user[2] == "Staff":
        raise credentials_exception
    return crud.get_user_data_by_DBID(db, dbid)


@router.get("/get_user_info_dash_board_base_info/{dbid}")
async def get_user_info_dash_board_base_info(dbid: int, db: Session = Depends(function.get_db),
                                             user: schemas.current_user = Depends(function.decode_auth_token)):
    # TODO permissions
    if not user[2] == "Staff":
        raise credentials_exception
    return crud.get_base_users_info_on_teamsepak(db, dbid)


@router.get("/get_user_info_dash_board_base_misc/{dbid}")
async def get_user_info_dash_board_base_misc(dbid: int, db: Session = Depends(function.get_db),
                                             user: schemas.current_user = Depends(function.decode_auth_token)):
    # TODO permissions
    if not user[2] == "Staff":
        raise credentials_exception
    return crud.get_base_users_misc_on_teamsepak(db, dbid)


@router.get("/get_user_info_timing/{dbid}")
async def get_user_info_dash_board_base_misc(dbid: int, db: Session = Depends(function.get_db),
                                             user: schemas.current_user = Depends(function.decode_auth_token)):
    # TODO permissions
    if not user[2] == "Staff":
        raise credentials_exception
    return crud.get_user_timing(db, dbid)


@router.get("/get_user_history_last_5_nick/{dbid}")
async def get_user_info_dash_board_base_misc(dbid: int, db: Session = Depends(function.get_db),
                                             user: schemas.current_user = Depends(function.decode_auth_token)):
    # TODO permissions and status
    if not user[2] == "Staff":
        raise credentials_exception
    data = schemas.UserList(users=[])
    user = schemas.DataToLastHistoryNick(nick='', status='nie działa', date_change=0)
    records = crud.return_list_history_last_5_nick(db, dbid)
    for element in records:
        user.nick = element.Nick
        user.date_change = element.time
        data.users.append(user)
        user = schemas.DataToLastHistoryNick(nick='', status='nie działa', date_change=0)
    return data.users

@router.get("/get_user_history_last_5_ip/{dbid}")
async def get_user_info_dash_board_base_misc(dbid: int, db: Session = Depends(function.get_db),
                                             user: schemas.current_user = Depends(function.decode_auth_token)):
    # TODO permissions and status
    if not user[2] == "Staff":
        raise credentials_exception
    data = schemas.UserList(users=[])
    user = schemas.DataToLastHistoryIp(ip='', status='Ok', date_change=0)
    records = crud.return_list_history_last_5_ip(db, dbid)
    for element in records:
        user.ip = element.CheckedIP.ip
        user.date_change = element.IpHistory.time
        if element.CheckedIP.proxy == 'yes':
            user.status = 'PROXY'
        data.users.append(user)
        user = schemas.DataToLastHistoryIp(ip='', status='ok', date_change=0)
    return data.users
