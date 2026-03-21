import os
import sqlite3
import telebot
import threading
from flask import Flask, request, jsonify, render_template_string

TOKEN = os.environ.get("TOKEN") or "8762924552:AAGenxs765-lHcljpclwNSFx-DvRBJAWPY0"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# DATABASE
conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, stars INT)")
c.execute("CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, caption TEXT, views INT)")
c.execute("CREATE TABLE IF NOT EXISTS saved (user TEXT, video_id INT)")
c.execute("CREATE TABLE IF NOT EXISTS messages (sender TEXT, receiver TEXT, text TEXT)")
conn.commit()

# HTML
HTML = """
<body style="background:black;color:white">

<input id="u" placeholder="Ad">
<button onclick="login()">Login</button>
<button onclick="profile()">Profil</button>

<hr>

<h3>Chat</h3>
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
  alert("⭐ Ulduz: "+d.stars+" | Saved: "+d.saved)
 })
}

function send(){
 let to=document.getElementById("to").value
 let text=document.getElementById("msg").value
 fetch("/send",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({user,to,text})})
}

function load(){
 fetch("/videos").then(r=>r.json()).then(v=>{
  let h=""
  v.forEach(x=>{
   h+=`
   <div>
   <video src="${x.url}" width="300" controls autoplay></video>
   <p>${x.caption}</p>
   👁 ${x.views}
   </div>`
  })
  document.getElementById("feed").innerHTML=h
 })
}

load()
</script>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

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
        res.append({"id":r[0],"url":r[1],"caption":r[2],"views":r[3]})
    return jsonify(res)

# VIEW + QAZANC
@app.route("/view/<int:id>")
def view(id):
    c.execute("UPDATE videos SET views=views+1 WHERE id=?",(id,))
    
    # hər 3000 view = 10 star
    c.execute("SELECT views FROM videos WHERE id=?",(id,))
    views = c.fetchone()[0]

    if views % 3000 == 0:
        # video sahibinə ulduz vermək (sadə versiya)
        c.execute("UPDATE users SET stars=stars+10")
    
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
    file = bot.get_file(m.video.file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

    c.execute("INSERT INTO videos(url,caption,views) VALUES (?,?,0)",
              (url, m.caption or "Video"))
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
