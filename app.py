from flask import Flask, render_template, request, redirect, session, url_for
import hashlib
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from flask_mysqldb import MySQL  
import numpy as np
import json
# FOR SERVER
#import public.AudioCenter.AudioCenter.AudioTools
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
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True
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
        data = executeQuery("SELECT joined,pfp,bio,place,website,id FROM audiocenter_users u WHERE username=%s", (self.username,))
        following = executeQuery("SELECT username FROM audiocenter_users u JOIN audiocenter_followers f ON f.follower_id=%s WHERE u.id=f.following_id;", (data[0]["id"],))
        followers = executeQuery("SELECT username FROM audiocenter_users u JOIN audiocenter_followers f ON f.following_id=%s WHERE u.id=f.follower_id;", (data[0]["id"],))
        if len(data) > 0:
            self.followers = followers
            self.following = following
            self.joined = data[0]["joined"]
            self.pfp = data[0]["pfp"]
            self.bio = data[0]["bio"]
            self.place = data[0]["place"]
            self.website = data[0]["website"]
            self.id = data[0]["id"]
        else:
            self.followers = None
            self.following = None
            self.joined = None
            self.pfp = None
            self.bio = None
            self.place = None
            self.website = None
            self.id = None
    def createDict(self):
        keys = ["username", "loggedIn", "followers", "following", "joined", "pfp", "bio", "place", "website", "id"]
        values = [self.username, self.loggedIn, self.followers, self.following, self.joined, self.pfp, self.bio, self.place, self.website, self.id]
        data = list(zip(keys, values))
        d = {k: v for k, v in data}
        return d

def getPosts(currentUser, userToShow):
    data = executeQuery("SELECT * FROM audiocenter_posts WHERE author_id=%s", (userToShow.id,))
    return data

def verifySessions():
    print("VERIFY SESSIONS")
    #Update this when adding new session vars
    #session["userData"]["loggedIn"] = True
    try:
        session["userData"]
    except KeyError:
        session["userData"] = userData("guest", False).createDict()
    try:
        session["filename"]
    except KeyError:
        session["filename"] = None
    try:
        session["detect"]
    except KeyError:
        session["detect"] = None
    try:
        session["convert"]
    except KeyError:
        session["convert"] = None
    print("DONE")

@app.route('/')
def index():
    verifySessions()
    res = []
    if session["userData"]["loggedIn"]:
        if request.values.get('posttype') == '0':
            res = genPosts('0', 0, None, 1)
        else:
            res = genPosts('1', 0, None, 0)
    return render_template('index.html.j2', userData=session["userData"], posts=res, posttype=request.values.get('posttype'))

@app.route('/detect', methods=["GET","POST"])
def detect():
    verifySessions()
    output = None
    out = dict() 
    error = ''
    if request.method == "POST":
        print("HI")
        f = request.files["file"]
        t = str(int(time.time()))   
        try:
            os.mkdir('static/audio/' + session["userData"]["username"] + '/detect')
        except:
            pass
        filename = 'static/audio/' + session["userData"]["username"] + '/detect/' + f.filename.split('.')[0] + ' [' + t + '].' + f.filename.split('.')[1]
        f.save(filename) 
        session["detect"] = filename
        originalFilename = session["detect"] 
        t = str(int(time.time()))
        try:
            os.mkdir('static/audio/' + session["userData"]["username"] + '/detect/trimmed/')
        except:
            pass
        trimmedFilename = 'static/audio/' + session["userData"]["username"] + '/detect/trimmed/' + f.filename.split('.')[0] + ' [' + t + '].wav'
        proxy = open(trimmedFilename, "w")
        try:
            AudioTools.trimSong(session["detect"], trimmedFilename)
        except:
            error = 'Oops! File format not supported.'
        session["detect"] = trimmedFilename
        try:
            output = AudioTools.detectSong(session["detect"])
        except:
            error = 'Oops! File format not supported.'
        out["type"] = "detect"
        session["detect"] = originalFilename
        out["output"] = output
        if output == None and error == '':
            error = 'Oops! Song not detected.'
    return render_template('detect.html.j2', fn=session["detect"], userData=session["userData"], out=out, error=error)

