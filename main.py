import os
import telebot
import threading
from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
from bson.objectid import ObjectId

TOKEN = os.environ.get("TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")

bot = telebot.TeleBot(TOKEN)
app = Flask(name)

client = MongoClient(MONGO_URI)
db = client["ecopix"]

users = db.users
videos = db.videos
follows = db.follows
comments = db.comments

HTML = """

<!DOCTYPE html><html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{margin:0;background:black;color:white;font-family:sans-serif;overflow:hidden}
.video{height:100vh;display:flex;justify-content:center;align-items:center;position:relative}
video{height:100vh}
.actions{position:absolute;right:10px;bottom:80px}
button{display:block;margin:10px;font-size:18px}
.nav{position:fixed;bottom:0;width:100%;background:#111;display:flex;justify-content:space-around;padding:10px}
</style>
</head><body><div id="feed"></div><div class="nav">
<button onclick="load()">🏠</button>
<button onclick="upload()">➕</button>
<button onclick="profile()">👤</button>
</div><script>
let user = prompt("Username yaz")

function load(){
 fetch("/videos").then(r=>r.json()).then(v=>{
  let h=""
  v.forEach(x=>{
   h+=`
   <div class="video">
    <video src="${x.url}" autoplay loop onclick="view('${x.id}')"></video>

    <div class="actions">
     <button onclick="like('${x.id}')">❤️ ${x.likes}</button>
     <button onclick="comment('${x.id}')">💬</button>
     <button onclick="follow('${x.owner}')">👤+</button>
    </div>
   </div>`
  })
  document.getElementById("feed").innerHTML=h
 })
}

function like(id){
 fetch("/like",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({id})})
 load()
}

function view(id){
 fetch("/view/"+id)
}

function comment(id){
 let t = prompt("Rəy yaz")
 fetch("/comment",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({id,text:t,user})})
}

function follow(u){
 fetch("/follow",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({user,follow:u})})
}

function upload(){
 let url = prompt("Video link (mp4)")
 let caption = prompt("Başlıq")
 fetch("/upload",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({url,caption,user})})
}

function profile(){
 fetch("/profile",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({user})})
 .then(r=>r.json()).then(d=>{
  alert("⭐ "+d.stars+" | Videolar "+d.videos)
 })
}

load()
</script></body>
</html>
"""@app.route("/")
def home():
return render_template_string(HTML)

@app.route("/videos")
def vids():
res=[]
for v in videos.find().sort("_id",-1):
res.append({
"id":str(v["_id"]),
"url":v["url"],
"likes":v.get("likes",0),
"owner":v["owner"]
})
return jsonify(res)

@app.route("/upload", methods=["POST"])
def upload():
d = request.json
videos.insert_one({
"url":d["url"],
"caption":d["caption"],
"likes":0,
"views":0,
"owner":d["user"]
})
return "ok"

@app.route("/like", methods=["POST"])
def like():
id = request.json["id"]
videos.update_one({"_id":ObjectId(id)},{"$inc":{"likes":1}})
return "ok"

@app.route("/view/<id>")
def view(id):
v = videos.find_one({"_id":ObjectId(id)})
videos.update_one({"_id":ObjectId(id)},{"$inc":{"views":1}})

if v["views"] % 3000 == 0:
    users.update_one({"username":v["owner"]},{"$inc":{"stars":10}})

return "ok"

@app.route("/comment", methods=["POST"])
def comm():
comments.insert_one(request.json)
return "ok"

@app.route("/follow", methods=["POST"])
def fol():
follows.insert_one(request.json)
return "ok"

@app.route("/profile", methods=["POST"])
def prof():
u = request.json["user"]
vcount = videos.count_documents({"owner":u})

user = users.find_one({"username":u}) or {"stars":0}

return jsonify({"stars":user.get("stars",0),"videos":vcount})

@bot.message_handler(content_types=['video'])
def tg_video(m):
file = bot.get_file(m.video.file_id)
url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

videos.insert_one({
    "url":url,
    "caption":m.caption or "Video",
    "likes":0,
    "views":0,
    "owner":str(m.from_user.id)
})

bot.reply_to(m,"Video əlavə olundu")

def run_bot():
bot.infinity_polling()

if name == "main":
threading.Thread(target=run_bot).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
