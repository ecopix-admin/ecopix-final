import os, asyncio, sqlite3
from flask import Flask, request, jsonify, render_template_string
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from threading import Thread

# --- KONFİQURASİYA ---
TOKEN = "8762924552:AAHGnprnWn4x7mnqnjZRQA-h0NfGXhNt0bI"
ADMIN_ID = 5073661002  # Sənin yeni təqdim etdiyin ID
WEB_URL = os.getenv("WEB_URL", "https://google.com")
DB_NAME = "ecopix_v3_final.db"

app = Flask(__name__)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, name TEXT, lang TEXT, notify INT DEFAULT 1)")
    c.execute("CREATE TABLE IF NOT EXISTS videos(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, file_id TEXT, is_ad INT DEFAULT 0, likes INT DEFAULT 0)")
    conn.commit()
    conn.close()

# --- HÜQUQİ QORUNMA MƏTNİ ---
LEGAL_TEXT = {
    "az": "⚖️ **Məxfilik və Məsuliyyət**\n\n1. Yüklənən hər bir videoya görə istifadəçi məsuliyyət daşıyır.\n2. Qanunsuz məzmunlar dərhal silinəcək.\n3. Eco Pix platforması yalnız vasitəçidir.",
    "ru": "⚖️ **Конфиденциальность**\n\n1. Пользователь несет ответственность за загруженное видео.\n2. Незаконный контент будет удален.\n3. Eco Pix является лишь посредником.",
    "en": "⚖️ **Privacy & Legal**\n\n1. Users are responsible for their uploaded content.\n2. Illegal content will be removed immediately.\n3. Eco Pix is only a platform provider."
}

# --- FRONTEND (TIKTOK STYLE) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #000; color: #fff; font-family: sans-serif; overflow: hidden; }
        .feed { height: 100vh; overflow-y: scroll; snap-type: y mandatory; scroll-behavior: smooth; }
        .card { height: 100vh; snap-align: start; position: relative; display: flex; align-items: center; justify-content: center; }
        video { width: 100%; height: 100%; object-fit: cover; }
        .side-bar { position: absolute; right: 15px; bottom: 120px; display: flex; flex-direction: column; gap: 20px; align-items: center; z-index: 10; }
        .btn-act { width: 55px; height: 55px; background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; }
    </style>
</head>
<body>
    <div class="feed" id="feed-container"></div>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script>
        let tg = window.Telegram.WebApp;
        async function load() {
            let res = await fetch('/api/videos');
            let data = await res.json();
            document.getElementById('feed-container').innerHTML = data.map(v => `
                <div class="card">
                    <video loop src="/video/${v.file_id}" onclick="this.paused?this.play():this.pause()"></video>
                    <div class="side-bar">
                        <div class="btn-act">❤️</div>
                        <div class="btn-act" onclick="tg.openLink('https://wa.me/?text=Bax!')">🔗</div>
                    </div>
                </div>
            `).join('');
        }
        load();
    </script>
</body>
</html>
"""

# --- BOT HANDLERS ---
@dp.message(CommandStart())
async def start(m: types.Message):
    lang = m.from_user.language_code if m.from_user.language_code in ["az", "ru", "en"] else "en"
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id, name, lang) VALUES (?, ?, ?)", (str(m.from_user.id), m.from_user.first_name, lang))
    conn.commit(); conn.close()
    
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Eco Pix Aç 📱", web_app=WebAppInfo(url=WEB_URL))],
        [KeyboardButton(text="⚙️ Ayarlar"), KeyboardButton(text="⚖️ Məxfilik")]
    ], resize_keyboard=True)
    await m.answer(f"Xoş gəldin {m.from_user.first_name}!", reply_markup=kb)

@dp.message(F.text == "⚖️ Məxfilik")
async def show_legal(m: types.Message):
    lang = m.from_user.language_code if m.from_user.language_code in LEGAL_TEXT else "en"
    await m.answer(LEGAL_TEXT[lang], parse_mode="Markdown")

@dp.message(F.video)
async def upload(m: types.Message):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO videos (user_id, file_id) VALUES (?, ?)", (str(m.from_user.id), m.video.file_id))
    conn.commit()
    
    users = c.execute("SELECT id FROM users WHERE notify = 1").fetchall()
    for u in users:
        try:
            if u[0] != str(m.from_user.id):
                await bot.send_message(u[0], "🔥 Yeni video! Eco Pix-ə daxil ol.")
        except: continue
    conn.close()
    await m.answer("Paylaşıldı! ✅")

# --- SERVER & API ---
@app.route("/")
def home(): return render_template_string(HTML_TEMPLATE)

@app.route("/api/videos")
def vids():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    res = c.execute("SELECT user_id, file_id, is_ad, likes FROM videos ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"user_id":r[0], "file_id":r[1], "is_ad":r[2], "likes":r[3]} for r in res])

@app.route("/video/<file_id>")
async def stream(file_id):
    file = await bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

if __name__ == "__main__":
    init_db()
    Thread(target=lambda: asyncio.run(dp.start_polling(bot)), daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