@app.route('/convert', methods=["GET","POST"])
def convert():
    verifySessions()
    output = None
    out = dict() 
    basename = ""
    error = ''
    validExtensions = ["m4a", "mp3"]
    if request.method == "POST":                        
        f = request.files["file"]
        extension = os.path.splitext(f.filename)[1].lower()
        print(extension)
        t = str(int(time.time()))   
        try:
            os.mkdir('static/audio/' + session["userData"]["username"] + '/convert')
        except:
            pass
        filename = 'static/audio/' + session["userData"]["username"] + '/convert/' + f.filename.split('.')[0] + ' [' + t + '].' + f.filename.split('.')[1]
        try:
            f.save(filename) 
        except:
            pass
        session["convert"] = filename
        out["type"] = "convert"
        if extension.lower() != ".wav":
            converted = AudioTools.mp3towav(session["convert"])
            if converted[1] == 1:
                error = 'Oops! File format not supported.'
                out["output"] = session["convert"]
            else:
                out["output"] = converted[0]
        else:
            out["output"] = session["convert"]
        basename = os.path.basename(out["output"])
        
    return render_template('convert.html.j2', error=error, fn=session["convert"], userData=session["userData"], out=out, base=basename)

@app.route('/editor', methods=["GET", "POST"])
def editor():
    verifySessions()
    fileLength = 0
    output = []
    out = dict()
    error = ''
    print(session["filename"])
    if session["filename"] == None:
        session["filename"] = []
    if request.method == "POST":
        if request.values.get("form") == "1":
            track = request.values.get("track")
            f = request.files["file-open"]
            t = str(int(time.time()))   
            try:
                os.mkdir('static/audio/' + session["userData"]["username"] + '/raw')
            except:
                pass
            filename = 'static/audio/'  + session["userData"]["username"] + '/raw/' + f.filename.split('.')[0] + ' [' + t + '].' + f.filename.split('.')[1]
            f.save(filename) 
            try:
                fileLength = AudioTools.length(filename)
                if track == "new":
                    a = session["filename"]
                    a.append(filename)
                    session["filename"] = a
                    print(session["filename"])
                else:
                    session["filename"][int(track)] = filename
            except:
                error = "Oops! File format not supported."
                
        elif request.values.get("form") == "2":
            if session["filename"] != None:
                print(request.values)
                #effectStart = int(request.values.get('effectsStartPoint'))
                #effectEnd = int(request.values.get('effectsEndPoint'))
                #effectWidth = int(request.values.get('effectsTotalWidth'))

                if request.values.get("download"):
                    dt = request.values.get("download-type")
                    track = request.values.getlist("track")
                    downloads = []
                    for i in track:
                        downloads.append(session["filename"][int(i)])
                    if dt == 'm':
                        downloads = [AudioTools.combine(downloads, 'static/audio/' + session["userData"]["username"] + '/output/')]
                    return render_template('download.html.j2', downloads=downloads, next='editor')
                elif request.values.get("savepost"):
                    track = request.values.getlist("track")
                    try:
                        os.mkdir('static/audio/' + session["userData"]["username"] + '/save')
                    except:
                        pass
                    try:
                        os.mkdir('static/audio/' + session["userData"]["username"] + '/save/' + request.values.get("posttitle"))
                    except:
                        pass
                    trackFiles = []
                    for i in track:
                        trackFiles.append(session["filename"][int(i)])
                    trackfile = AudioTools.combine(trackFiles, 'static/audio/' + session["userData"]["username"] + '/output/')
                    executeQuery("INSERT INTO audiocenter_posts(author_id, title, body, visibility, filepath) VALUES(%s, %s, %s, %s, %s)", (session["userData"]["id"], request.values.get("posttitle"), request.values.get("postbody"), request.values.get("vis"), 'static/audio/' + session["userData"]["username"] + '/save/' + request.values.get("posttitle") + '/audio.wav'))
                    AudioTools.saveFile(trackfile, 'static/audio/' + session["userData"]["username"] + '/save/' + request.values.get("posttitle"))
                elif request.values.get("cut"):
                    s = request.values.get("selected").split(",")
                    selected = []
                    ii = 0
                    iii = 0
                    for i in s:
                        if ii == 0:
                            selected.append([])
                        selected[iii].append(float(i))
                        ii+=1
                        if ii == 3:
                            ii = 0
                            iii+=1
                    track = request.values.getlist("track")
                    for i in track:
                        AudioTools.makeCut(session["filename"][int(i)], selected[int(i)], 'delete')
                elif request.values.get("key-change"):
                    s = request.values.get("selected").split(",")
                    selected = []
                    ii = 0
                    iii = 0
                    for i in s:
                        if ii == 0:
                            selected.append([])
                        selected[iii].append(float(i))
                        ii+=1
                        if ii == 3:
                            ii = 0
                            iii+=1
                    track = request.values.getlist("track")
                    selectType = request.values.get("select-type")
                    steps = int(request.values.get("steps"))
                    out["type"] = "files"
                    try:
                        os.mkdir('static/audio/' + session["userData"]["username"] + '/output')
                    except:
                        pass
                    for i in track:
                        if selectType == 'f':
                            output = AudioTools.keyChange(session["filename"][int(i)], 'static/audio/' + session["userData"]["username"] + '/output/', steps)
                            session["filename"][int(i)] = output
                        elif selectType == 's':
                            output = AudioTools.makeCut(session["filename"][int(i)], selected[int(i)], 'key', steps)
                            session["filename"][int(i)] = output
                elif request.values.get("amplify"):
                    track = request.values.getlist("track")
                    factor = float(request.values.get("factorAmp"))
                    print("****************AMPLIFY")
                    out["type"] = "files"
                    try:
                        os.mkdir('static/audio/' + session["userData"]["username"] + '/output')
                    except:
                        pass
                    for i in track:
                        output = AudioTools.amplify(session["filename"][int(i)], 'static/audio/' + session["userData"]["username"] + '/output/', factor)
                        session["filename"][int(i)] = output
                elif request.values.get("split-tracks"):
                    track = request.values.getlist("track")
                    out["type"] = "files"
                    try:
                        os.mkdir('static/audio/' + session["userData"]["username"] + '/output')
                    except:
                        pass
                    for i in track:
                        output = AudioTools.split(session["filename"][int(i)], 'static/audio/' + session["userData"]["username"] + '/output/', 2)
                        a = session["filename"]
                        a[int(i)] = output[0]
                        a.insert(int(i)+1, output[1])
                        session["filename"] = a
                elif request.values.get("speed-change"):
                    s = request.values.get("selected").split(",")
                    selected = []
                    ii = 0
                    iii = 0
                    for i in s:
                        if ii == 0:
                            selected.append([])
                        selected[iii].append(float(i))
                        ii+=1
                        if ii == 3:
                            ii = 0
                            iii+=1
                    track = request.values.getlist("track")
                    selectType = request.values.get("select-type")
                    factor = float(request.values.get("factorSpeed"))
                    out["type"] = "files"
                    try:
                        os.mkdir('static/audio/' + session["userData"]["username"] + '/output')
                    except:
                        pass
                    for i in track:
                        if selectType == 'f':
                            output = AudioTools.changeSpeed(session["filename"][int(i)], 'static/audio/' + session["userData"]["username"] + '/output/', factor)
                            session["filename"][int(i)] = output
                        elif selectType == 's':
                            output = AudioTools.makeCut(session["filename"][int(i)], selected[int(i)], 'speed', factor)
                            session["filename"][int(i)] = output
                elif request.values.get("delete-track"):
                    track = request.values.get("track")
                    a = session["filename"]
                    del a[int(track)]
                    session["filename"] = a
            else:
                error = "Oops! You have not uploaded a file."
        if len(session["filename"]) > 4:
            session["filename"] = session["filename"][0:4]
            error = 'Oops! You have reached the limit of 4 tracks.'
    out["output"] = session["filename"]
    return render_template('editor.html.j2', t=request.method, out=out, error=error, userData=session["userData"], fileLength = fileLength)

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
    error = ''
    if not session["userData"]["loggedIn"]:
        return(redirect(url_for("login")))
    if request.method == "POST":
        if request.values.get("formnum") == "0":
            f = request.files["file-input"]
            filen = int(f.seek(0, os.SEEK_END))
            f.seek(0, os.SEEK_SET)
            if filen < 1000000:
                try:
                    os.mkdir('static/images/pfps/' + session["userData"]["username"])
                except:
                    pass
                filename = 'static/images/pfps/' + session["userData"]["username"] + '/pfp.png'
                f.save(filename)
                executeQuery("UPDATE audiocenter_users SET pfp=%s WHERE username=%s", (True,session["userData"]["username"]))
            else:
                error = 'Oops! File too large. Please uplaod a file smaller than 1 mb.'
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
                import validators
                if not validators.url(newWebsite):
                    error = 'Oops! Please enter a valid URL.'
                else:
                    executeQuery("UPDATE audiocenter_users SET website=%s WHERE username=%s", (newWebsite, session["userData"]["username"]))
    session["userData"] = userData(session["userData"]["username"], True).createDict()
    res = []
    spinoff = True
    dir_path = 'static/audio/' + session["userData"]["username"] + '/save'
    # Iterate directory
    res = genPosts('2', 0, session["userData"]["username"], 2)
    if len(res) > 0:
        spinoff = False
    return render_template('profile.html.j2', edit=True, userData=session["userData"], userToShowData=session["userData"], posts = res, path = dir_path, spinoff=spinoff, error=error)

#Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup(): 
    error = ''
    verifySessions()
    if request.method=="GET": 
        return render_template("signup.html.j2", userData=session["userData"]) 
    else: 
        #I am not doing server-side validation for the username and password because the request.values.get always returns a string, which can be hashed
        #If the user really wants to put their password as a color, that's fine
        username = request.values.get("username")
        paswd = request.values.get("paswd") 
        conf = request.values.get("confpaswd")
        if username == "" or paswd == "" or conf == "":
            error = 'Oops! Please fill in all fields.'
            return render_template("signup.html.j2", error=error, userData=session["userData"])
        if len(paswd) < 8:
            error = 'Oops! Password must be at least 8 characters.'
            return render_template("signup.html.j2", error=error, userData=session["userData"])
        if paswd != conf:
            error = 'Oops! Password must match confirmation.'
            return render_template("signup.html.j2", error=error, userData=session["userData"])
        paswdsha=hashlib.sha256(paswd.encode('utf-8')).hexdigest()
        data = executeQuery("SELECT * FROM audiocenter_users WHERE username=%s", (username,))
        if len(data)==0:
            paswdsha=hashlib.sha256(paswd.encode('utf-8')).hexdigest()
            date = datetime.datetime.now()
            date = date.strftime("%B %Y")
            os.mkdir('static/audio/' + username)
            executeQuery("INSERT INTO audiocenter_users(joined, username, password, bio, place, website) VALUES (%s, %s, %s, %s, %s, %s);", (date, username, paswdsha, "This user has not added a bio yet.", "Earth", ""))
            return redirect(url_for("login"))
        else:
            error = 'Oops! That username has been taken.'
            return render_template("signup.html.j2", error=error, userData=session["userData"])

