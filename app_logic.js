let contacts = JSON.parse(localStorage.getItem('azchat_contacts')) || [];
let calls = JSON.parse(localStorage.getItem('azchat_calls')) || [];

// Zəng Səsi funksiyası
function playRingtone() {
    document.getElementById('ringtone').play().catch(e => console.log("Səs üçün toxunuş lazımdır"));
}

function stopRingtone() {
    document.getElementById('ringtone').pause();
    document.getElementById('ringtone').currentTime = 0;
}

// Mesaj Səsi funksiyası (Bildiriş)
function playMsgSound() {
    document.getElementById('msg-sound').play();
    if (Notification.permission === "granted") {
        new Notification("AzChat", { body: "Yeni mesajınız var!" });
    }
}

// Zəng Başlatma (Gedən)
async function startCall(name, type) {
    document.getElementById('call-user-name').innerText = name;
    document.getElementById('call-screen').style.display = 'flex';
    document.getElementById('call-status').innerText = "Zəng edilir...";
    
    playRingtone(); // Zəng səsi başlasın

    // Tarixçəyə əlavə et
    const newCall = { name, type, time: new Date().toLocaleString(), id: Date.now() };
    calls.unshift(newCall);
    localStorage.setItem('azchat_calls', JSON.stringify(calls));
    renderCalls();

    if(type === 'video') {
        const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
        document.getElementById('local-v').srcObject = stream;
        document.getElementById('video-grid').style.display = 'grid'; // Ekranı iki yerə böl
    }
}

function endCall() {
    stopRingtone();
    document.getElementById('call-screen').style.display = 'none';
    const stream = document.getElementById('local-v').srcObject;
    stream?.getTracks().forEach(t => t.stop());
}

// Zəng Tarixçəsini Göstər və Sil
function renderCalls() {
    const list = document.getElementById('call-history-list');
    list.innerHTML = calls.map((c, index) => `
        <div class="call-item">
            <div class="call-meta">
                <h4>${c.name}</h4>
                <p>${c.time}</p>
            </div>
            <div class="call-btns">
                <i class="fas fa-phone-alt" onclick="startCall('${c.name}', 'audio')"></i>
                <i class="fas fa-trash" onclick="deleteCall(${index})"></i>
            </div>
        </div>
    `).join('');
}

function deleteCall(index) {
    calls.splice(index, 1);
    localStorage.setItem('azchat_calls', JSON.stringify(calls));
    renderCalls();
}

// Bildiriş icazəsi al
Notification.requestPermission();
renderCalls();
