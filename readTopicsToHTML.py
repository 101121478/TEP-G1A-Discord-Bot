from flask import Flask, render_template
import mysql.connector
import os
import sys, time
from dotenv import load_dotenv


load_dotenv()

# Get SQL database details
dbHost = os.getenv('dbHost')
dbUser = os.getenv('dbUser')
dbPassword = os.getenv('dbPassword')
db = os.getenv('database')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
        cursor.execute("SELECT * FROM topics")
        result = cursor.fetchall()
        
    templateData = {
        'topics' : result
        }
    return render_template('displayTopics.html', **templateData)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1') 