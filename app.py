from flask import Flask, render_template, request, redirect, session, url_for
import hashlib
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from flask_mysqldb import MySQL  
import AudioTools
import os
import time
app = Flask(__name__)
app.secret_key="key" #For session variables
app.config['MYSQL_HOST']='mysql.2223.lakeside-cs.org'
app.config['MYSQL_USER']='student2223'
app.config['MYSQL_PASSWORD']='m545CS42223' 
app.config['MYSQL_DB']='2223project_1'
app.config['MYSQL_CURSORCLASS']='DictCursor'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "secret"
mysql = MySQL(app) 

def executeQuery(query, queryVars):
    print(query, queryVars)
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
    out = dict()
    if not session or not session["filename"]:
        session["filename"] = None
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
                out["type"] = "detect"
                output = dict()
                output["title"] = AudioTools.detectSong(session["filename"]).get("track").get("title")
                output["artist"] = AudioTools.detectSong(session["filename"]).get("track").get("subtitle")
                output["image"] = AudioTools.detectSong(session["filename"]).get("track").get("images").get("coverart")
            elif request.values.get("convert"):
                print("convert")
            elif request.values.get("keychange"):
                out["type"] = "files"
                output = AudioTools.keyChange(session["filename"], 'static/output/', 10)
            elif request.values.get("amplify"):
                print("****************AMPLIFY")
                out["type"] = "files"
                output = AudioTools.amplify(session["filename"], 'static/output/',4)
            elif request.values.get("split"):
                out["type"] = "files"
                output = AudioTools.split(session["filename"], 'static/output/', 2)
            elif request.values.get("waveform"):
                out["type"] = "waveform"
                output = AudioTools.displayWaveform(session["filename"])
    out["output"] = output
    return render_template('editor.html.j2', t=request.method, fn=session["filename"], out=out)

#Login
@app.route('/login', methods=['GET', 'POST']) 
def login(): 
    if request.method=="GET": 
        return render_template("login.html.j2")
    elif request.method=="POST": 
        userput=request.values.get("username") 
        passput=request.values.get("paswd") 
        passwdsha=hashlib.sha256(passput.encode('utf-8')).hexdigest()
        data = executeQuery("SELECT * FROM audiocenter_users WHERE username=%s AND password=%s", (userput, passwdsha))
        if len(data) > 0: 
            session["username"]=userput
            return redirect(url_for("index"))
        else:
            return render_template("login.html.j2", invalid=True)

#Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup(): 
    if request.method=="GET": 
        return render_template("signup.html.j2") 
    else: 
        #I am not doing server-side validation for the username and password because the request.values.get always returns a string, which can be hashed
        #If the user really wants to put their password as a color, that's fine
        username=request.values.get("username")
        paswd=request.values.get("paswd") 
        paswdsha=hashlib.sha256(paswd.encode('utf-8')).hexdigest()
        data = executeQuery("SELECT * FROM audiocenter_users WHERE username=%s", (username,))
        if len(data)==0:
            paswdsha=hashlib.sha256(paswd.encode('utf-8')).hexdigest()
            executeQuery("INSERT INTO audiocenter_users VALUES (NULL, %s, %s);", (username, paswdsha))
            return redirect(url_for("login"))
        else:
            data = executeQuery("SELECT * FROM audiocenter_users", ())
            return render_template("signup.html.j2", invalid=True)