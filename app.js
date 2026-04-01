let myPeer;
let currentCall;
let localStream;
let activeChatId = null;
let timerInt;
const myID = localStorage.getItem('az_id') || 'az-' + Math.floor(100000 + Math.random() * 900000);
localStorage.setItem('az_id', myID);

function init() {
    myPeer = new Peer(myID);
    myPeer.on('open', id => document.getElementById('my-status').innerText = "ID: " + id);

    // Gələn Zəng Məntiqi
    myPeer.on('call', call => {
        document.getElementById('ringtone').play();
        showCallOverlay(call.peer, true);
        currentCall = call;
    });

    renderAll();
}

// Kontakt və Tarixçəni Render Et
function renderAll() {
    // Kontaktlar (Əlifba sırası)
    const cList = document.getElementById('contacts');
    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    contacts.sort((a,b) => a.name.localeCompare(b.name));
    cList.innerHTML = contacts.map(c => `
        <div class="item-card" onclick="openChat('${c.id}', '${c.name}')">
            <img src="${c.photo || 'https://via.placeholder.com/50'}" class="avatar">
            <div class="item-info"><b>${c.name}</b><span>${c.id}</span></div>
        </div>
    `).join('');

    // Zəng Tarixçəsi (WhatsApp stili)
    const callsPage = document.getElementById('calls');
    let history = JSON.parse(localStorage.getItem('az_history') || '[]');
    callsPage.innerHTML = history.map((h, index) => `
        <div class="item-card">
            <i class="fas ${h.type==='Buraxılmış'?'fa-phone-slash':'fa-phone'} " style="color:${h.type==='Buraxılmış'?'red':'var(--wa-accent)'}; margin-right:15px;"></i>
            <div class="item-info"><b>${h.name}</b><span>${h.time} (${h.duration})</span></div>
            <div class="item-actions">
                <i class="fas fa-phone" onclick="initiateCall('voice', '${h.id}')"></i>
                <i class="fas fa-trash" style="color:rgba(255,255,255,0.3)" onclick="deleteHistory(${index})"></i>
            </div>
        </div>
    `).join('');
}

// Zəng Funksiyaları
function initiateCall(type, targetId = activeChatId) {
    const constraints = { video: type === 'video', audio: true };
    navigator.mediaDevices.getUserMedia(constraints).then(stream => {
        localStream = stream;
        const call = myPeer.call(targetId, stream);
        showCallOverlay(targetId, false);
        currentCall = call;
        handleCallStream(call, type);
    });
}

function answerCall() {
    document.getElementById('ringtone').pause();
    navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
        localStream = stream;
        currentCall.answer(stream);
        showCallOverlay(currentCall.peer, false, true);
        handleCallStream(currentCall, 'video');
    });
}

function handleCallStream(call, type) {
    if(type === 'video') document.getElementById('v-remote').style.display = 'block';
    call.on('stream', remote => {
        document.getElementById('v-remote').srcObject = remote;
        startTimer();
    });
}

function startTimer() {
    let sec = 0;
    clearInterval(timerInt);
    timerInt = setInterval(() => {
        sec++;
        let m = Math.floor(sec/60).toString().padStart(2,'0');
        let s = (sec%60).toString().padStart(2,'0');
        document.getElementById('call-timer').innerText = `${m}:${s}`;
    }, 1000);
}

function endCall() {
    if(currentCall) {
        addHistory(currentCall.peer, 'Gedən', document.getElementById('call-timer').innerText);
        currentCall.close();
    }
    location.reload(); // Sistemi sıfırla
}

// Tarixçəni Silmə
function deleteHistory(index) {
    let history = JSON.parse(localStorage.getItem('az_history') || '[]');
    history.splice(index, 1);
    localStorage.setItem('az_history', JSON.stringify(history));
    renderAll();
}

function addHistory(id, type, duration) {
    let history = JSON.parse(localStorage.getItem('az_history') || '[]');
    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    let name = contacts.find(c => c.id === id)?.name || id;
    history.unshift({ name, id, type, duration, time: new Date().toLocaleString('az-AZ') });
    localStorage.setItem('az_history', JSON.stringify(history));
    renderAll();
}

// Profil və Digər Səhifə Keçidləri
function setPage(p) {
    document.querySelectorAll('.page').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.getElementById(p).classList.add('active');
    event.currentTarget.classList.add('active');
}

function openChat(id, name) {
    activeChatId = id;
    document.getElementById('chat-window').style.display = 'flex';
    document.getElementById('chat-name').innerText = name;
}
function closeChat() { document.getElementById('chat-window').style.display = 'none'; }

function showCallOverlay(id, isIncoming, active = false) {
    document.getElementById('call-overlay').style.display = 'flex';
    document.getElementById('call-user').innerText = id;
    document.getElementById('incoming-btns').style.display = isIncoming ? 'flex' : 'none';
    document.getElementById('active-btns').style.display = !isIncoming || active ? 'flex' : 'none';
}

init();
