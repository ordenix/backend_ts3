from datetime import datetime, timedelta
import time
from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased
from sqlalchemy import desc, asc
import modelsdb, schemas
import hashlib
import os
import function


#def get_list_user_by_ip(db:Session, IP: str):
 #   print("!!!!!!!!!!!!!!!!!!!!!!!!!")
 #   return db.query(modelsdb.to_login_online_users_on_teamsepak).filter(modelsdb.to_login_online_users_on_teamsepak.IP == IP).all()
def get_user_data_by_DBID(db: Session, DBID: str):
    return db.query(modelsdb.base_users_on_teamsepak).filter(modelsdb.base_users_on_teamsepak.DBID == DBID).first()


def create_user_temp_token (db: Session, data: schemas.Temp_Token):
    db_data = modelsdb.temp_autch_token(DBID=data.DBID, token=data.token)
    db.add(db_data)
    db.commit()
def get_user_temp_token(db: Session, DBID: str):
    return db.query(modelsdb.temp_autch_token).filter(modelsdb.temp_autch_token.DBID == DBID).first()
def update_user_temp_token(db: Session, data: schemas.Temp_Token):
    data_db = db.query(modelsdb.temp_autch_token).filter(modelsdb.temp_autch_token.DBID==data.DBID).first()
    data_db.token=data.token
    db.commit()
    ##################################################################RANG_REGISTER##
def get_rank_list(db: Session, DB_NAME):
    return db.query(DB_NAME).all()
def add_rank_list(db: Session, DB_NAME, data: schemas.rank_ts3_basic):
    db_data = DB_NAME(rank_name=data.rank_name,group_id=data.group_id,path=data.path)
    db.add(db_data)
    db.commit()
def delete_rank_list(db: Session, DB_NAME, id,table_name):
    data_db = db.query(DB_NAME).filter(DB_NAME.id==id).first()
    if not data_db:
        return
    db.delete(data_db)
    db.commit()
    querry=("ALTER TABLE "+table_name+ " DROP id")
    db.execute(querry)
    querry=("ALTER TABLE "+table_name+" AUTO_INCREMENT=0")
    db.execute(querry)
    querry=("ALTER TABLE "+table_name+" ADD id int UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST")
    db.execute(querry)
    db.commit()
#def upadte_online_timing_disabled_users(db: Session, DBID):
 #   user = db.query(modelsdb.time_users_on_teamsepak).filter(modelsdb.time_users_on_teamsepak.DBID==DBID).first()
  #  user.TIME_MIC_DISABLED +=1
   # db.commit()
def update_rank_list(db: Session, DB_NAME, data: schemas.rank_ts3_basic,id):
    record = db.query(DB_NAME).filter(DB_NAME.id==id).first()
    if data:
        record.rank_name = data.rank_name
        record.group_id = data. group_id
        record.path = data.path
        db.commit()
def get_staff_rank(db: Session):
    return db.query(modelsdb.grant_rank).all()
def update_staff_rank(db: Session, data:schemas.staff_rank_base_append):
    if data.id == 0:
        table=get_staff_rank(db)
        if len(table) == 0:
            key=1
        else:
            last=db.query(modelsdb.grant_rank).filter(modelsdb.grant_rank.id==len(table)).first()
            key=last.id+1


        db_data=modelsdb.grant_rank(rank_name = data.rank_name, group_id = data.group_id, acces_to_register = data.acces_to_register, acces_to_grant_rank = data.acces_to_grant_rank,acces_to_staff_user = data.acces_to_staff_user,rank_id=key)
        db.add(db_data)
        db.commit()
    else:
        record = db.query(modelsdb.grant_rank).filter(modelsdb.grant_rank.id==data.id).first()
        if data:
            record.rank_name = data.rank_name
            record.group_id = data. group_id
            record.acces_to_register = data.acces_to_register
            record.acces_to_grant_rank = data.acces_to_grant_rank
            record.acces_to_staff_user = data.acces_to_staff_user
            db.commit()
    return


def get_staff_rank_by_id(db: Session, rank_id: int):
    return db.query(modelsdb.grant_rank).filter(modelsdb.grant_rank.rank_id == rank_id).first()

def delete_staff_rank(db: Session, rank_id):
    data_db = db.query(modelsdb.grant_rank).filter(modelsdb.grant_rank.rank_id==rank_id).first()
    if not data_db:
        return
    db.delete(data_db)
    db.commit()
    return


