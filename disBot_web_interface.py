import os
import mysql.connector

from flask import Flask, render_template, redirect, url_for
from flask_discord import DiscordOAuth2Session, Unauthorized, AccessDenied, requires_authorization


# Get SQL database details
dbHost = os.getenv('dbHost')
dbUser = os.getenv('dbUser')
dbPassword = os.getenv('dbPassword')
db = os.getenv('database')

app = Flask(__name__)

app.secret_key = b"%\xe0'\x01\xdeH\x8e\x85m|\xb3\xffCN\xc9g"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"  

app.config["DISCORD_CLIENT_ID"] = 843032598011445248
app.config["DISCORD_CLIENT_SECRET"] = "E827wO8tzzxIjqAldZhTCaxlmxdOKLJ_"
app.config["DISCORD_BOT_TOKEN"] = "ODExNTAwNTYyMDQ1ODYxOTE5.YCzGyg.p5Ca2fLh-e5WWcJyMxTqr0VA2HM"
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:8080/callback"

discord = DiscordOAuth2Session(app)

# Send a welcome message to the user through Discord DM when they log in through web interface
def welcome_user(user):
    dm_channel = discord.bot_request("/users/@me/channels", "POST", json={"recipient_id": user.id})
    return discord.bot_request(
        f"/channels/{dm_channel['id']}/messages", "POST", json={"content": "Hello " + user.name + ". This message is to inform tht you recently logged into my web interface."}
    )


#Initial page that is displayed when accessing web interface
@app.route("/")
def index():
    if not discord.authorized:
        return render_template("login.html")
    
    user = discord.fetch_user()

    templateData = {
            'user' : user
        }

    
        
    return render_template("index.html", **templateData, welcome='Welcome ' + user.name)

#Catches any 'Unathorized' errors that are thrown. Redirects to index.html.
@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("index"))

#Catches any 'AccessDenied' errors that are thrown. Redirects to index.html.
@app.errorhandler(AccessDenied)
def redirect_unauthorized(e):
    return redirect(url_for("index"))

# Login page which creates the discord session for the user login.
@app.route("/login/")
def login():
    return discord.create_session()

# Executes when the user logs in discord's OAuth returns back to the web interface
@app.route("/callback/")
def callback():
    data = discord.callback()
    redirect_to = data.get("redirect", "/")
    
    return redirect(redirect_to)

#HTML page for displaying the topics SQL table 
@app.route('/displayTopics.html')
def displayTopics():

    # Initialise connection to SQL database with details from .env file
    mydb = mysql.connector.connect(
        host=dbHost,
        user=dbUser,
        password=dbPassword,
        database=db
    )

    with mydb:
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM topics ORDER BY count DESC")
        result = cursor.fetchall()
        
    templateData = {
        'topics' : result
        }
    return render_template('displayTopics.html', **templateData)

# Executes when the user presses the logout button in index.html
@app.route("/logout/")
def logout():
    discord.revoke()
    return redirect(url_for(".index"))

if __name__ == "__main__":
    app.run(debug=True, port=8080, host='127.0.0.1')