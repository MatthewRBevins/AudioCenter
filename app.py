from flask import Flask, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from flask_mysqldb import MySQL
import AudioTools
import time
app = Flask(__name__)

app.config['MYSQL_HOST'] = "mysql.2223.lakeside-cs.org"
app.config['MYSQL_USER'] = "student2223"
app.config['MYSQL_PASSWORD'] = "m545CS42223"
app.config['MYSQL_DB'] = "2223project_1"
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "secret"
mysql = MySQL(app)

def executeQuery(query, queryVars):
    #Initialize database connection
    cursor = mysql.connection.cursor()
    #Execute query
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    #Fetch data from query
    return cursor.fetchall()

@app.route('/')
def index():
    return render_template('index.html.j2')

@app.route('/editor', methods=["GET", "POST"])
def editor():
    output = None
    if request.method == "POST":
        if request.values.get("form") == "1":
            f = request.files["file"]
            t = str(int(time.time()))
            filename = 'static/audio/' + f.filename.split('.')[0] + ' [' + t + '].' + f.filename.split('.')[1]
            f.save(filename)
            session["filename"] = filename
        elif request.values.get("form") == "2":
            if request.values.get("detect"):
                output = AudioTools.detectSong(session["filename"])
            elif request.values.get("keychange"):
                output = AudioTools.keyChange(session["filename"], 'static/output', 4)
            elif request.values.get("amplify"):
                output = AudioTools.amplify(session["filename"], 'static/output',4)
            elif request.values.get("split"):
                output = AudioTools.split(session["filename"], 'static/output/', 2)
            elif request.values.get("waveform"):
                output = AudioTools.displayWaveform(session["filename"])
    return render_template('editor.html.j2', t=request.method, fn=session["filename"], out=output)

@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template('login.html.j2')

