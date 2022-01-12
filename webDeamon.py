#! /usr/bin/python3
import ts3
import modelsdb, schemas, crud


def convert_list_to_string(data):
    output = ""
    for element in data:
        output += element
    return output


def add_rank(ts3conn, rank_id, DBID):
    try:
        ts3conn.servergroupaddclient(sgid=rank_id, cldbid=DBID)
    except: return


def delete_rank(ts3conn, rank_id, DBID):
    try:
        ts3conn.servergroupdelclient(sgid=rank_id, cldbid=DBID)
    except: return


def online_info_user(ts3conn, DBID):
    try:
        user_info = ts3conn.clientdbinfo(cldbid=DBID)
        CLID = ts3conn.clientgetids(cluid=user_info[0]['client_unique_identifier'])
        CLID = int(CLID[0]['clid'])
    except: return
    info_client = ts3conn.clientinfo(clid=str(CLID))
    return info_client
    
def now_list_on_line(IP): #without QUERRY
    with ts3.query.TS3Connection("SECRET IP", 10011) as ts3conn:

        ts3conn.login(client_login_name="BOT_WEB", client_login_password="SECRET_PASSWORD")
        ts3conn.use(sid=1)
        try:
            ts3conn.clientupdate(client_nickname="Sauron TS3|WEB")
        except:
            pass
        list=ts3conn.clientlist()
        listaaam=[]
        nowonline=[]
        for i in list.parsed:
            try:
                info_client=ts3conn.clientinfo(clid=i['clid'])
                if info_client[0]['client_type']=='0':
                    if IP==info_client[0]['connection_client_ip']:
                        nowonline.append({'DBID': info_client[0]['client_database_id'],"IP": info_client[0]['connection_client_ip'],"Nick": info_client[0]['client_nickname'], "UID": info_client[0]['client_unique_identifier']})
            except: pass
        ts3conn.logout()
        ts3conn.quit()
        return nowonline
def get_DBID_by_UID(UID:str):
    with ts3.query.TS3Connection("SECRET IP", 10011) as ts3conn:

        ts3conn.login(client_login_name="BOT_WEB", client_login_password="SECRET_PASSWORD")
        ts3conn.use(sid=1)
        try:
            ts3conn.clientupdate(client_nickname="Sauron TS3|WEB")

        except:
            pass
        try:
            response=ts3conn.clientgetdbidfromuid(cluid=UID)
        except:
            return 0

        #servergrouppermlist        
        ts3conn.logout()
        ts3conn.quit()
        DBID=response.parsed[0]['cldbid']
    return DBID
def send_token_to_user(DBID,token):
    with ts3.query.TS3Connection("IP", 10011) as ts3conn:

        ts3conn.login(client_login_name="BOT_WEB", client_login_password="SECRET_PASSWORD")
        try:
            ts3conn.use(sid=1)
            try:
                ts3conn.clientupdate(client_nickname="Sauron TS3|WEB")
            except:
                pass
        

            user_info=ts3conn.clientdbinfo(cldbid=DBID)
            CLID=ts3conn.clientgetids(cluid=user_info[0]['client_unique_identifier'])
            CLID=CLID[0]['clid']
            message="[b]Twój klucz do autoryzowania się w systemie to: [COLOR=#ff0000][U]" + token +"[/COLOR][/B]"
            ts3conn.sendtextmessage(targetmode=1, target=CLID, msg=message)
        except: pass
       # ts3conn.logout()
       # ts3conn.quit()
def get_group_name(group_id):
        # with ts3.query.TS3Connection("localhost", 10011) as ts3conn:
    with ts3.query.TS3Connection("SECRET_IP", 10011) as ts3conn:

        ts3conn.login(client_login_name="BOT_WEB", client_login_password="SECRET_PASSWORD")
        ts3conn.use(sid=1)
        try:
            ts3conn.clientupdate(client_nickname="Sauron TS3|WEB")
        except:
            pass
        listgroup = ts3conn.servergrouplist()
        for i in listgroup.parsed:
            if i['sgid']==str(group_id):
                return i['name']
        return "----- BRAK RANGI NA TS3---- "
        ts3conn.logout()
        ts3conn.quit()


        



#    



