import os
import telebot
import threading
from flask import Flask, jsonify, render_template_string, request

# --- AYARLAR ---
TOKEN = "8682822347:AAEGrzVzv495LwTcGA85sCl5CbxhOsNRv7Q"
ADMIN_ID = 5073661002 # Sənin ID-n (Videoları silmək üçün)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Məlumatları müvəqqəti yaddaşda saxlayırıq (Render Disk pulsuz olmadığı üçün)
video_list = []

HTML = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>EcoPix | Social</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #000; color: #fff; overflow: hidden; font-family: sans-serif; }
        
        /* Video Akışı */
        .video-feed { width: 100%; height: 100vh; overflow-y: scroll; scroll-snap-type: y mandatory; scrollbar-width: none; }
        .video-feed::-webkit-scrollbar { display: none; }
        .video-card { position: relative; width: 100%; height: 100vh; scroll-snap-align: start; display: flex; align-items: center; justify-content: center; }
        video { width: 100%; height: 100%; object-fit: cover; }

        /* Sağ tərəf ikonları */
        .side-bar { position: absolute; right: 10px; bottom: 120px; display: flex; flex-direction: column; gap: 20px; align-items: center; z-index: 100; }
        .profile-btn { width: 45px; height: 45px; border-radius: 50%; border: 2px solid #fff; background: #444; overflow: hidden; }
        .action-item { text-align: center; cursor: pointer; }
        .action-item i { font-size: 30px; filter: drop-shadow(0 0 5px #000); }
        .action-item span { display: block; font-size: 12px; margin-top: 5px; }

        /* Alt Məlumat */
        .bottom-info { position: absolute; left: 15px; bottom: 80px; z-index: 10; width: 70%; }
        .username { font-weight: bold; font-size: 16px; margin-bottom: 5px; }
        .desc { font-size: 14px; opacity: 0.9; }

        /* Alt Menyu və Böyük + Düyməsi */
        .bottom-nav { position: absolute; bottom: 0; width: 100%; height: 70px; background: rgba(0,0,0,0.9); display: flex; justify-content: space-around; align-items: center; border-top: 0.5px solid #333; }
        .plus-btn { background: #fff; color: #000; width: 50px; height: 35px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; border: none; font-weight: bold; }

        /* Paylaşma və Koment Paneli (Gizli) */
        .overlay-panel { display: none; position: fixed; bottom: 0; width: 100%; height: 50%; background: #111; border-top-left-radius: 20px; border-top-right-radius: 20px; z-index: 1000; padding: 20px; }
    </style>
</head>
<body>

    <div class="video-feed" id="feed"></div>

    <div class="bottom-nav">
        <i class="fas fa-home" style="font-size: 22px;"></i>
        <i class="fas fa-search" style="font-size: 22px;"></i>
        <button class="plus-btn" onclick="openBot()">+</button>
        <i class="fas fa-comment-dots" style="font-size: 22px;"></i>
        <i class="fas fa-user" style="font-size: 22px;"></i>
    </div>

    <script>
        async function loadVideos() {
            const res = await fetch('/api/videos');
            const videos = await res.json();
            const feed = document.getElementById('feed');
            feed.innerHTML = '';

            videos.reverse().forEach(v => {
                feed.innerHTML += `
                    <div class="video-card">
                        <video loop playsinline onclick="this.paused ? this.play() : this.pause()" src="${v.url}"></video>
                        <div class="side-bar">
                            <div class="profile-btn"><img src="https://ui-avatars.com/api/?name=User" width="100%"></div>
                            <div class="action-item" onclick="alert('Bəyənildi!')"><i class="fas fa-heart"></i><span>${v.likes}</span></div>
                            <div class="action-item" onclick="alert('Rəylər tezliklə...')"><i class="fas fa-comment-dots"></i><span>0</span></div>
                            <div class="action-item" onclick="shareSocial('${v.url}')"><i class="fas fa-share"></i><span>Paylaş</span></div>
                        </div>
                        <div class="bottom-info">
                            <div class="username">@user_${v.user_id}</div>
                            <div class="desc">${v.desc}</div>
                        </div>
                    </div>`;
            });
            setupAutoPlay();
        }

        function setupAutoPlay() {
            const observer = new IntersectionObserver(es => {
                es.forEach(e => { 
                    const v = e.target.querySelector('video');
                    if(e.isIntersecting) v.play(); else v.pause(); 
                });
            }, {threshold: 0.8});
            document.querySelectorAll('.video-card').forEach(c => observer.observe(c));
        }

        function openBot() {
            window.location.href = "https://t.me/EcoPixSocialBot"; // Bura öz botunun linkini yaz
        }

        function shareSocial(url) {
            if(navigator.share) {
                navigator.share({ title: 'EcoPix-də videoya bax!', url: url });
            } else {
                alert("Linki kopyalayın: " + url);
            }
        }

        loadVideos();
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/api/videos')
def get_v(): return jsonify(video_list)

# --- BOT İDARƏETMƏ ---

@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(m, "EcoPix-ə xoş gəldin! 🎥\\n\\nVideo göndər (və ya çək), mən onu saniyəsində saytda paylaşım. Hər kəs sənin videolarını görəcək!")

@bot.message_handler(commands=['admin'])
def admin_panel(m):
    if m.from_user.id == ADMIN_ID:
        bot.reply_to(m, "Admin xos geldin! Videonu silmək üçün '/sil [Video ID]' yaz.")

@bot.message_handler(content_types=['video'])
def handle_video(m):
    file_info = bot.get_file(m.video.file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    
    video_data = {
        "id": len(video_list) + 1,
        "user_id": m.from_user.id,
        "url": url,
        "desc": m.caption or "Yeni video #ecopix",
        "likes": 0
    }
    video_list.append(video_data)
    bot.reply_to(m, "Video uğurla paylaşıldı! 🚀\\n\\nBax: https://ecopix-final.onrender.com")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
