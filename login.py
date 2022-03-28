
unauthorized_operation_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="UNAUTHORIZED OPERATION",
        )


# get current limit rank
# @router.get("/get_current_rank_limit/")
# async def get_rank_limit(db: Session = Depends(function.get_db),
#                          user: schemas.current_user = Depends(function.decode_auth_token)):
#     dbid = int(user[1])
#     with ts3.query.TS3Connection(config.query_ts3['host'], config.query_ts3['port']) as ts3conn:
#         ts3conn.login(client_login_name=config.query_ts3['login'], client_login_password=config.query_ts3['pass'])
#         ts3conn.use(sid=1)
#         try:
#             ts3conn.clientupdate(client_nickname="Sauron TS3|WEB")
#         except:
#             pass
#         limit = function.current_limit_rank_games(ts3conn, dbid, db)
#     return limit


# return_current_rank
@router.get("/current_rank/") ??????????????
async def return_current_rank(user: schemas.current_user = Depends(function.decode_auth_token)):
    dbid = int(user[1])
    with ts3.query.TS3Connection(config.query_ts3['host'], config.query_ts3['port']) as ts3conn:
        ts3conn.login(client_login_name=config.query_ts3['login'], client_login_password=config.query_ts3['pass'])
        ts3conn.use(sid=1)
        try:
            ts3conn.clientupdate(client_nickname="Sauron TS3|WEB")
        except:
            pass
        rank_list = function.return_current_rank_list(ts3conn, dbid, db)
    return rank_list


# return current to set rank array
# @router.get("/current_to_set_array/{group_name}")
# async def return_current_to_set_array(group_name: str,
#                                       user: schemas.current_user = Depends(function.decode_auth_token),
#                                       db: Session = Depends(function.get_db)):
#     dbid = int(user[1])
#     response_db = crud.get_list_rank_games_by_group_name(db, group_name)
#     to_set_rank_list = []
#     with ts3.query.TS3Connection(config.query_ts3['host'], config.query_ts3['port']) as ts3conn:
#         ts3conn.login(client_login_name=config.query_ts3['login'], client_login_password=config.query_ts3['pass'])
#         ts3conn.use(sid=1)
#         try:
#             ts3conn.clientupdate(client_nickname="Sauron TS3|WEB")
#         except:
#             pass
#         rank_list = function.return_current_rank_list(ts3conn, dbid, db)
#     for i in response_db:
#         for z in rank_list:
#             if int(z) == i.group_id:
#                 to_set_rank_list.append(i.group_id)
#     return to_set_rank_list


# set rank games
@router.put("/set_rank_games/")
async def set_rank_games(rank_list_to_set: list,
                         user: schemas.current_user = Depends(function.decode_auth_token),
                         db: Session = Depends(function.get_db)):
    dbid = int(user[1])
    with ts3.query.TS3Connection(config.query_ts3['host'], config.query_ts3['port']) as ts3conn:
        ts3conn.login(client_login_name=config.query_ts3['login'], client_login_password=config.query_ts3['pass'])
        ts3conn.use(sid=1)
        try:
            ts3conn.clientupdate(client_nickname="Sauron TS3|WEB")
        except:
            pass
        current_rank_list = function.return_current_rank_list(ts3conn, dbid, db)
        limit_rank = function.current_limit_rank_games(ts3conn, dbid, db)
        # if len(rank_list_to_set) > limit_rank:
        #     return unauthorized_operation_exception
        all_game_rank_list = crud.return_all_rank_games(db)
        all_game_rank_list_id = []
        for i in all_game_rank_list:
            all_game_rank_list_id.append(i.group_id)

        for i in rank_list_to_set:
            if i not in all_game_rank_list_id:
                return unauthorized_operation_exception
        print("alles clar")
        for i in current_rank_list:
            if int(i) in all_game_rank_list_id and int(i) not in rank_list_to_set:
                webDeamon.delete_rank(ts3conn, i, dbid)
                crud.update_rank_in_db(db, dbid, i, "DELETE")
        for i in rank_list_to_set:
            if i in all_game_rank_list_id and str(i) not in current_rank_list:
                webDeamon.add_rank(ts3conn, i, dbid)
                crud.update_rank_in_db(db, dbid, i, "ADD")
        # TODO curent rank list to int list






    return


@router.post("/get_message_by_id/")
async def get_message_by_id(message_id: schemas.MessageId,
                         user: schemas.current_user = Depends(function.decode_auth_token),
                         db: Session = Depends(function.get_db)):
    print("ss")
    return crud.return_message_by_id(db, message_id.message_id)


@router.post("/recovery/send_token/")
async def post_recovery_send_token(login: schemas.Login, db: Session = Depends(function.get_db)):
    user_not_found = HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="User Not Found",
    )
    user = crud.get_user_from_user_register_by_login(db, login.login)
    if not user:
        raise user_not_found
    data_token = crud.get_user_temp_token(db, user.dbid)
    letters = string.ascii_letters
    temp_token = (''.join(random.choice(letters) for i in range(10)))
    credentials = schemas.Temp_Token(DBID=user.dbid, token=temp_token)
    if data_token:
        crud.update_user_temp_token(db, credentials)
    else:
        crud.create_user_temp_token(db, credentials)
    webDeamon.send_token_to_user(user.dbid, temp_token)


@router.post("/recovery/send_password/")
async def post_recovery_send_password(data: schemas.RecoverPasswordToken, db: Session = Depends(function.get_db)):
    token_incorrect = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Token INCORECT",
    )
    user = crud.get_user_from_user_register_by_login(db, data.login)
    data_token = crud.get_temp_token_data_by_token(db, data.token)
    if not user or not data_token:
        raise token_incorrect
    if data_token.DBID == user.dbid:
        encoded_password = function.hash_password(data.password.encode('utf-8'))
        crud.update_password(db, data_token.DBID, encoded_password)
        crud.delete_temp_token(db, data.token)
        #TODO check seciurity it

