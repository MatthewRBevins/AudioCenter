from flask import Flask, render_template, request, redirect, session, url_for
import hashlib
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from flask_mysqldb import MySQL  
import numpy as np
import AudioTools
import os
import time
import datetime
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

class userData:
    def __init__(self, username, loggedIn):
        self.username = username
        self.loggedIn = loggedIn
        data = executeQuery("SELECT joined,pfp,bio,place,website FROM audiocenter_users WHERE username=%s", (self.username,))
        if len(data) > 0:
            self.joined = data[0]["joined"]
            self.pfp = data[0]["pfp"]
            self.bio = data[0]["bio"]
            self.place = data[0]["place"]
            self.website = data[0]["website"]
        else:
            self.joined = None
            self.pfp = None
            self.bio = None
            self.place = None
            self.website = None
    def createDict(self):
        keys = ["username", "loggedIn", "joined", "pfp", "bio", "place", "website"]
        values = [self.username, self.loggedIn, self.joined, self.pfp, self.bio, self.place, self.website]
        data = list(zip(keys, values))
        d = {k: v for k, v in data}
        return d

def verifySessions():
    print("VERIFY SESSIONS")
    #Update this when adding new session vars
    #session["userData"]["loggedIn"] = True
    try:
        session["userData"]
    except KeyError:
        session["userData"] = userData("", False).createDict()
    try:
        session["filename"]
    except KeyError:
        session["filename"] = None
    print("DONE")

@app.route('/')
def index():
    verifySessions()
    return render_template('index.html.j2', userData=session["userData"])

@app.route('/detect', methods=["GET","POST"])
def detect():
    verifySessions()
    output = None
    out = dict() 
    errors = []
    if request.method == "POST":
        print("HI")
        f = request.files["file"]
        t = str(int(time.time()))   
        filename = 'static/audio/' + f.filename.split('.')[0] + ' [' + t + '].' + f.filename.split('.')[1]
        f.save(filename) 
        session["filename"] = filename
        originalFilename = session["filename"] 
        t = str(int(time.time())) 
        trimmedFilename = 'static/audio/trimmed/' + t + '.wav'
        proxy = open(trimmedFilename, "w")
        AudioTools.trimSong(session["filename"], trimmedFilename)
        session["filename"] = trimmedFilename
        output = AudioTools.detectSong(session["filename"])
        out["type"] = "detect"
        session["filename"] = originalFilename
        out["output"] = output
        if output == None:
            errors = ['Song not detected.']
    return render_template('detect.html.j2', fn=session["filename"], userData=session["userData"], out=out, errors=errors)

@app.route('/convert', methods=["GET","POST"])
def convert():
    verifySessions()
    output = None
    out = dict() 
    errors = []
    basename = ""
    if request.method == "POST":
        print("HI")                         
        f = request.files["file"]
        t = str(int(time.time()))   
        filename = 'static/audio/' + f.filename.split('.')[0] + ' [' + t + '].' + f.filename.split('.')[1]
        f.save(filename) 
        session["filename"] = filename
        out["type"] = "convert"
        out["output"] = AudioTools.mp3towav(session["filename"])
        basename = os.path.basename(out["output"])
        
    return render_template('convert.html.j2', fn=session["filename"], userData=session["userData"], out=out, base=basename)

@app.route('/editor', methods=["GET", "POST"])
def editor():
    verifySessions()
    output = session["filename"]
    out = dict() 
    fileLength = AudioTools.length(output)
    errors = []
    if request.method == "POST":
        if request.values.get("form") == "1":
            f = request.files["file-open"]
            t = str(int(time.time()))   
            filename = 'static/audio/' + f.filename.split('.')[0] + ' [' + t + '].' + f.filename.split('.')[1]
            f.save(filename) 
            session["filename"] = filename
            fileLength = AudioTools.length(session["filename"])
        elif request.values.get("form") == "2":
            if session["filename"] != None:
                if request.values.get("key-change"):
                    steps = int(request.values.get("steps"))
                    out["type"] = "files"
                    output = AudioTools.keyChange(session["filename"], 'static/output/', steps)
                    session["filename"] = output[0]
                elif request.values.get("amplify"):
                    factor = float(request.values.get("factorAmp"))
                    print("****************AMPLIFY")
                    out["type"] = "files"
                    output = AudioTools.amplify(session["filename"], 'static/output/', factor)
                    session["filename"] = output[0]
                elif request.values.get("split-tracks"):
                    out["type"] = "files"
                    output = AudioTools.split(session["filename"], 'static/output/', 2)
                    session["filename"] = output[0]
                elif request.values.get("speed-change"):
                    factor = float(request.values.get("factorSpeed"))
                    out["type"] = "files"
                    output = AudioTools.changeSpeed(session["filename"], 'static/output/', factor)
                    session["filename"] = output[0]
            else:
                errors.append("You have not uploaded a file.")
    out["output"] = output
    return render_template('editor.html.j2', t=request.method, fn=session["filename"], out=out, errors=errors, userData=session["userData"], fileLength = fileLength)

