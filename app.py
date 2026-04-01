from flask import Flask,render_template,redirect,url_for
from flask_dance.contrib.google import make_google_blueprint, google
import requests
import dotenv
import os
import json
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # to be removed
dotenv.load_dotenv()
app = Flask(__name__)
app.secret_key=os.getenv('APP_SECRET_KEY')
app.config["GOOGLE_OAUTH_CLIENT_ID"]=os.getenv('GOOGLE_CLIENT')
app.config["GOOGLE_OAUTH_CLIENT_SECRET"]=os.getenv('GOOGLE_CLIENT_PASS')
blueprint = make_google_blueprint(scope=["openid","https://www.googleapis.com/auth/userinfo.email","https://www.googleapis.com/auth/userinfo.profile"],redirect_to="home")
print(blueprint.session.authorization_url)
dataFile = 'data.json'

def load():
    if not os.path.exists(dataFile):
        return {}
    
    with open(dataFile,"r") as f:
        try:
            users = json.load(f)
            return users
        except:
            print(Exception)
            return {}
def save(users):
    with open(dataFile,"w") as f:
            json.dump(users,f,indent=4)

def load_users_data(email:str) -> dict:
    users = load()
    user_data = users.get(email,{})
    movies = user_data.get('movies',[])
    shows = user_data.get('shows',[])
    return user_data,movies,shows

def add_towatch(email:str,ismovie:bool,content:dict)-> bool:
    users = load()
    if email not in users:
        return False
    if ismovie:
        users[email]["movies"].append(content)
    elif not ismovie:
        users[email]["shows"].append(content)
    save(users)
    return True

def new_user(email:str) -> bool:
    users = load()
    if email in users:
        return True
    users[email] = {"movies":[],"shows":[]}
    save(users)
    return False
        

def delete_account(email)->bool:
    users = load()
    if email in users:
        del users[email]
        save(users)
        return True
    print(f"user {email} not found")
    return False

def delete_element(email:str,id:int,ismovie:bool)->bool:
    users = load()
    if email not in users:
        print(f"user {email} not found")
        return False
    if ismovie:
        users[email]['movies']=[m for m in users[email]["movies"] if m['id']!= id]
    else:
        users[email]['movies']=[m for m in users[email]["movies"] if m['id']!= id]
    save(users)
    return True

app.register_blueprint(blueprint)

@app.route("/")
def login():
    return render_template("index.html")
@app.route("/home")
def home():
    if not google.authorized:
        return redirect(url_for("google.login"))
    data = google.get("/oauth2/v2/userinfo")
    if not data.ok:
        return "failed to fetch data"
    userinfo = data.json()
    return f"<h2> Welcome {userinfo['name']} to the nest</h2>"
@app.route("/add")
def add():
    return
if __name__ =='__main__':
    app.run(port=5000,debug=True)