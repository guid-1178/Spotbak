from flask import render_template,Flask, session,request,redirect

from install import installdb,UserCheck,AddUserSQL,spotify
import yaml,json, uuid

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)


def UpdateConfig(config,data):
    file =  open("config.yaml", "w")
    print(config["db"]["path"])
    config['db']['path'] = data["db_path"]
    config['csv']['path'] = data["csv_path"]
    yaml.dump(config,file)
    file.close()
  
client = spotify(config['spotify'])
app = Flask(__name__)
# use UUID to generate session key.
app.secret_key = str(uuid.uuid4()).replace("-","")
app.config['config'] = config

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup', methods=['POST','GET'])
def dbsetup():
    db_path = app.config['config']['db']['path']
    csv_path = app.config['config']['csv']['path']
    db_fullpath = str(app.config['config']['db']['path']+"/"+app.config['config']['db']['name'])

    if request.method == 'POST':
        if 'csvpath' and 'dbpath' in request.form:

            data = {"csv_path":request.form['csvpath'],"db_path":request.form['dbpath']}
            
            print(data["db_path"])
            UpdateConfig(app.config['config'],data)
            return redirect(request.referrer)
        
        if 'clear-config' in request.form:
            data = {"csv_path":'',"db_path":''}
            UpdateConfig(app.config['config'],data)
            session.clear()
            return redirect(request.referrer)
        
        if 'install-db' in request.form:
            if installdb(db_path,db_fullpath,csv_path):
                session['installed'] = True
            return redirect(request.referrer)        
        
    return render_template('setup.html',db_path=db_path,csv_path=csv_path)

@app.route('/spotify/auth', methods=['GET'])
def auth():
    name = "jeff"
    config=app.config['config']['spotify']
    scopes = "%20".join(config['scopes'])
    auth_url = f"{config['accounts_url']}/authorize?client_id={config['client_id']}&response_type=code&redirect_uri={config['callback_url']}&scope={scopes}"

    print("Auth page")
    return render_template('spotify.html',auth_url=auth_url)

@app.route('/spotify/callback', methods=['GET'])
def callback(code=None,error=None):
    error = request.args.get("error")
    code = request.args.get("code")
    db_fullpath = str(app.config['config']['db']['path']+"/"+app.config['config']['db']['name'])

    if code:
        response = client.get_token(code)
        token = json.loads(response)
        print(token)
        if 'access_token' in token:
            user = client.get_userinfo(token["access_token"])
        else:
            error = token
            user = ''
        if user:
            #user = json.loads(user)
            print(user['display_name'])
            if not UserCheck(user,db_fullpath):
                AddUserSQL(user,token['refresh_token'],token['access_token'],db_fullpath)
            if UserCheck(user,db_fullpath):
                session['user-installed'] = True

        
    if error:
        print(error)
    return render_template('spotify.html',error=error,user_info=user)

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html')