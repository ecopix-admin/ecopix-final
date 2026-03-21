import os
import telebot
import threading
from flask import Flask, request, jsonify, render_template_string

# --- AYARLAR ---
TOKEN = "8682822347:AAEGrzVzv495LwTcGA85sCl5CbxhOsNRv7Q"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Videoları yaddaşda (RAM) saxlayırıq. 
# QEYD: Sayt yenilənəndə videolar silinəcək, amma Render disk üçün pul istədiyi üçün ən yaxşı pulsuz yol budur.
video_list = []

HTML = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>EcoPix | Pro</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #000; color: #fff; overflow: hidden; font-family: sans-serif; }
        .video-feed { width: 100%; height: 100vh; overflow-y: scroll; scroll-snap-type: y mandatory; scrollbar-width: none; }
        .video-feed::-webkit-scrollbar { display: none; }
        .video-card { position: relative; width: 100%; height: 100vh; scroll-snap-align: start; display: flex; align-items: center; justify-content: center; }
        video { width: 100%; height: 100%; object-fit: cover; }
        .search-bar { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); width: 90%; z-index: 100; }
        .search-bar input { width: 100%; padding: 12px; border-radius: 25px; border: none; background: rgba(255,255,255,0.2); color: white; backdrop-filter: blur(10px); }
        .side-bar { position: absolute; right: 15px; bottom: 100px; display: flex; flex-direction: column; gap: 20px; align-items: center; }
        .action-item { text-align: center; font-size: 30px; text-shadow: 0 0 5px #000; }
        .action-item span { display: block; font-size: 12px; margin-top: 5px; }
        .bottom-info { position: absolute; left: 15px; bottom: 30px; }
    </style>
</head>
<body>
    <div class="search-bar"><input type="text" placeholder="Video axtar..."></div>
    <div class="video-feed" id="feed"></div>
    <script>
        async function load() {
            const res = await fetch('/api/videos');
            const videos = await res.json();
            const feed = document.getElementById('feed');
            feed.innerHTML = '';
            videos.reverse().forEach(v => {
                feed.innerHTML += `
                    <div class="video-card">
                        <video loop playsinline onclick="this.paused ? this.play() : this.pause()" src="${v.url}"></video>
                        <div class="side-bar">
                            <div class="action-item"><i class="fas fa-heart"></i><span>0</span></div>
                            <div class="action-item"><i class="fas fa-eye"></i><span>0</span></div>
                            <div class="action-item"><i class="fas fa-share"></i></div>
                        </div>
                        <div class="bottom-info"><b>@EcoPix</b><p>${v.desc}</p></div>
                    </div>`;
            });
            const obs = new IntersectionObserver(es => {
                es.forEach(e => { if(e.isIntersecting) e.target.querySelector('video').play(); else e.target.querySelector('video').pause(); });
            }, {threshold: 0.8});
            document.querySelectorAll('.video-card').forEach(c => obs.observe(c));
        }
        load();
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/api/videos')
def get(): return jsonify(video_list)

@bot.message_handler(content_types=['video'])
def h(m):
    file_info = bot.get_file(m.video.file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    video_list.append({"url": url, "desc": m.caption or ""})
    bot.reply_to(m, "Video əlavə edildi! ✅")

threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
