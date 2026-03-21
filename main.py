import os
import sqlite3
import telebot
import threading
from flask import Flask, request, jsonify, render_template_string

# --- AYARLAR ---
TOKEN = "8682822347:AAEGrzVzv495LwTcGA85sCl5CbxhOsNRv7Q"
ADMIN_ID = 5073661002

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- DATABASE ---
def get_db_connection():
    conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
    return conn

conn = get_db_connection()
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, stars INT)")
c.execute("CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS saved (user TEXT, video_id INT)")
c.execute("CREATE TABLE IF NOT EXISTS messages (sender TEXT, receiver TEXT, text TEXT)")
conn.commit()

# --- MAIN HTML ---
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>EcoPix</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: black; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
        .video-card { border: 1px solid #333; margin: 10px; padding: 10px; border-radius: 10px; }
        video { width: 100%; border-radius: 5px; }
        button { background: #007bff; color: white; border: none; padding: 10px; margin: 5px; cursor: pointer; border-radius: 5px; }
        input { padding: 10px; margin: 5px; width: 80%; border-radius: 5px; border: 1px solid #333; background: #222; color: white; }
    </style>
</head>
<body>
    <h3>EcoPix | Premium Content</h3>
    <hr>
    <div id="feed"></div>

    <script>
        async function loadVideos() {
            const res = await fetch('/api/videos');
            const videos = await res.json();
            const feed = document.getElementById('feed');
            feed.innerHTML = '';
            videos.reverse().forEach(v => {
                feed.innerHTML += `
                    <div class="video-card">
                        <video controls src="${v.url}"></video>
                    </div>`;
            });
        }
        loadVideos();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/videos')
def get_videos():
    c.execute("SELECT url FROM videos")
    rows = c.fetchall()
    return jsonify([{"url": r[0]} for r in rows])

# --- BOT COMMANDS ---
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Xoş gəldin! Video göndər, saytda paylaşılsın. 🚀")

@bot.message_handler(content_types=['video'])
def handle_video(m):
    file_info = bot.get_file(m.video.file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    
    c.execute("INSERT INTO videos (url) VALUES (?)", (url,))
    conn.commit()
    bot.reply_to(m, "Video uğurla sayta əlavə edildi! ✅\nBax: https://ecopix-final.onrender.com")

# --- RUN ---
def run_bot():
    try:
        print("Bot başladılır...")
        bot.infinity_polling()
    except Exception as e:
        print(f"Bot xətası: {e}")

if __name__ == "__main__":
    # Botu ayrı mövzuda (thread) başlat
    threading.Thread(target=run_bot, daemon=True).start()
    # Flask-ı əsas mövzuda başlat
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
