import os
import telebot
import multiprocessing
from flask import Flask, render_template_string, request, jsonify

TOKEN = os.environ.get("TOKEN") or "8762924552:AAGLDCtEuj7YVMOdTdlqtRO5uyljws3XHGo"
ADMIN_ID = 5073661002

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# DATABASE
videos = []
users = {}

# HTML
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EcoPix</title>

<style>
body{margin:0;background:black;color:white;font-family:sans-serif}
.video{height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center}
video{height:70vh}
button{padding:8px;margin:3px}
.top{position:fixed;top:10px;left:10px}
</style>

</head>
<body>

<div class="top">
<input id="user" placeholder="Ad yaz">
<button onclick="login()">Login</button>
<button onclick="profile()">Profil</button>
</div>

<div id="feed"></div>

<script>
let videos=[]
let user=""

function login(){
 user=document.getElementById("user").value
 fetch("/login",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({user})})
 alert("Login olundu")
}

function profile(){
 fetch("/profile",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({user})})
 .then(r=>r.json()).then(d=>{
  alert("Saved video sayı: "+d.saved.length)
 })
}

fetch("/get_videos").then(r=>r.json()).then(d=>{
 videos=d
 show()
})

function show(){
 let html=""
 videos.forEach((v,i)=>{
  html+=`
  <div class="video">
    <video src="${v.url}" controls autoplay loop></video>
    <div>${v.caption}</div>
    <div>👁 ${v.views} | ❤️ ${v.likes}</div>
    
    <button onclick="like(${i})">❤️ Like</button>
    <button onclick="comment(${i})">💬 Comment</button>
    <button onclick="save(${i})">💾 Save</button>
  </div>`
 })
 document.getElementById("feed").innerHTML=html
}

function like(i){
 fetch("/like",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({i})})
 .then(()=>location.reload())
}

function comment(i){
 let text=prompt("Şərh yaz")
 fetch("/comment",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({i,text})})
 .then(()=>alert("Yazıldı"))
}

function save(i){
 fetch("/save",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({i,user})})
 .then(()=>alert("Saved"))
}
</script>

</body>
</html>
"""

# ROUTES
@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/get_videos")
def get_videos():
    return jsonify(videos)

# PROFIL LOGIN
@app.route("/login", methods=["POST"])
def login():
    user = request.json["user"]
    if user not in users:
        users[user] = {"saved": []}
    return "ok"

# PROFIL DATA
@app.route("/profile", methods=["POST"])
def profile():
    user = request.json["user"]
    return jsonify(users.get(user, {"saved": []}))

# SAVE VIDEO
@app.route("/save", methods=["POST"])
def save():
    user = request.json["user"]
    i = request.json["i"]
    if user in users:
        users[user]["saved"].append(i)
    return "ok"

# LIKE
@app.route("/like", methods=["POST"])
def like():
    i = request.json["i"]
    videos[i]["likes"] += 1
    return "ok"

# COMMENT
@app.route("/comment", methods=["POST"])
def comment():
    i = request.json["i"]
    text = request.json["text"]
    videos[i]["comments"].append(text)
    return "ok"

# TELEGRAM
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Video göndər → sayta düşəcək 🚀")

@bot.message_handler(commands=['admin'])
def admin(m):
    if m.from_user.id != ADMIN_ID:
        return
    
    for i,v in enumerate(videos):
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("❌ Sil", callback_data=f"del_{i}"))
        bot.send_message(m.chat.id, f"{i+1}. {v['caption']}", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("del_"))
def delete(c):
    if c.from_user.id != ADMIN_ID:
        return
    
    i = int(c.data.split("_")[1])
    if i < len(videos):
        videos.pop(i)
        bot.answer_callback_query(c.id, "Silindi")

# VIDEO
@bot.message_handler(content_types=['video'])
def video(m):
    try:
        file = bot.get_file(m.video.file_id)
        url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
        
        videos.append({
            "url": url,
            "caption": m.caption or "Video",
            "likes": 0,
            "views": 0,
            "comments": []
        })
        
        bot.reply_to(m, "Paylaşıldı ✅")
        
    except:
        bot.reply_to(m, "Xəta ❌")

# VIEW
@app.before_request
def count_views():
    if request.path == "/":
        for v in videos:
            v["views"] += 1

# SERVER
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    p = multiprocessing.Process(target=run_web)
    p.start()
    print("EcoPix FULL işləyir 🚀")
    run_bot()