def create_register_user(db: Session, user: schemas.User_Create_extendent):
    timenow=int(time.time())
    exist_user= db.query(modelsdb.User_register).all()
    encoded_password=function.hash_password(user.password.encode('utf-8')) 

    # if user not exist create staff acount leater add more func.
    if exist_user:
        db_user = modelsdb.User_register(login=user.login, password=encoded_password, uid=user.uid, dbid=user.dbid, role="Register",date_created=timenow,last_login=0)
    else:
        db_user = modelsdb.User_register(login=user.login, password=encoded_password, uid=user.uid, dbid=user.dbid, role="Staff",date_created=timenow,last_login=0)    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return
def get_user_by_dbid(db: Session, dbid: int):
    return db.query(modelsdb.User_register).filter(modelsdb.User_register.dbid == dbid).first()
def get_user_by_login(db: Session, login: str):
    return db.query(modelsdb.User_register).filter(modelsdb.User_register.login == login).first()
def update_last_login(db: Session,login):
    record = db.query(modelsdb.User_register).filter(modelsdb.User_register.login==login).first()
    record.last_login=int(time.time())
    db.commit()
def get_user_staff(db: Session):
    #return db.query(modelsdb.User_register, modelsdb.privilage_to_rank).join(modelsdb.privilage_to_rank,  modelsdb.User_register).filter(modelsdb.User_register.role == "Staff").all()
    return db.query(modelsdb.User_register).filter(modelsdb.User_register.role == "Staff").all()
def get_user_register(db: Session):
    #return db.query(modelsdb.User_register, modelsdb.privilage_to_rank).join(modelsdb.privilage_to_rank,  modelsdb.User_register).filter(modelsdb.User_register.role == "Staff").all()
    return db.query(modelsdb.User_register).filter(modelsdb.User_register.role == "Register").all()

def check_staff_grants(db: Session, dbid, grant_name):
    privilige_to_rank=db.query(modelsdb.privilage_to_rank).filter(modelsdb.privilage_to_rank.DBID == dbid).first()
    if not privilige_to_rank:
        return False
    grant_rank=db.query(modelsdb.grant_rank).filter(modelsdb.grant_rank.rank_id == privilige_to_rank.rank_id).first()
    if grant_name == "acces_to_register":
        if grant_rank.acces_to_register == True:
            return True
        else: return False
    if grant_name == "acces_to_grant_rank":
        if grant_rank.acces_to_grant_rank == True:
            return True
        else: return False
    if grant_name == "acces_to_staff_user":
        if grant_rank.acces_to_staff_user == True:
            return True
        else: return False
    if grant_name == "access_to_game_rank":
        if grant_rank.access_to_game_rank:
            return True
        else: return False
   
    return False
def set_role_staff(db: Session,dbid,role):
    user=db.query(modelsdb.User_register).filter(modelsdb.User_register.dbid==dbid).first()
    if not user:
        return
    user.role=role
    db.commit()
def set_role_to_staf(db: Session,dbid,rank_id):
    relation=db.query(modelsdb.privilage_to_rank).filter(modelsdb.privilage_to_rank.DBID==dbid).first()
    if relation:
        relation.rank_id=rank_id
        db.commit()
    else:
        relation=modelsdb.privilage_to_rank(DBID=dbid,rank_id=rank_id)
        db.add(relation)
        db.commit()
        db.refresh(relation)
def delete_role_to_staf(db: Session, dbid):
    data_db = db.query(modelsdb.privilage_to_rank).filter(modelsdb.privilage_to_rank.DBID==dbid).first()
    if not data_db:
        return
    db.delete(data_db)
    db.commit()
    return


def check_role_to_staff(db: Session, dbid: int):
    return db.query(modelsdb.privilage_to_rank).filter(modelsdb.privilage_to_rank.DBID == dbid).first()


def delete_user(db: Session, rank_id):
    data_db = db.query(modelsdb.User_register).filter(modelsdb.User_register.dbid==rank_id).first()
    if not data_db:
        return
    db.delete(data_db)
    db.commit()
    return

def return_settings(db: Session, setting: str):
    querry = db.query(modelsdb.modules_settings).filter(modelsdb.modules_settings.setting==setting).first()
    if not querry:
        return None
    return querry.options


