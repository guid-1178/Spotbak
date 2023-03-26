import sys, os, sqlite3, requests,json, base64

class Database(object):

    def __init__(self,path):
        try:
            self._db_connection = sqlite3.connect(path)
            self._db_cur = self._db_connection.cursor()
        except sqlite3.OperationalError as e:
            print(e)

        

    def query(self, query):
        return self._db_cur.execute(query)


    def __del__(self):
        self._db_connection.close()

class spotify(object):
    def __init__(self,config):
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.account_url = config['accounts_url']
        self.api_url = config['api_url']
        self.callback_url = config['callback_url']
        self.scopes = "%20".join(config['scopes'])
        self.client_encoded = base64.b64encode(bytes(self.client_id + ":" + self.client_secret, 'utf-8'))

    def get_userinfo (self,access_token):
        headers = { 'Authorization' : 'Bearer  {0}'.format(access_token) }
        r = requests.get(self.api_url + '/v1/me', headers=headers)
        return(json.loads(r.text))   

    def get_token(self,code):
        headers = {	"content-type": "application/x-www-form-urlencoded", 'Authorization' : 'Basic  {0}'.format(self.client_encoded.decode('utf-8')) }
        payload = {'grant_type': 'authorization_code',
        'code': code ,
        'redirect_uri': self.callback_url}
        r = requests.post(self.account_url+"/api/token", headers=headers, params=payload)
        return(r.text)

    def check_token(self,access_token):
        headers = { 'Authorization' : 'Bearer  {0}'.format(access_token) }
        r = requests.get(self.api_url + '/v1/me', headers=headers)
        return(json.loads(r.text))  

    def renew_token(self,refresh_token):
        headers = {	"content-type": "application/x-www-form-urlencoded", 'Authorization' : 'Basic  {0}'.format(self.client_encoded.decode('utf-8')) }
        payload = {'grant_type': 'refresh_token',
        'refresh_token': refresh_token ,
        'redirect_uri': self.callback_url}
        r = requests.post(self.account_url + "/api/token", headers=headers, params=payload)
        return(json.loads(r.text))

    def get_playlist(self,access_token,userid):
        headers = { 'Authorization' : 'Bearer  {0}'.format(access_token) }
        r = requests.get(self.api_url + '/v1/users/{0}/playlists'.format(userid), headers=headers)
        return(json.loads(r.text))
        
    def get_tracks(self,access_token,plid):
        headers = { 'Authorization' : 'Bearer  {0}'.format(access_token) }
        r = requests.get(self.api_url + '/v1/playlists/{0}/tracks'.format(plid), headers=headers)
        return(json.loads(r.text))


def installdb(dbPath,dbFullPath,csvPath):
   
    for path in [csvPath,dbPath]:
        try:
            if not os.path.exists(path):
                os.mkdir(path)
        except:
            print(sys.exc_info()[0])
            sys.exit("ERROR: Problems while creating folders")

    db = Database(dbFullPath)
    tablecheck = db.query("""SELECT name FROM sqlite_master WHERE type='table' AND name='users_spotbak';""").fetchone()
    
    if not tablecheck:
        create_table = """CREATE TABLE
        users_spotbak(user TEXT NOT NULL,
        country TEXT, 
        access_token TEXT, 
        refresh_token TEXT, 
        last_updated DATETIME, 
        userid TEXT)"""
        
        db.query(create_table)
    return True


def UserCheck(user_info,dbFullPath):
    db = Database(dbFullPath)
    
    result = db.query(''' SELECT userid from users_spotbak where userid= '{0}';'''.format(user_info["id"])).fetchone()
    if result:
        return True
    if not result:
        return False


def AddUserSQL(user_info,refresh,access,dbFullPath):
    db = Database(dbFullPath)

    print('User not found,  creating records...')
    sqlqry = ''' INSERT into users_spotbak(user,country,refresh_token,access_token,last_updated,userid) values('{0}','{1}','{2}','{3}',CURRENT_TIMESTAMP,{4});'''
    db.query(sqlqry.format(user_info['display_name'],user_info['country'],refresh,access,user_info['id']))
    db._db_connection.commit()


