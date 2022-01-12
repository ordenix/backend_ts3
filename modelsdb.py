from sqlalchemy import *
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.orm import aliased


class User_register(Base):
    __tablename__ = "users_register"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(32))
    password = Column(String(64))
    is_banned = Column(Boolean, default=False)
    date_created = Column(Integer)
    last_login = Column(Integer)
    uid = Column(String(32), unique=True)
    dbid = Column(Integer,unique=True)
    role = Column(String(32))
    privilages = relationship("grant_rank", secondary="privilage_to_rank")


class online_users_on_teamsepak(Base):
    __tablename__ = "online_users_on_teamsepak"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, unique=True)
    UID = Column(String(32), unique=True)
    IP = Column(Text)
    Nick = Column(Text(convert_unicode=True))


class temp_autch_token(Base):
    __tablename__ = "temp_auth_token"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, unique=True)
    token = Column(String(32), unique=True)


class register_rank_gender(Base):
    __tablename__ = "register_rank_gender"
    id = Column(Integer, primary_key=True, index=True)
    rank_name = Column(String(32))
    group_id = Column(Integer)
    path = Column(String(32))


class register_rank_province(Base):
    __tablename__ = "register_rank_province"
    id = Column(Integer, primary_key=True, index=True)
    rank_name = Column(String(32))
    group_id = Column(Integer)
    path = Column(String(32))


class game_rank(Base):
    __tablename__ = "game_rank"
    id = Column(Integer, primary_key=True, index=True)
    rank_name = Column(String(32))
    group_id = Column(Integer)
    path = Column(String(32))
    group_name = Column(String(32))
    sort_id = Column(Integer)

class games_rank_table_list(Base):
    __tablename__ = "games_rank_table_list"
    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(32))
    sort_id = Column(Integer)


class privilage_to_rank(Base):
    __tablename__ = "privilage_to_rank"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, ForeignKey("users_register.dbid"))
    rank_id = Column(Integer, ForeignKey("grant_rank.rank_id"))


class grant_rank(Base):
    __tablename__ = "grant_rank"
    id = Column(Integer, primary_key=True, index=True)
    rank_id = Column(Integer, unique=True)
    rank_name = Column(String(32))
    group_id = Column(Integer)
    acces_to_register = Column(Boolean)
    acces_to_grant_rank = Column(Boolean)
    acces_to_staff_user = Column(Boolean)
    access_to_game_rank = Column(Boolean)
    parents = relationship(privilage_to_rank, cascade="all,delete")


class modules_settings(Base):
    __tablename__ = "modules_settings"
    id = Column(Integer, primary_key=True, index=True)
    setting = Column(String(32))
    options = Column(String(32))


class base_users_on_teamsepak(Base):
    __tablename__ = "base_users_on_teamsepak"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, unique=True)
    UID = Column(String(32), unique=True)
    IP = Column(Text)
    Nick = Column(Text(convert_unicode=True))


class base_users_info_on_teamsepak(Base):
    __tablename__ = "base_users_info_on_teamsepak"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, unique=True)
    total_connections = Column(Integer)
    real_total_connections = Column(Integer)
    created = Column(Integer)
    last_connect = Column(Integer)
    myteamspeak_id = Column(String(128))
    description = Column(Text(convert_unicode=True))


class base_users_misc_on_teamsepak(Base):
    __tablename__ = "base_users_misc_on_teamsepak"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, unique=True)
    client_badges = Column(String(128))
    client_country = Column(String(128))
    client_version = Column(String(128))
    platform = Column(String(128))


class base_users_server_data_on_teamsepak(Base):
    __tablename__ = "base_users_server_data_on_teamsepak"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, unique=True)
    server_groups = Column(String(128))
    is_register = Column(Boolean) 
    check_rules = Column(Boolean)


class time_users_on_teamsepak(Base):
    __tablename__ = "timing_users_on_teamsepak"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer)
    TIME_TOTAL = Column(Integer)
    TIME_ONLINE = Column(Integer)
    TIME_AWAY = Column(Integer)
    TIME_IDLE = Column(Integer)
    TIME_MIC_DISABLED = Column(Integer)