def return_module_settings(db: Session, module_name: str):
    record = db.query(modelsdb.ActiveModules).filter(modelsdb.ActiveModules.module_name == module_name).first()
    if not record:
        return None
    return record


def update_settings(db: Session, module_name: str, parameters: bool):
    record = db.query(modelsdb.ActiveModules).filter(modelsdb.ActiveModules.module_name == module_name).first()
    if record:
        record.status = parameters
    else:
        record = modelsdb.ActiveModules(module_name=module_name, status=parameters)
        db.add(record)
    db.commit()
    return

def get_user_timing(db: Session, DBID):
    return db.query(modelsdb.time_users_on_teamsepak).filter(modelsdb.time_users_on_teamsepak.DBID==DBID).first()
def return_rank_by_id(db: Session, DB_NAME, group_id):
    return db.query(DB_NAME).filter(DB_NAME.group_id==group_id).first()
def get_user_rank_on_ts(db: Session, DBID):
    return db.query(modelsdb.base_users_server_data_on_teamsepak).filter(modelsdb.base_users_server_data_on_teamsepak.DBID==DBID).first()
def update_rank_in_db(db: Session,DBID,rank_id,action):
    record = db.query(modelsdb.base_users_server_data_on_teamsepak).filter(modelsdb.base_users_server_data_on_teamsepak.DBID==DBID).first()
    if not record.server_groups == '':
        list_group = list(record.server_groups.split(","))
        if action=="DELETE":
            try:
                list_group.remove(str(rank_id))
            except: pass
    else:
        list_group = []
    if action=="ADD":
        list_group.append(str(rank_id))
    list_str=','.join(list_group)
    record.server_groups=list_str
    db.commit()


def accept_rules_and_register(db, dbid):
    record = db.query(modelsdb.base_users_server_data_on_teamsepak).\
        filter(modelsdb.base_users_server_data_on_teamsepak.DBID == dbid).first()
    record.check_rules = True
    record.is_register = True
    db.commit()


# get limits rank
def get_limits(db):
    query = db.query(modelsdb.rank_limit).order_by(modelsdb.rank_limit.limit_register_rank.desc()).all()
    return query


# get group rank games name list
def get_list_rank_games_name(db):
    return db.query(modelsdb.games_rank_table_list).order_by(modelsdb.games_rank_table_list.sort_id.asc()).all()


# get list rank games by group name
def get_list_rank_games_by_group_name(db, group_name):
    return db.query(modelsdb.game_rank).filter(modelsdb.game_rank.group_name == group_name).order_by(modelsdb.game_rank.sort_id.asc()).all()


def update_rank_games(db, rank: schemas.RankGames):
    record = db.query(modelsdb.game_rank).filter(modelsdb.game_rank.id == rank.id).first()
    if record:
        record.rank_name = rank.rank_name
        record.group_id = rank.group_id
        record.path = rank.path
        record.group_name = rank.group_name
        record.sort_id = rank.sort_id
    else:
        record = modelsdb.game_rank(rank_name=rank.rank_name, group_id=rank.group_id, path=rank.path,
                                    group_name=rank.group_name, sort_id=rank.sort_id)
        db.add(record)
    db.commit()


def update_list_rank_games(db, group: schemas.RankGamesList):
    record = db.query(modelsdb.games_rank_table_list).filter(modelsdb.games_rank_table_list.id == group.id).first()
    if record:
        record.group_name = group.group_name
        record.sort_id = group.sort_id
    else:
        record = modelsdb.games_rank_table_list(group_name=group.group_name, sort_id=group.sort_id)
        db.add(record)
    db.commit()


def delete_rank_games(db: Session, rank: schemas.RankGames):
    record = db.query(modelsdb.game_rank).filter(modelsdb.game_rank.id == rank.id).first()
    if not record:
        return
    db.delete(record)
    db.commit()
    return


def delete_list_rank_games(db: Session, group: schemas.RankGamesList):
    record = db.query(modelsdb.games_rank_table_list).filter(modelsdb.games_rank_table_list.id == group.id).first()
    if not record:
        return
    db.delete(record)
    db.commit()
    return


def return_all_rank_games(db: Session):
    return db.query(modelsdb.game_rank).all()


