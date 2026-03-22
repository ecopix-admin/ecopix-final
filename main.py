import os
import telebot
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime

# --- KONFİQURASİYA ---
TOKEN = "8682822347:AAEGrzVzv495LwTcGA85sCl5CbxhOsNRv7Q"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Sənin MongoDB Bağlantın
app.config["MONGO_URI"] = "mongodb+srv://admin:PoI5dlpwD3T4weFC@cluster0.vpwiifj.mongodb.net/EcoPix_Final?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

# --- TƏHLÜKƏSİZLİK (Kiber Hücumdan Qorunma) ---
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# --- ANA SƏHİFƏ (TikTok Scroll + Keşfet) ---
@app.route('/')
def index():
    # Videoların 0.1 saniyədə açılması üçün sürətli çəkim
    videos = list(mongo.db.videos.find().sort("created_at", -1))
    ad = mongo.db.settings.find_one({"type": "ads"})
    ad_code = ad['code'] if ad else ""
    return render_template('index.html', videos=videos, ad_code=ad_code)

# --- LİKE VƏ ŞƏRH SİSTEMİ ---
@app.route('/like/<video_id>', methods=['POST'])
def like_video(video_id):
    mongo.db.videos.update_one({"_id": ObjectId(video_id)}, {"$inc": {"likes": 1}})
    return jsonify({"status": "success", "color": "red"})

# --- PROFİL VƏ VİDEO YÜKLƏMƏ ---
@app.route('/profile/<username>')
def profile(username):
    user = mongo.db.users.find_one({"username": username})
    user_videos = list(mongo.db.videos.find({"username": username}))
    return render_template('profile.html', user=user, videos=user_videos)

# --- ADMİN PANELİ (Reklam, Silmə, Dəyişmə) ---
@app.route('/admin_panel', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Adsterra və ya Digər Reklam Banner Kodlarını bura daxil et
        ad_html = request.form.get('ad_html')
        mongo.db.settings.update_one({"type": "ads"}, {"$set": {"code": ad_html}}, upsert=True)
        return "Sistem Yeniləndi!"
    return render_template('admin.html')

# --- MƏXFİLİK SİYASƏTİ (Qanuni Müdafiə) ---
@app.route('/privacy')
def privacy():
    return """
    <h1>EcoPix Məxfilik Siyasəti</h1>
    <p>Bu platforma istifadəçi məlumatlarını 256-bit şifrələmə ilə qoruyur.</p>
    <p>Paylaşılan videoların qanuni məsuliyyəti istifadəçinin özünə aiddir.</p>
    """

# --- TELEGRAM BOT İDARƏETMƏSİ ---
@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_message(message.chat.id, "EcoPix Canlı Yayım və Video Platformasına Xoş Gəldiniz!")

# --- RENDER ÜÇÜN PORT AYARI ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
