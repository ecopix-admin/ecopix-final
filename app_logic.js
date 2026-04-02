let callLogs = JSON.parse(localStorage.getItem('az_calls')) || [];

// Səsləri işə salmaq üçün mütləqdir
function initAudio() {
    console.log("Audio sistemi aktivdir.");
}

function playRingtone() {
    const ring = document.getElementById('ringtone');
    ring.play().catch(e => console.log("Səs üçün istifadəçi hərəkəti lazımdır"));
}

function stopRingtone() {
    const ring = document.getElementById('ringtone');
    ring.pause();
    ring.currentTime = 0;
}

// Zəng funksiyası
async function startCall(name, isVideo) {
    document.getElementById('call-name').innerText = name;
    document.getElementById('call-screen').style.display = 'flex';
    playRingtone();

    // Tarixçəyə yaz
    const callData = { name, time: new Date().toLocaleTimeString(), date: new Date().toLocaleDateString(), id: Date.now() };
    callLogs.unshift(callData);
    localStorage.setItem('az_calls', JSON.stringify(callLogs));
    renderCallLogs();

    if(isVideo) {
        document.getElementById('video-box').style.display = 'block';
        const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
        document.getElementById('local-video').srcObject = stream;
    }
}

function endCall() {
    stopRingtone();
    document.getElementById('call-screen').style.display = 'none';
    const stream = document.getElementById('local-video').srcObject;
    stream?.getTracks().forEach(t => t.stop());
}

// Bildiriş Göndərmə
function sendNotification(title, msg) {
    document.getElementById('msg-sound').play();
    if (Notification.permission === "granted") {
        new Notification(title, { body: msg, icon: 'logo.png' });
    }
}

// Tarixçəni göstər
function renderCallLogs() {
    const logDiv = document.getElementById('call-log');
    logDiv.innerHTML = callLogs.map((c, i) => `
        <div style="display:flex; justify-content:space-between; padding:15px; border-bottom:1px solid #222;">
            <div>
                <b>${c.name}</b><br>
                <small>${c.date} ${c.time}</small>
            </div>
            <div>
                <i class="fas fa-phone" onclick="startCall('${c.name}', false)" style="color:var(--green); margin-right:20px;"></i>
                <i class="fas fa-trash" onclick="deleteLog(${i})" style="color:red;"></i>
            </div>
        </div>
    `).join('');
}

function deleteLog(index) {
    callLogs.splice(index, 1);
    localStorage.setItem('az_calls', JSON.stringify(callLogs));
    renderCallLogs();
}

// İcazə istə
if (Notification.permission !== "granted") {
    Notification.requestPermission();
}

renderCallLogs();