def get_base_users_info_on_teamsepak(db: Session, dbid: int):
    return db.query(modelsdb.base_users_info_on_teamsepak).filter(modelsdb.base_users_info_on_teamsepak.DBID == dbid).first()


def get_base_users_misc_on_teamsepak(db: Session, dbid: int):
    return db.query(modelsdb.base_users_misc_on_teamsepak).filter(modelsdb.base_users_misc_on_teamsepak.DBID == dbid).first()

# get user ranks
def get_user_rank(db: Session):
    return db.query(modelsdb.rank_limit).all()


#get list user for search
def get_user_for_search_all(db: Session):
    return db.query(modelsdb.base_users_on_teamsepak).order_by(modelsdb.base_users_on_teamsepak.Nick.asc()).all()


#put message
def put_message(db: Session, message: schemas.Message, author: int):
    record = db.query(modelsdb.message).filter(modelsdb.message.id == message.id).first()
    if record:
        record.message = message.message
        record.title = message.title
        record.priority = message.priority
        record.readable = message.readable
        record.date_auto_arch = message.date_auto_arch
        record.date_auto_pub = message.date_auto_pub
        if message.selected_type == 'all':
            record.to_all = True
            record.to_group_id = None
            record.to_id = None
            record.to_staff_rank = None
        elif message.selected_type == 'single':
            record.to_all = None
            record.to_group_id = None
            record.to_id = message.searchUser["DBID"]
            record.to_staff_rank = None
        elif message.selected_type == 'group':
            print("group")
    else:
        if message.selected_type == 'all':
            record = modelsdb.message(to_all=True, message=message.message, date=datetime.now().timestamp(),
                                      author=author, priority=message.priority, date_auto_arch=message.date_auto_arch,
                                      date_auto_pub=message.date_auto_pub, readable=message.readable, title=message.title)
        elif message.selected_type == 'single':
            record = modelsdb.message(to_id=message.searchUser["DBID"], message=message.message, date=datetime.now().timestamp(),
                                      author=author, priority=message.priority, date_auto_arch=message.date_auto_arch,
                                      date_auto_pub=message.date_auto_pub, readable=message.readable,
                                      title=message.title)
        elif message.selected_type == 'group':
            print("group")
        #TODO single group
        db.add(record)
    db.commit()
    return

def return_message_by_id(db: Session, message_id: int):
    return db.query(modelsdb.message).filter(modelsdb.message.id == message_id).first()


def get_ids_message_non_arch(db: Session):
    return db.query(modelsdb.message).filter(modelsdb.message.archive == False).all()


def return_user_list_on_teamspeak_base(db: Session):
    return db.query(modelsdb.base_users_on_teamsepak).all()
   # to_all = Column(Boolean, default=False)
    #to_group_id = Column(String(256))
    #to_id = Column(String(256))
    #to_staff_rank = Column(String(256))


def return_last_ip_list(db: Session):
    return db.query(modelsdb.IpHistory).order_by(modelsdb.IpHistory.id.desc()).all()


def return_last_nick_list(db: Session):
    return db.query(modelsdb.NickHistory).order_by(modelsdb.NickHistory.id.desc()).all()


def return_check_ip_list(db: Session):
    return db.query(modelsdb.CheckedIP).all()


def return_base_users_info_on_teamsepak(db: Session):
    return db.query(modelsdb.base_users_info_on_teamsepak).all()

def return_join_table_to_list_users(db: Session):
    return db.query(modelsdb.base_users_on_teamsepak, modelsdb.base_users_info_on_teamsepak).\
        select_from(modelsdb.base_users_on_teamsepak).\
        join(modelsdb.base_users_info_on_teamsepak, modelsdb.base_users_info_on_teamsepak.DBID==modelsdb.base_users_on_teamsepak.DBID).all()


def return_join_table_ip(db: Session):
    return db.query(modelsdb.IpHistory, modelsdb.CheckedIP).\
        select_from(modelsdb.IpHistory).\
        join(modelsdb.CheckedIP, modelsdb.CheckedIP.id == modelsdb.IpHistory.id_ip).\
        order_by(modelsdb.IpHistory.id.desc()).\
        all()


def return_list_online_dbid(db: Session):
    record = db.query(modelsdb.OnlineUserOnTs).first()
    return list(record.list.split(","))


