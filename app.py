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

@app.route('/results', methods=['POST','GET'])
def results():
    filenames = []
    if request.method == "POST":
        f = request.files["ff"]
        t = time.localtime()
        #filename = '/static/audio/' + f.filename + ' [' + str(int(time.time())) + ']'
        filename = 'static/audio/' + f.filename.split('.')[0] + ' [' + str(int(time.time())) + '].' + f.filename.split('.')[1]
        f.save(filename)
        if request.values.get("type") == "spleeter":
            filenames = AudioTools.split(filename, 'static/output/', 2)
        elif request.values.get("type") == "amplify":
            filenames = AudioTools.amplify(filename, 'static/output',4)
        elif request.values.get("type") == "keychange":
            filenames = AudioTools.keyChange(filename, 'static/output', 4)
    return render_template('results.html.j2', filenames = filenames)