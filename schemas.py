from typing import List, Optional, Dict, Optional, Tuple

from pydantic import BaseModel




class User(BaseModel):
    login: str
    password: str
    uid: str
    dbid: int


class User_Create_Incomong(User):
    token: str


class User_Create_extendent(User):
    date_created: int


class UserLogin(BaseModel):
    login: str
    password: str


class UserInfo(BaseModel):
    DBID: int
    IP: str
    UID: str
    Nick: str
    class Config:
        orm_mode = True
#class UserInfo_List(BaseModel):
#    __root__: List[UserInfo] 
class Temp_Token(BaseModel):
    DBID: int
    token: str
    class Config:
        orm_mode = True


class current_user(BaseModel):
    DBID: int
    UID: str
    Role: str


class navMenu(BaseModel):
    icon: str
    route_link_name: str
    name: str
    status: str
    color_status: str


class rank_ts3_basic(BaseModel):
    rank_name: str
    group_id: int
    path: str


class rank_ts3_append(rank_ts3_basic):
    id: int
    type: str


class staff_rank_base(BaseModel):
    id: int
    rank_name: str
    rank_id: int
    class Config:
        orm_mode = True


class staff_rank_base_append(staff_rank_base):
    group_id: int
    acces_to_register: bool
    acces_to_grant_rank: bool
    acces_to_staff_user: bool
    class Config:
        orm_mode = True

   
class name_rank(BaseModel):
    name: str
    class Config:
        orm_mode = True


class privilage_to_rank(BaseModel):
    rank_id: int
    rank_name: str
    class Config:
        orm_mode = True


class List_Staff(BaseModel):
    login: str
    dbid: int
    last_login: int
    privilages : List[privilage_to_rank] =[]
    class Config:
        orm_mode = True


class uid(BaseModel):
    uid: str
    class Config:
        orm_mode = True


class dbid(BaseModel):
    dbid: int
    class Config:
        orm_mode = True


class set_privilage(BaseModel):
    dbid: int
    rank_id: int
    class Conig:
        orm_mode = True


class staus_rules(BaseModel):
    connect: bool
    time: bool
    ban: bool
    rules: bool
    status_register: bool

    class Config:
        orm_mode = True


class register_user_form(BaseModel):
    gender_id: int
    province_id: int


class RankGames(BaseModel):
    id: int
    rank_name: str
    group_id: int
    path: str
    group_name: str
    sort_id: int


class RankGamesList(BaseModel):
    id: int
    group_name: str
    sort_id: int


class CurrentServerHealthInfo(BaseModel):
    ping: float
    current_user: int
    pack_loss: float


class ServerHealthInfo(BaseModel):
    ping: List = []
    current_user: List = []
    pack_loss: List = []


class UserDataForSearch(BaseModel):
    DBID: int
    Nick: str


class UserList(BaseModel):
    users: List = []


class UserDataToTable(BaseModel):
    Nick: str
    UID: str
    DBID: int
    Last_ip: str
    Last_login: int
    Status: str
    IsOnline: bool


class Message(BaseModel):
    date_auto_arch: str
    date_auto_pub: str
    selected_staff: List = []
    selected_user: List = []
    selected_type: str
    searchUser: dict
    message: str
    title: str
    priority: int
    readable: bool
    id: int

    class Config:
        orm_mode = True


class MessageId(BaseModel):
    message_id: int


class DataToLastHistoryNick(BaseModel):
    nick: str
    date_change: int
    status: str


class DataToLastHistoryIp(BaseModel):
    ip: str
    date_change: int
    status: str


class PayloadActionBanType(BaseModel):
    id: int
    name: str
    group_id: int
    action: str
    time: bool


class SettingsToBanModule(BaseModel):
    active: bool
    auto_ban: bool
    two_factor: bool

    class Config:
        orm_mode = True


class BanPermissions(BaseModel):
    id: int
    rank_grant_id: int
    action_ban_id: int
    max_time_to_action: int
    two_factor_auth: bool
    add: bool
    limit_per_10m: int
    limit_per_1d: int
    overflow: bool
    commit: bool
    commit_auto: bool
    delete: bool


class BanTableData(BaseModel):
    id: int
    name: str
    description: str
    skip_grant: bool
    active: bool


class BanTimesData(BaseModel):
    id: int
    action_id: int
    ban_id: int
    times_from: int
    times_from_setting: str
    times_to: int
    times_to_setting: str
    time_from: int
    time_from_setting: str
    time_to: int
    time_to_setting: str
    points: int


class BanHistoryData(BaseModel):
    id: int
    ban_client_dbid: int
    ban_id: int
    action_id: int
    additional_info: str
    add_admin_dbid: int
    time_add: int
    time_to: int
    active: bool
    time_to_overflow: int
    to_commit: bool
    commit: bool
    commit_admin_dbid: int
    time_commit: int
    auto_ban: bool
    removed: bool
    removed_dbid: int
    time_removed: int


class BanTimeParameterToAdd(BaseModel):
    time_from: int
    time_from_setting: str
    time_to: int
    time_to_setting: str
    times_this: int
    times_all: int
    action_name: str
    action_id: int
    timing: bool
    ignore_ban: bool


class BanTimeParameterToCalculateAdd(BaseModel):
    dbid: int
    ban_id: int


class DataActionPermissions(BaseModel):
    action_id: int


class DataToAddBan(BaseModel):
    ban_client_dbid: int
    ban_id: int
    action_id: int
    additional_info: str
    time: int


class Login(BaseModel):
    login: str


class RecoverPasswordToken(BaseModel):
    token: str
    password: str
    login: str