def return_list_history_last_5_nick(db: Session, dbid: int):
    return db.query(modelsdb.NickHistory).filter(modelsdb.NickHistory.dbid == dbid).\
        order_by(modelsdb.NickHistory.id.desc()).limit(5).all()


def return_list_history_last_5_ip(db: Session, dbid: int):
    return db.query(modelsdb.IpHistory, modelsdb.CheckedIP).\
        select_from(modelsdb.IpHistory).\
        join(modelsdb.CheckedIP, modelsdb.CheckedIP.id == modelsdb.IpHistory.id_ip).\
        filter(modelsdb.IpHistory.dbid == dbid).\
        order_by(modelsdb.IpHistory.id.desc()).limit(5).all()


def put_data_ban_action_type(db: Session, data: modelsdb.ActionBanType):
    record = db.query(modelsdb.ActionBanType).filter(modelsdb.ActionBanType.id == data.id).first()
    if record:
        record.name = data.name
        record.group_id = data.group_id
        record.action = data.action
        record.time = data.time
        db.commit()
    else:
        record = modelsdb.ActionBanType(name=data.name, group_id=data.group_id, action=data.action, time=data.time)
        db.add(record)
        db.commit()


def get_ban_action_type(db: Session):
    return db.query(modelsdb.ActionBanType).all()


def get_ban_action_type_by_id(db: Session, id: int):
    return db.query(modelsdb.ActionBanType).filter(modelsdb.ActionBanType.id == id).first()

def delete_ban_action_type(db: Session, data: modelsdb.ActionBanType):
    record = db.query(modelsdb.ActionBanType).filter(modelsdb.ActionBanType.id==data.id).first()
    if not record:
        return
    db.delete(record)
    db.commit()
    return


def get_ban_permissions(db: Session):
    return db.query(modelsdb.BanPermission, modelsdb.grant_rank, modelsdb.ActionBanType).\
           select_from(modelsdb.BanPermission).\
           join(modelsdb.grant_rank, modelsdb.BanPermission.rank_grant_id == modelsdb.grant_rank.rank_id).\
           join(modelsdb.ActionBanType, modelsdb.BanPermission.action_ban_id == modelsdb.ActionBanType.id).\
           order_by(modelsdb.BanPermission.rank_grant_id.asc(), modelsdb.BanPermission.action_ban_id.asc()). all()


def get_ban_permissions_by_grant_rank_by_action_id(db: Session, rank_grant_id: int, action_ban_id: int):
    return db.query(modelsdb.BanPermission).filter(modelsdb.BanPermission.rank_grant_id == rank_grant_id).\
           filter(modelsdb.BanPermission.action_ban_id == action_ban_id).first()


def get_ban_permissions_by_group_rank_id(db: Session, id: int):
    return db.query(modelsdb.BanPermission, modelsdb.grant_rank, modelsdb.ActionBanType).\
           select_from(modelsdb.BanPermission).\
           join(modelsdb.grant_rank, modelsdb.BanPermission.rank_grant_id == modelsdb.grant_rank.rank_id).\
           join(modelsdb.ActionBanType, modelsdb.BanPermission.action_ban_id == modelsdb.ActionBanType.id).\
           order_by(modelsdb.BanPermission.rank_grant_id.asc(), modelsdb.BanPermission.action_ban_id.asc()).\
           where(modelsdb.BanPermission.rank_grant_id == id).all()

def get_ban_permissions_simple(db: Session):
    return db.query(modelsdb.BanPermission).all()


def update_ban_permissions(db: Session, data: schemas.BanPermissions):
    record = db.query(modelsdb.BanPermission).filter(modelsdb.BanPermission.id == data.id).first()
    if record:
        record.rank_grant_id = data.rank_grant_id
        record.action_ban_id = data.action_ban_id
        record.max_time_to_action = data.max_time_to_action
        record.two_factor_auth = data.two_factor_auth
        record.add = data.add
        record.limit_per_10m = data.limit_per_10m
        record.limit_per_1d = data.limit_per_1d
        record.overflow = data.overflow
        record.commit = data.commit
        record.commit_auto = data.commit_auto
        record.delete = data.delete
    else:
        record = modelsdb.BanPermission(rank_grant_id=data.rank_grant_id, action_ban_id=data.action_ban_id,
                                        max_time_to_action=data.max_time_to_action, two_factor_auth=data.two_factor_auth,
                                        add=data.add, limit_per_10m=data.limit_per_10m, limit_per_1d=data.limit_per_1d,
                                        overflow=data.overflow, commit=data.commit, commit_auto=data.commit_auto,
                                        delete=data.delete)
        db.add(record)
    db.commit()


