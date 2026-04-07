from flask import Flask,render_template,redirect,url_for,request
from flask_dance.contrib.google import make_google_blueprint, google
import requests
import dotenv
import os
import json
import uuid
dotenv.load_dotenv()
app = Flask(__name__)
app.secret_key=os.getenv('APP_SECRET_KEY')
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.getenv('GOOGLE_CLIENT')
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.getenv('GOOGLE_CLIENT_PASS')

blueprint = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT'),
    client_secret=os.getenv('GOOGLE_CLIENT_PASS'),
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_to="home"
)
app.register_blueprint(blueprint, url_prefix="/login")

JSONBIN_KEY=os.getenv('JSONBIN_KEY')
JSONBIN_BIN_ID=os.getenv('JSONBIN_BIN_ID')
JSONBIN_URL=f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
HEADERS = {"X-Master-Key": JSONBIN_API_KEY}

def load():
    try:
        resp = requests.get(f"{JSONBIN_URL}/latest",headers=HEADERS)
        if resp.ok:
            return resp.json().get('record', {})
        return {}
    except:
        return {}

def save(users):
    try:
        requests.put(JSONBIN_URL, json=users, headers={"Content-Type": "application/json", **HEADERS})
    except Exception as e:
        print(f"Cloud Save Error: {e}")

def load_users_data(email:str):
    users = load()
    user_data = users.get(email,{})
    movies = user_data.get('movies',[])
    shows = user_data.get('shows',[])
    return user_data, movies, shows

def add_towatch(email:str, ismovie:bool, content:dict):
    users = load()
    if email not in users:
        new_user(email)
        users = load()
    
    key = "movies" if ismovie else "shows"
    users[email][key].append(content)
    save(users)
    return True

def new_user(email:str):
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
        users[email]['shows']=[m for m in users[email]["shows"] if m['id']!= id]
    save(users)
    return True

@app.route("/")
def login():
    if google.authorized:
        return redirect(url_for("home"))
    return render_template("index.html")

@app.route("/home")
def home():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info from Google.", 400
    
    userinfo = resp.json()
    email = userinfo['email']
    new_user(email)
    _, movies, shows = load_users_data(email)

    return render_template('home.html', name=userinfo['name'], movies=movies, shows=shows)

@app.route("/add", methods=['GET','POST'])
def add():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('type')
        
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok: return redirect(url_for('login'))
        email = resp.json()['email']
        
        content = {"id": str(uuid.uuid4()), "title": title}
        ismovie = (category == "movie")
        add_towatch(email, ismovie, content)
        return redirect(url_for('home'))
        
    return render_template("add.html")

@app.route("/delete/<type>/<id>")
def delete(type, id):
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok: return redirect(url_for('login'))
    email = resp.json()['email']
    
    ismovie = (type == "movie")
    delete_element(email, id, ismovie)
    return redirect(url_for("home"))

@app.route("/delete-account")
def delete_acc():
    if not google.authorized:
        return redirect(url_for("google.login"))
    email = google.get("/oauth2/v2/userinfo").json()['email']
    delete_account(email)
    if blueprint.token:
        del blueprint.token
    return redirect(url_for('login'))
@app.route("/logout")
def logout():
    if blueprint.token:
        del blueprint.token
    return redirect(url_for('login'))
if __name__ =='__main__':
    app.run(port=5000,debug=True)