class rank_limit(Base):
    __tablename__ = "rank_limit"
    id = Column(Integer, primary_key=True, index=True)
    rank_id = Column(Integer)
    rank_name = Column(String(128))
    limit_register_rank = Column(Integer)


class read_message(Base):
    __tablename__ = "read_messages"
    id = Column(Integer, primary_key=True, index=True)
    dbid = Column(Integer)
    read_msg = Column(String(256))


class message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256))
    date = Column(String(256))
    message = Column(String(1024))
    author = Column(Integer)
    to_all = Column(Boolean, default=False)
    to_group_id = Column(String(256))
    to_id = Column(String(256))
    to_staff_rank = Column(String(256))
    priority = Column(Integer)
    readable = Column(Boolean)
    date_auto_arch = Column(String(256))
    date_auto_pub = Column(String(256))
    archive = Column(Boolean, default=False)


class CheckedIP(Base):
    __tablename__ = "CheckedIP"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(128))
    asn = Column(String(128))
    provider = Column(String(128))
    continent = Column(String(128))
    country = Column(String(128))
    city = Column(String(128))
    region = Column(String(128))
    region_code = Column(String(128))
    latitude = Column(String(128))
    longitude = Column(String(128))
    iso_code = Column(String(128))
    proxy = Column(String(128))
    type = Column(String(128))
    port = Column(String(128))
    risk = Column(String(128))
    attack_history = Column(String(128))
    last_seen_human = Column(String(128))
    last_seen_unix = Column(String(128))


class IpHistory(Base):
    __tablename__ = "IpHistory"
    id = Column(Integer, primary_key=True, index=True)
    id_ip = Column(Integer)
    dbid = Column(Integer)
    time = Column(Integer)


class NickHistory(Base):
    __tablename__ = "NickHistory"
    id = Column(Integer, primary_key=True, index=True)
    Nick = Column(Text(convert_unicode=True))
    dbid = Column(Integer)
    time = Column(Integer)


class OnlineUserOnTs(Base):
    __tablename__ = "OnlineUserOnTs"
    id = Column(Integer, primary_key=True, index=True)
    list = Column(String(1024))


class ActionBanType(Base):
    __tablename__ = "ActionBanType"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    group_id = Column(Integer)
    action = Column(String(256))
    time = Column(Boolean)


class ActiveModules(Base):
    __tablename__ = "active_modules"
    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String(32))
    status = Column(Boolean)


class BanPermission(Base):
    __tablename__ = "ban_permission"
    id = Column(Integer, primary_key=True, index=True)
    rank_grant_id = Column(Integer)  # grant
    action_ban_id = Column(Integer)
    max_time_to_action = Column(Integer)
    two_factor_auth = Column(Boolean)
    add = Column(Boolean)
    limit_per_10m = Column(Integer)
    limit_per_1d = Column(Integer)
    overflow = Column(Boolean)
    commit = Column(Boolean)
    commit_auto = Column(Boolean)
    delete = Column(Boolean)


class BanTable(Base):
    __tablename__ = "ban_table"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(1024))
    description = Column(String(1024))
    skip_grant = Column(Boolean)
    active = Column(Boolean)


class BanTimes(Base):
    __tablename__ = "ban_times"
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer)
    ban_id = Column(Integer)
    times_from = Column(Integer)
    times_from_setting = Column(String(128))
    times_to = Column(Integer)
    times_to_setting = Column(String(128))
    time_from = Column(Integer)
    time_from_setting = Column(String(128))
    time_to = Column(Integer)
    time_to_setting = Column(String(128))
    points = Column(Integer)


class BanHistoryTable(Base):
    __tablename__ = "ban_history_table"
    id = Column(Integer, primary_key=True, index=True)
    ban_client_dbid = Column(Integer)
    ban_id = Column(Integer)
    action_id = Column(Integer)
    additional_info = Column(String(1024))
    add_admin_dbid = Column(Integer)
    time_add = Column(Integer)
    time_to = Column(Integer)
    active = Column(Boolean)
    time_to_overflow = Column(Integer)
    to_commit = Column(Boolean)
    commit = Column(Boolean)
    commit_admin_dbid = Column(Integer)
    time_commit = Column(Integer)
    auto_ban = Column(Boolean)
    removed = Column(Boolean)
    removed_dbid = Column(Integer)
    time_removed = Column(Integer)