@app.route('/@<userToShow>', methods = ["GET"])
def userShow(userToShow):
    data = executeQuery("SELECT * FROM audiocenter_users WHERE username=%s", (userToShow,))
    print("DATA:")
    if len(data) == 0:
        return render_template('index.html.j2', userData=session["userData"], error='Oops! User not found.')
    userToShowData = userData(userToShow, False).createDict()
    dir_path = 'static/audio/' + userToShow + '/save'
    if userToShow in session["userData"]["following"]:
        res = genPosts('2', 0, userToShow, 0)
    else:
        res = genPosts('2', 0, userToShow, 1)
    spinoff = True
    if len(res) > 0:
        spinoff = False
    return render_template('profile.html.j2', spinoff=False, edit=False, userData=session["userData"], userToShowData=userToShowData, posts=res)

@app.route('/signout', methods=['POST'])
def signout():
    session["userData"] = userData("guest", False).createDict()
    return redirect(url_for("index"))

@app.route('/follow', methods=['POST'])
def follow():
    if session["userData"]["loggedIn"]:
        followingID = request.values.get("following")
        l = executeQuery("SELECT * FROM audiocenter_followers WHERE follower_id=%s AND following_id=%s", (session["userData"]["id"], followingID))
        if len(l) == 0:
            executeQuery("INSERT INTO audiocenter_followers(follower_id, following_id) VALUES(%s, %s)", (session["userData"]["id"], followingID))
        else:
            executeQuery("DELETE FROM audiocenter_followers WHERE follower_id=%s AND following_id=%s", (session["userData"]["id"], followingID))
    return 'success'

