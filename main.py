import os
import telebot
import pymongo
from flask import Flask, render_template, request, redirect, url_for
from threading import Thread

# --- SƏNİN MƏLUMATLARIN (YENİLƏNDİ) ---
TOKEN = "8682822347:AAEGrzVzv495LwTcGA85sCl5CbxhOsNRv7Q" # Yeni token
# MongoDB Atlas bağlantısı (Şifrə və link tam yerləşdirildi)
MONGO_URI = "mongodb+srv://admin:PoI5dlpwD3T4weFC@cluster0.vpwiifj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Verilənlər bazasına qoşulma
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["ecopix_db"]
    video_col = db["videos"]
    settings_col = db["settings"]
except Exception as e:
    print(f"Bazaya qoşulma xətası: {e}")
    video_col = []
    settings_col = None

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
bot = telebot.TeleBot(TOKEN)

# --- VEB SAYT FUNKSİYALARI ---

@app.route('/')
def index():
    # Videoları və reklam kodunu bazadan çək
    all_videos = list(video_col.find()) if hasattr(video_col, 'find') else []
    ad_data = settings_col.find_one({"type": "ad_code"}) if settings_col else None
    current_ad = ad_data['code'] if ad_data else ""
    return render_template('index.html', videos=all_videos, ad_code=current_ad)

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        new_ad = request.form.get('ad_html')
        if settings_col:
            settings_col.update_one({"type": "ad_code"}, {"$set": {"code": new_ad}}, upsert=True)
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/profile')
def profile():
    all_videos = list(video_col.find()) if hasattr(video_col, 'find') else []
    return render_template('profile.html', videos=all_videos)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# --- TELEGRAM BOT FUNKSİYALARI ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🌟 EcoPix-ə xoş gəldiniz!\n\nVideo göndərin, biz onu saytda paylaşaq. Reklam yerləşdirmək üçün saytın admin panelindən istifadə edin.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    # Telegram-dan gələn videonu bazaya yazırıq
    file_info = bot.get_file(message.video.file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    
    video_data = {
        "video_url": file_url,
        "username": message.from_user.username or "Anonim",
        "user_id": message.from_user.id
    }
    
    if hasattr(video_col, 'insert_one'):
        video_col.insert_one(video_data)
        bot.reply_to(message, "✅ Videonuz qəbul edildi və saytın ana səhifəsinə əlavə olundu!")
    else:
        bot.reply_to(message, "❌ Baza xətası! Video yadda saxlanılmadı.")

# --- SERVERİN İŞƏ SALINMASI ---

def run_flask():
    # Render üçün port 10000 olaraq qalır
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot.polling(none_stop=True)