#Login
@app.route('/login', methods=['GET', 'POST']) 
def login(): 
    verifySessions()
    if session["userData"]["loggedIn"]:
        return(redirect(url_for("profile")))
    if request.method=="GET": 
        return render_template("login.html.j2", userData=session["userData"])
    elif request.method=="POST": 
        userput=request.values.get("username") 
        passput=request.values.get("paswd") 
        passwdsha=hashlib.sha256(passput.encode('utf-8')).hexdigest()
        data = executeQuery("SELECT * FROM audiocenter_users WHERE username=%s AND password=%s", (userput, passwdsha))
        if len(data) > 0: 
            session["userData"] = userData(userput, True).createDict()
            return redirect(url_for("index"))
        else:
            return render_template("login.html.j2", invalid=True, userData=session["userData"])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    verifySessions()
    if not session["userData"]["loggedIn"]:
        return(redirect(url_for("login")))
    if request.method == "POST":
        if request.values.get("formnum") == "0":
            f = request.files["file-input"]
            try:
                os.mkdir('static/images/pfps/' + session["userData"]["username"])
            except:
                pass
            filename = 'static/images/pfps/' + session["userData"]["username"] + '/pfp.png'
            f.save(filename)
            executeQuery("UPDATE audiocenter_users SET pfp=%s WHERE username=%s", (True,session["userData"]["username"]))
        elif request.values.get("formnum") == "1":
            newUsername = request.values.get("username")
            if newUsername != "":
                data = executeQuery("SELECT * FROM audiocenter_users WHERE username=%s", (newUsername,))
                if len(data) == 0 or (len(data) == 1 and data[0]["username"] == session["userData"]["username"]):
                    executeQuery("UPDATE audiocenter_users SET username=%s WHERE username=%s", (newUsername, session["userData"]["username"]))
                    session["userData"] = userData(newUsername, True).createDict()
        elif request.values.get("formnum") == "2":
            newBio = request.values.get("bio")
            if newBio != "":
                executeQuery("UPDATE audiocenter_users SET bio=%s WHERE username=%s", (newBio, session["userData"]["username"]))
        elif request.values.get("formnum") == "3":
            newPlace = request.values.get("place")
            newWebsite = request.values.get("website")
            if newPlace != "":
                executeQuery("UPDATE audiocenter_users SET place=%s WHERE username=%s", (newPlace, session["userData"]["username"]))
            if newWebsite != "":
                executeQuery("UPDATE audiocenter_users SET website=%s WHERE username=%s", (newWebsite, session["userData"]["username"]))
    session["userData"] = userData(session["userData"]["username"], True).createDict()
    return render_template('profile.html.j2', edit=True, userData=session["userData"], userToShowData=session["userData"])

#Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup(): 
    verifySessions()
    if request.method=="GET": 
        return render_template("signup.html.j2", userData=session["userData"]) 
    else: 
        #I am not doing server-side validation for the username and password because the request.values.get always returns a string, which can be hashed
        #If the user really wants to put their password as a color, that's fine
        username=request.values.get("username")
        paswd=request.values.get("paswd") 
        paswdsha=hashlib.sha256(paswd.encode('utf-8')).hexdigest()
        data = executeQuery("SELECT * FROM audiocenter_users WHERE username=%s", (username,))
        if len(data)==0:
            paswdsha=hashlib.sha256(paswd.encode('utf-8')).hexdigest()
            date = datetime.datetime.now()
            date = date.strftime("%B %Y")
            executeQuery("INSERT INTO audiocenter_users(joined, username, password, bio, place, website) VALUES (%s, %s, %s, %s, %s, %s);", (date, username, paswdsha, "This user has not added a bio yet.", "Earth", ""))
            return redirect(url_for("login"))
        else:
            data = executeQuery("SELECT * FROM audiocenter_users", ())
            return render_template("signup.html.j2", invalid=True, userData=session["userData"])

@app.route('/@<userToShow>', methods = ["GET"])
def userShow(userToShow):
    data = executeQuery("SELECT * FROM audiocenter_users WHERE username=%s", (userToShow,))
    print("DATA:")
    if len(data) == 0:
        return render_template('index.html.j2', userData=session["userData"], errors=['User not found.'])
    userToShowData = userData(userToShow, False).createDict()
    return render_template('profile.html.j2', edit=False, userData=session["userData"], userToShowData=userToShowData)

@app.route('/signout', methods=['POST'])
def signout():
    session["userData"] = userData("", False).createDict()
    return redirect(url_for("index"))