@app.route('/like', methods=['POST'])
def like():
    print("&&&&&&&&&&&&&&&")
    print(request.values.get("postID"))
    diff = int(request.values.get("prev"))-int(request.values.get("likeOrDislike"))
    likes = int(executeQuery("SELECT likes FROM audiocenter_posts WHERE id=%s", (request.values.get("postID"),))[0]["likes"])
    dislikes = int(executeQuery("SELECT dislikes FROM audiocenter_posts WHERE id=%s", (request.values.get("postID"),))[0]["dislikes"])
    if diff == 2:
        print("LIKE TO DISLIKE")
        dislikes += 1
        likes -= 1
    if diff == 1:
        if int(request.values.get("prev")) == 0:
            print("NOTHING TO DISLIKE")
            dislikes += 1
        else:
            print("LIKE TO NOTHING")
            likes -= 1
    if diff == -1:
        if int(request.values.get("prev")) == 0:
            print("NOTHING TO LIKE")
            likes += 1
        else:
            print("DISLIKE TO NOTHING")
            dislikes -= 1
    if diff == -2:
        print("DISLIKE TO LIKE")
        likes += 1
        dislikes -= 1
    executeQuery("UPDATE audiocenter_posts SET likes=%s,dislikes=%s WHERE id=%s", (likes, dislikes, request.values.get("postID")))
    executeQuery("DELETE FROM audiocenter_likes WHERE post_id=%s AND user_id=%s", (request.values.get("postID"), session["userData"]["id"]))
    executeQuery("INSERT INTO audiocenter_likes(user_id, post_id, like_or_dislike) VALUES(%s, %s, %s)", (session["userData"]["id"], request.values.get("postID"), request.values.get("likeOrDislike")))
    return 'success'

@app.route('/genPosts', methods=['POST'])
def genPosts(postType, startIndex, username, perms):
    #perms = 0: public, perms = 1: followers only, perms = 2: private
    permLevels = [["public"], ["public", "followers"], ["public", "followers", "private"]]
    res = []
    #for you
    if postType == '0':
        ii = 0
        br = False
        for i in session["userData"]["following"]:
            userID = executeQuery("SELECT id FROM audiocenter_users WHERE username=%s", (i["username"],))
            post = executeQuery("SELECT * FROM audiocenter_posts p JOIN audiocenter_users u ON u.id=p.author_id WHERE p.author_id=%s ", (userID[0]["id"],))
            for i in post:
                liked = executeQuery("SELECT like_or_dislike FROM audiocenter_likes WHERE user_id=%s AND post_id=%s", (session["userData"]["id"], i["id"]))
                i["liked"] = 0
                if len(liked) != 0:
                    i["liked"] = liked[0]["like_or_dislike"]
                if ii >= startIndex and i["visibility"] in permLevels[perms]:
                    res.append(i)
                if len(res) == 10:
                    br = True
                    break
                ii += 1
            if br:
                break
    #specific username
    elif postType == '2':
        userID = executeQuery("SELECT id FROM audiocenter_users WHERE username=%s", (username,))
        post = executeQuery("SELECT * FROM audiocenter_posts p JOIN audiocenter_users u ON u.id=p.author_id WHERE p.author_id=%s ", (userID[0]["id"],))
        ii = 0
        for i in post:
            liked = executeQuery("SELECT like_or_dislike FROM audiocenter_likes WHERE user_id=%s AND post_id=%s", (session["userData"]["id"], i["id"]))
            i["liked"] = 0
            if len(liked) != 0:
                i["liked"] = liked[0]["like_or_dislike"]
            if ii >= startIndex and i["visibility"] in permLevels[perms]:
                res.append(i)
            if len(res) == 10:
                break
            ii += 1
    #trending
    else:
        post = executeQuery("SELECT * FROM audiocenter_posts p JOIN audiocenter_users u ON u.id=p.author_id ORDER BY likes DESC", ())
        ii = 0
        for i in post:
            liked = executeQuery("SELECT like_or_dislike FROM audiocenter_likes WHERE user_id=%s AND post_id=%s", (session["userData"]["id"], i["id"]))
            i["liked"] = 0
            if len(liked) != 0:
                i["liked"] = liked[0]["like_or_dislike"]
            if ii >= startIndex and i["visibility"] in permLevels[perms]:
                res.append(i)
            if len(res) == 10:
                break
            ii += 1
    return res