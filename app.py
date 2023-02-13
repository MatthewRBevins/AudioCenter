from flask import Flask, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from flask_mysqldb import MySQL
app = Flask(__name__)
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
import os
class Separate():
    def __init__(self, file, actualname):
        separator = Separator('spleeter:2stems')
        audio_loader = AudioAdapter.default()
        sample_rate = 44100
        waveform, _ = audio_loader.load(file, sample_rate=sample_rate)
        separator.separate_to_file(file, 'statiwc/output')
        self.filenames = ['static/output/' + actualname + '/accompaniment.wav', 'static/output/' + actualname + '/vocals.wav']

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

@app.route('/results', methods=['POST','GET'])
def results():
    nnames = []
    if request.method == "POST":
        f = request.files["ff"]
        filename = 'static/audio' + f.filename
        f.save(filename)
        s = Separate(filename, f.filename.replace(".wav",""))
        nnames = s.filenames
    return render_template('results.html.j2', filenames = nnames)