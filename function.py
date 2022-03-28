
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


