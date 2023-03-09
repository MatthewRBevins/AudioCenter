from flask import Flask, render_template, request, redirect, session, url_for
import hashlib
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from flask_mysqldb import MySQL  
import wave, audioop
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
import os
from pydub import AudioSegment
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

class Separate():
    def __init__(self, file, actualname):
        separator = Separator('spleeter:2stems')
        audio_loader = AudioAdapter.default()
        sample_rate = 44100
        waveform, _ = audio_loader.load(file, sample_rate=sample_rate)
        separator.separate_to_file(file, 'statiwc/output')
        self.filenames = ['static/output/' + actualname + '/accompaniment.wav', 'static/output/' + actualname + '/vocals.wav']

def amplify(file, factor): 
    factor = factor #Adjust volume by factor
    with wave.open(file, 'rb') as wav:
        p = wav.getparams()
        with wave.open('output.wav', 'wb') as audio:
            audio.setparams(p)
            frames = wav.readframes(p.nframes)
            audio.writeframesraw(audioop.mul(frames, p.sampwidth, factor))

def combine(sound1, sound2): 
    audiosound1 = AudioSegment.from_wav(sound1)
    audiosound2 = AudioSegment.from_wav(sound2)
    mixed = audiosound1.overlay(audiosound2) 
    mixed.export("mixed.wav", format='wav')

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

@app.route('/separate', methods=['POST','GET'])
def resultser():
    nnames = []
    if request.method == "POST":
        f = request.files["ff"]
        filename = 'static/audio' + f.filename
        f.save(filename)
        s = Separate(filename, f.filename.replace(".wav",""))
        nnames = s.filenames
    return render_template('results.html.j2', filenames = nnames)


@app.route('/amplify', methods=["POST"])
def results(): 
    vocals = request.values.get("vocals")
    amplify("vocals.wav", float(vocals))
    combine("output.wav", "accompaniment.wav")
    return render_template("results.html.j2", vocals=vocals)

#Login
@app.route('/login', methods=['GET', 'POST']) 
def login(): 
    if request.method=="GET": 
        return render_template("login.html.j2")
    elif request.method=="POST": 
        cursor=mysql.connection.cursor() 
        userput=request.values.get("username") 
        passput=request.values.get("paswd") 
        passwdsha=hashlib.sha256(passput.encode('utf-8')).hexdigest()
        query="SELECT * FROM audiocenter_users WHERE username=%s AND password=%s"
        queryVars=(userput, passwdsha)
        cursor.execute(query, queryVars) 
        mysql.connection.commit() 
        data=cursor.fetchall()
        if len(data) > 0: 
            session["username"]=userput
            return redirect(url_for("input"))
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
        cursor=mysql.connection.cursor() 
        paswdsha=hashlib.sha256(paswd.encode('utf-8')).hexdigest()
        query="SELECT * FROM audiocenter_users WHERE username=%s"
        queryVars=(username,)
        cursor.execute(query, queryVars) 
        mysql.connection.commit() 
        data=cursor.fetchall()
        if len(data)==0:
            paswdsha=hashlib.sha256(paswd.encode('utf-8')).hexdigest()
            query="INSERT INTO audiocenter_users VALUES (NULL, %s, %s);"
            queryVars=(username, paswdsha)
            cursor.execute(query, queryVars)
            mysql.connection.commit() 
            return redirect(url_for("login"))
        else:
            query="SELECT * FROM audiocenter_users"
            cursor.execute(query) 
            mysql.connection.commit() 
            data=cursor.fetchall()
            return render_template("signup.html.j2", invalid=True)

@app.route('/input') 
def input():
    return render_template("base.html.j2")