def delete_ban_permissions(db: Session, data: schemas.BanPermissions):
    record = db.query(modelsdb.BanPermission).filter(modelsdb.BanPermission.id==data.id).first()
    if not record:
        return
    db.delete(record)
    db.commit()
    return


def get_ban_table(db: Session):
    return db.query(modelsdb.BanTable).all()


def get_ban_by_id(db: Session, id: int):
    return db.query(modelsdb.BanTable).filter(modelsdb.BanTable.id == id).first()

# def get_ban_table_by_id()
def update_ban_table(db: Session, data: schemas.BanTableData):
    record = db.query(modelsdb.BanTable).filter(modelsdb.BanTable.id == data.id).first()
    if record:
        record.name = data.name
        record.description = data.description
        record.skip_grant = data.skip_grant
        record.active = data.active
    else:
        record = modelsdb.BanTable(name=data.name, description=data.description, skip_grant=data.skip_grant,
                                   active=data.active)
        db.add(record)
    db.commit()
    return

def delete_ban_table(db: Session, data: schemas.BanTableData):
    record = db.query(modelsdb.BanTable).filter(modelsdb.BanTable.id == data.id).first()
    if not record:
        return
    db.delete(record)
    db.commit()
    return


def get_ban_times_by_ban_id(db: Session, ban_id: int):
    return db.query(modelsdb.BanTimes).filter(modelsdb.BanTimes.ban_id == ban_id).all()


def update_ban_times(db: Session, data: schemas.BanTimesData):
    record = db.query(modelsdb.BanTimes).filter(modelsdb.BanTimes.id == data.id).first()
    if record:
        record.action_id = data.action_id
        record.ban_id = data.ban_id
        record.times_from = data.times_from
        record.times_from_setting = data.times_from_setting
        record.times_to = data.times_to
        record.times_to_setting = data.times_to_setting
        record.time_from = data.time_from
        record.time_from_setting = data.time_from_setting
        record.time_to = data.time_to
        record.time_to_setting = data.time_to_setting
        record.points = data.points
    else:

        record = modelsdb.BanTimes(action_id=data.action_id, ban_id=data.ban_id, times_from=data.times_from,
                                   times_from_setting=data.times_from_setting, times_to_setting=data.times_to_setting,
                                   times_to=data.times_to, time_from=data.time_from, time_to=data.time_to,
                                   time_from_setting=data.time_from_setting, time_to_setting=data.time_to_setting,
                                   points=data.points)
        db.add(record)
    db.commit()
    return


def delete_ban_times(db: Session, data: schemas.BanTimesData):
    record = db.query(modelsdb.BanTimes).filter(modelsdb.BanTimes.id == data.id).first()
    if not record:
        return
    db.delete(record)
    db.commit()
    return


def get_ban_history(db: Session):
    ban_user = aliased(modelsdb.base_users_on_teamsepak, name="ban_user")
    add_admin = aliased(modelsdb.base_users_on_teamsepak, name="add_admin")
    commit_admin = aliased(modelsdb.base_users_on_teamsepak, name="commit_admin")
    removed_admin = aliased(modelsdb.base_users_on_teamsepak, name="removed_admin")
    return db.query(modelsdb.BanHistoryTable, ban_user, add_admin, commit_admin, removed_admin, modelsdb.BanTable, modelsdb.ActionBanType).\
        outerjoin(ban_user, modelsdb.BanHistoryTable.ban_client_dbid == ban_user.DBID).\
        outerjoin(add_admin, modelsdb.BanHistoryTable.add_admin_dbid == add_admin.DBID).\
        outerjoin(commit_admin, modelsdb.BanHistoryTable.commit_admin_dbid == commit_admin.DBID).\
        outerjoin(removed_admin, modelsdb.BanHistoryTable.removed_dbid == removed_admin.DBID). \
        outerjoin(modelsdb.BanTable, modelsdb.BanHistoryTable.ban_id == modelsdb.BanTable.id). \
        outerjoin(modelsdb.ActionBanType, modelsdb.BanHistoryTable.action_id == modelsdb.ActionBanType.id).all()


