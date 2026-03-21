import os
import sqlite3
import telebot
import threading
from flask import Flask, request, jsonify, render_template_string

TOKEN = os.environ.get("TOKEN") or "TOKEN"
ADMIN_ID = 5073661002

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# DATABASE
conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, stars INT)")
c.execute("CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, caption TEXT, views INT, likes INT, owner TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS saved (user TEXT, video_id INT)")
c.execute("CREATE TABLE IF NOT EXISTS messages (sender TEXT, receiver TEXT, text TEXT)")
conn.commit()

# MAIN HTML
HTML = """
<body style="background:black;color:white">

<h3>EcoPix</h3>

<input id="u" placeholder="Ad">
<button onclick="login()">Login</button>
<button onclick="profile()">Profil</button>

<hr>

<h3>Mesaj</h3>
<input id="to" placeholder="Kimə">
<input id="msg" placeholder="Mesaj">
<button onclick="send()">Göndər</button>

<hr>

<div id="feed"></div>

<script>
let user=""

function login(){
 user=document.getElementById("u").value
 fetch("/login",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({user})})
}

function profile(){
 fetch("/profile",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({user})})
 .then(r=>r.json()).then(d=>{
  alert("⭐ "+d.stars+" | Saved "+d.saved)
 })
}

function send(){
 let to=document.getElementById("to").value
 let text=document.getElementById("msg").value
 fetch("/send",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({user,to,text})})
}

function view(id){
 fetch("/view/"+id)
}

function like(id){
 fetch("/like",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({id})})
}

function save(id){
 fetch("/save",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({id,user})})
}

function load(){
 fetch("/videos").then(r=>r.json()).then(v=>{
  let h=""
  v.forEach(x=>{
   h+=`
   <div style="margin-bottom:30px">
   <video src="${x.url}" width="300" controls autoplay onplay="view(${x.id})"></video>
   <p>${x.caption}</p>
   👁 ${x.views} ❤️ ${x.likes}
   <br>
   <button onclick="like(${x.id})">❤️ Like</button>
   <button onclick="save(${x.id})">💾 Save</button>
   </div>`
  })
  document.getElementById("feed").innerHTML=h
 })
}

load()
</script>
"""

# ADMIN HTML
ADMIN_HTML = """
<body style="background:black;color:white">
<h2>ADMIN PANEL</h2>
<div id="data"></div>

<script>
fetch("/admin_data").then(r=>r.json()).then(d=>{
 let h="<h3>Videolar</h3>"
 d.videos.forEach(v=>{
  h+=`ID:${v.id} 👁${v.views} ❤️${v.likes}<br>
  <button onclick="del(${v.id})">❌ Sil</button><hr>`
 })

 h+="<h3>Userlər</h3>"
 d.users.forEach(u=>{
  h+=`${u.username} ⭐${u.stars}<br>
  <button onclick="add('${u.username}')">+10⭐</button><hr>`
 })

 document.getElementById("data").innerHTML=h
})

function del(id){
 fetch("/delete_video",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({id})})
 location.reload()
}

function add(u){
 fetch("/add_star",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({user:u})})
 location.reload()
}
</script>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

# ADMIN
@app.route("/admin")
def admin():
    key = request.args.get("key")
    if str(key) != str(ADMIN_ID):
        return "Giriş qadağandır"
    return render_template_string(ADMIN_HTML)

@app.route("/admin_data")
def admin_data():
    c.execute("SELECT * FROM videos")
    videos = [{"id":r[0],"views":r[3],"likes":r[4]} for r in c.fetchall()]

    c.execute("SELECT * FROM users")
    users = [{"username":r[0],"stars":r[1]} for r in c.fetchall()]

    return jsonify({"videos":videos,"users":users})

@app.route("/delete_video", methods=["POST"])
def delete_video():
    vid = request.json["id"]
    c.execute("DELETE FROM videos WHERE id=?",(vid,))
    conn.commit()
    return "ok"

@app.route("/add_star", methods=["POST"])
def add_star():
    u = request.json["user"]
    c.execute("UPDATE users SET stars=stars+10 WHERE username=?",(u,))
    conn.commit()
    return "ok"

# LOGIN
@app.route("/login", methods=["POST"])
def login():
    u = request.json["user"]
    c.execute("INSERT OR IGNORE INTO users VALUES (?,?)",(u,0))
    conn.commit()
    return "ok"

# PROFILE
@app.route("/profile", methods=["POST"])
def profile():
    u = request.json["user"]

    c.execute("SELECT stars FROM users WHERE username=?",(u,))
    stars = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM saved WHERE user=?",(u,))
    saved = c.fetchone()[0]

    return jsonify({"stars":stars,"saved":saved})

# VIDEOS
@app.route("/videos")
def videos():
    c.execute("SELECT * FROM videos")
    rows = c.fetchall()

    res=[]
    for r in rows:
        res.append({"id":r[0],"url":r[1],"caption":r[2],"views":r[3],"likes":r[4]})
    return jsonify(res)

# VIEW + QAZANC
@app.route("/view/<int:id>")
def view(id):
    c.execute("UPDATE videos SET views=views+1 WHERE id=?",(id,))
    c.execute("SELECT views, owner FROM videos WHERE id=?",(id,))
    views, owner = c.fetchone()

    if views % 3000 == 0:
        c.execute("UPDATE users SET stars=stars+10 WHERE username=?",(owner,))
    conn.commit()
    return "ok"

# LIKE
@app.route("/like", methods=["POST"])
def like():
    vid = request.json["id"]
    c.execute("UPDATE videos SET likes=likes+1 WHERE id=?",(vid,))
    conn.commit()
    return "ok"

# SAVE
@app.route("/save", methods=["POST"])
def save():
    user = request.json["user"]
    vid = request.json["id"]
    c.execute("INSERT INTO saved VALUES (?,?)",(user,vid))
    conn.commit()
    return "ok"

# CHAT
@app.route("/send", methods=["POST"])
def send():
    u = request.json["user"]
    to = request.json["to"]
    text = request.json["text"]

    c.execute("INSERT INTO messages VALUES (?,?,?)",(u,to,text))
    conn.commit()
    return "ok"

# TELEGRAM VIDEO
@bot.message_handler(content_types=['video'])
def video(m):
    username = str(m.from_user.id)

    c.execute("INSERT OR IGNORE INTO users VALUES (?,?)",(username,0))

    file = bot.get_file(m.video.file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

    c.execute("INSERT INTO videos(url,caption,views,likes,owner) VALUES (?,?,0,0,?)",
              (url, m.caption or "Video", username))
    conn.commit()

    bot.reply_to(m,"Video əlavə olundu")

# RUN
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
