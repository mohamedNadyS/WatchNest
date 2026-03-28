from flask import Flask,render_template,redirect,url_for
from flask_dance.contrib.google import make_google_blueprint, google
import requests
import dotenv
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
dotenv.load_dotenv()
app = Flask(__name__)
app.secret_key=os.getenv('APP_SECRET_KEY')
app.config["GOOGLE_OAUTH_CLIENT_ID"]=os.getenv('GOOGLE_CLIENT')
app.config["GOOGLE_OAUTH_CLIENT_SECRET"]=os.getenv('GOOGLE_CLIENT_PASS')
blueprint = make_google_blueprint(scope=["openid","https://www.googleapis.com/auth/userinfo.email","https://www.googleapis.com/auth/userinfo.profile"],redirect_to="home")
print(blueprint.session.authorization_url)

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
if __name__ =='__main__':
    app.run(port=5000,debug=True)