def get_ban_history_by_creator_id_and_action_id(db: Session, dbid: int, action_id: int):
    ban_user = aliased(modelsdb.base_users_on_teamsepak, name="ban_user")
    add_admin = aliased(modelsdb.base_users_on_teamsepak, name="add_admin")
    commit_admin = aliased(modelsdb.base_users_on_teamsepak, name="commit_admin")
    removed_admin = aliased(modelsdb.base_users_on_teamsepak, name="removed_admin")
    return db.query(modelsdb.BanHistoryTable, ban_user, add_admin, commit_admin, removed_admin, modelsdb.BanTable, modelsdb.ActionBanType).\
        outerjoin(ban_user, modelsdb.BanHistoryTable.ban_client_dbid == ban_user.DBID).\
        outerjoin(add_admin, modelsdb.BanHistoryTable.add_admin_dbid == add_admin.DBID).\
        outerjoin(commit_admin, modelsdb.BanHistoryTable.commit_admin_dbid == commit_admin.DBID).\
        outerjoin(removed_admin, modelsdb.BanHistoryTable.removed_dbid == removed_admin.DBID). \
        outerjoin(modelsdb.BanTable, modelsdb.BanHistoryTable.ban_id == modelsdb.BanTable.id). \
        filter(modelsdb.BanHistoryTable.add_admin_dbid == dbid). \
        filter(modelsdb.BanHistoryTable.action_id == action_id). \
        outerjoin(modelsdb.ActionBanType, modelsdb.BanHistoryTable.action_id == modelsdb.ActionBanType.id).all()

def get_ban_history_by_user_dbid(db: Session, user_dbid: int):
    ban_user = aliased(modelsdb.base_users_on_teamsepak, name="ban_user")
    add_admin = aliased(modelsdb.base_users_on_teamsepak, name="add_admin")
    commit_admin = aliased(modelsdb.base_users_on_teamsepak, name="commit_admin")
    removed_admin = aliased(modelsdb.base_users_on_teamsepak, name="removed_admin")
    return db.query(modelsdb.BanHistoryTable, ban_user, add_admin, commit_admin, removed_admin, modelsdb.BanTable, modelsdb.ActionBanType).\
        outerjoin(ban_user, modelsdb.BanHistoryTable.ban_client_dbid == ban_user.DBID).\
        outerjoin(add_admin, modelsdb.BanHistoryTable.add_admin_dbid == add_admin.DBID).\
        outerjoin(commit_admin, modelsdb.BanHistoryTable.commit_admin_dbid == commit_admin.DBID).\
        outerjoin(removed_admin, modelsdb.BanHistoryTable.removed_dbid == removed_admin.DBID). \
        outerjoin(modelsdb.BanTable, modelsdb.BanHistoryTable.ban_id == modelsdb.BanTable.id). \
        outerjoin(modelsdb.ActionBanType, modelsdb.BanHistoryTable.action_id == modelsdb.ActionBanType.id). \
        filter(modelsdb.BanHistoryTable.ban_client_dbid == user_dbid).all()


def get_ban_history_by_user_dbid_ban_id(db: Session, user_dbid: int, ban_id: int):
    ban_user = aliased(modelsdb.base_users_on_teamsepak, name="ban_user")
    add_admin = aliased(modelsdb.base_users_on_teamsepak, name="add_admin")
    commit_admin = aliased(modelsdb.base_users_on_teamsepak, name="commit_admin")
    removed_admin = aliased(modelsdb.base_users_on_teamsepak, name="removed_admin")
    return db.query(modelsdb.BanHistoryTable, ban_user, add_admin, commit_admin, removed_admin, modelsdb.BanTable, modelsdb.ActionBanType).\
        outerjoin(ban_user, modelsdb.BanHistoryTable.ban_client_dbid == ban_user.DBID).\
        outerjoin(add_admin, modelsdb.BanHistoryTable.add_admin_dbid == add_admin.DBID).\
        outerjoin(commit_admin, modelsdb.BanHistoryTable.commit_admin_dbid == commit_admin.DBID).\
        outerjoin(removed_admin, modelsdb.BanHistoryTable.removed_dbid == removed_admin.DBID). \
        outerjoin(modelsdb.BanTable, modelsdb.BanHistoryTable.ban_id == modelsdb.BanTable.id). \
        outerjoin(modelsdb.ActionBanType, modelsdb.BanHistoryTable.action_id == modelsdb.ActionBanType.id). \
        filter(modelsdb.BanHistoryTable.ban_client_dbid == user_dbid).filter(modelsdb.BanHistoryTable.ban_id == ban_id).all()


def update_ban_history_table(db: Session, data: schemas.BanHistoryData):
    record = db.query(modelsdb.BanHistoryTable).filter(modelsdb.BanHistoryTable.id == data.id).first()
    if record:
        record.id = data.id
        record.ban_client_dbid = data.ban_client_dbid
        record.ban_id = data.ban_id
        record.action_id = data.action_id
        record.additional_info = data.additional_info
        record.add_admin_dbid = data.add_admin_dbid
        record.time_add = data.time_add
        record.time_to = data.time_to
        record.active = data.active
        record.time_to_overflow = data.time_to_overflow
        record.to_commit = data.to_commit
        record.commit = data.commit
        record.commit_admin_dbid = data.commit_admin_dbid
        record.time_commit = data.time_commit
        record.auto_ban = data.auto_ban
        record.removed = data.removed
        record.removed_dbid = data.removed_dbid
        record.time_removed = data.time_removed

    else:
        record = modelsdb.BanHistoryTable(id=data.id, ban_client_dbid=data.ban_client_dbid, ban_id=data.ban_id,
                                          action_id=data.action_id, additional_info=data.additional_info,
                                          add_admin_dbid=data.add_admin_dbid, time_add=data.time_add,
                                          time_to=data.time_to, active=data.active,
                                          time_to_overflow=data.time_to_overflow, to_commit=data.to_commit,
                                          commit=data.commit, commit_admin_dbid=data.commit_admin_dbid,
                                          time_commit=data.time_commit, auto_ban=data.auto_ban, removed=data.removed,
                                          removed_dbid=data.removed_dbid, time_removed=data.time_removed)
        db.add(record)
    db.commit()
    return


def get_ban_last_history_by_user_dbid(db: Session, user_dbid: int, time: int):
    ban_user = aliased(modelsdb.base_users_on_teamsepak, name="ban_user")
    add_admin = aliased(modelsdb.base_users_on_teamsepak, name="add_admin")
    commit_admin = aliased(modelsdb.base_users_on_teamsepak, name="commit_admin")
    removed_admin = aliased(modelsdb.base_users_on_teamsepak, name="removed_admin")
    return db.query(modelsdb.BanHistoryTable, ban_user, add_admin, commit_admin, removed_admin, modelsdb.BanTable, modelsdb.ActionBanType).\
        outerjoin(ban_user, modelsdb.BanHistoryTable.ban_client_dbid == ban_user.DBID).\
        outerjoin(add_admin, modelsdb.BanHistoryTable.add_admin_dbid == add_admin.DBID).\
        outerjoin(commit_admin, modelsdb.BanHistoryTable.commit_admin_dbid == commit_admin.DBID).\
        outerjoin(removed_admin, modelsdb.BanHistoryTable.removed_dbid == removed_admin.DBID). \
        outerjoin(modelsdb.BanTable, modelsdb.BanHistoryTable.ban_id == modelsdb.BanTable.id). \
        outerjoin(modelsdb.ActionBanType, modelsdb.BanHistoryTable.action_id == modelsdb.ActionBanType.id). \
        filter(modelsdb.BanHistoryTable.ban_client_dbid == user_dbid).filter(modelsdb.BanHistoryTable.time_add >= time).all()


def get_user_from_user_register_by_login(db: Session, login: str):
    return db.query(modelsdb.User_register).filter(modelsdb.User_register.login == login).first()


def get_temp_token_data_by_token(db: Session, token: str):
    return db.query(modelsdb.temp_autch_token).filter(modelsdb.temp_autch_token.token == token).first()


def update_password(db: Session, dbid: int, password: str):
    record = db.query(modelsdb.User_register).filter(modelsdb.User_register.dbid == dbid).first()
    if record:
        record.password = password
        db.commit()


def delete_temp_token(db: Session, token: str):
    record = db.query(modelsdb.temp_autch_token).filter(modelsdb.temp_autch_token.token == token).first()
    if record:
        db.delete(record)
        db.commit()
