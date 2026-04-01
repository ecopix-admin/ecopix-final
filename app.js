let myPeer;
let localStream;
let currentCall;
let callStartTime;
let timerInterval;

// 1. Sabit ID Sistemi
const myID = localStorage.getItem('az_id') || 'az-' + Math.floor(100000 + Math.random() * 900000);
localStorage.setItem('az_id', myID);

function init() {
    myPeer = new Peer(myID);
    myPeer.on('open', id => document.getElementById('my-status').innerText = "ID: " + id);
    
    myPeer.on('call', call => {
        const callerName = getContactName(call.peer);
        document.getElementById('inc-name').innerText = callerName;
        document.getElementById('incoming-overlay').style.display = 'flex';

        document.getElementById('btn-accept').onclick = () => {
            navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
                localStream = stream;
                call.answer(stream);
                startCallUI(call, callerName);
                addHistory(call.peer, 'Gələn', true);
            });
        };

        document.getElementById('btn-reject').onclick = () => {
            call.close();
            document.getElementById('incoming-overlay').style.display = 'none';
            addHistory(call.peer, 'Buraxılmış', false);
        };
    });
    renderContacts();
    renderHistory();
}

// 2. Kontaktlar (Əlifba Sırası)
function saveContact() {
    let name = document.getElementById('c-name').value;
    let id = document.getElementById('c-id').value;
    if(!name || !id) return;

    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    contacts.push({name, id});
    // Əlifba sırası ilə düzmək
    contacts.sort((a, b) => a.name.localeCompare(b.name));
    localStorage.setItem('az_contacts', JSON.stringify(contacts));
    closeModal();
    renderContacts();
}

function renderContacts() {
    const container = document.getElementById('contact-list');
    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    container.innerHTML = '';
    contacts.forEach(c => {
        container.innerHTML += `
            <div class="card" onclick="makeCall('${c.id}', '${c.name}')">
                <div class="avatar"><img src="https://via.placeholder.com/50"></div>
                <div class="info"><b>${c.name}</b><small>${c.id}</small></div>
                <i class="fas fa-video" style="color:var(--accent); font-size:20px;"></i>
            </div>`;
    });
}

// 3. Zəng və Tarixçə
function makeCall(id, name) {
    navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
        localStream = stream;
        const call = myPeer.call(id, stream);
        startCallUI(call, name);
        addHistory(id, 'Gedən', true);
    });
}

function startCallUI(call, name) {
    currentCall = call;
    callStartTime = Date.now();
    document.getElementById('incoming-overlay').style.display = 'none';
    document.getElementById('call-ui').style.display = 'flex';
    document.getElementById('active-caller-name').innerText = name;
    
    call.on('stream', remoteStream => {
        document.getElementById('remote-v').srcObject = remoteStream;
    });

    timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
    let diff = Math.floor((Date.now() - callStartTime) / 1000);
    let m = Math.floor(diff / 60).toString().padStart(2, '0');
    let s = (diff % 60).toString().padStart(2, '0');
    document.getElementById('timer').innerText = `${m}:${s}`;
}

function terminateCall() {
    if(currentCall) currentCall.close();
    clearInterval(timerInterval);
    document.getElementById('call-ui').style.display = 'none';
    if(localStream) localStream.getTracks().forEach(t => t.stop());
}

function addHistory(id, type, wasAnswered) {
    let history = JSON.parse(localStorage.getItem('az_history') || '[]');
    let duration = wasAnswered ? document.getElementById('timer').innerText : "00:00";
    history.unshift({
        name: getContactName(id),
        id: id,
        type: type,
        time: new Date().toLocaleString('az-AZ'),
        duration: duration
    });
    localStorage.setItem('az_history', JSON.stringify(history.slice(0, 50)));
    renderHistory();
}

function renderHistory() {
    const container = document.getElementById('call-history-list');
    let history = JSON.parse(localStorage.getItem('az_history') || '[]');
    container.innerHTML = '';
    history.forEach(h => {
        let icon = h.type === 'Buraxılmış' ? 'fa-phone-slash h-missed' : (h.type === 'Gələn' ? 'fa-arrow-down h-incoming' : 'fa-arrow-up h-outgoing');
        container.innerHTML += `
            <div class="card">
                <i class="fas ${icon}" style="margin-right:15px; font-size:20px;"></i>
                <div class="info"><b>${h.name}</b><small>${h.time} (${h.duration})</small></div>
                <button onclick="deleteHistory(event)" style="background:none; border:none; color:white; opacity:0.3;"><i class="fas fa-trash"></i></button>
            </div>`;
    });
}

// Yardımçı funksiyalar
function getContactName(id) {
    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    let c = contacts.find(x => x.id === id);
    return c ? c.name : id;
}

function setPage(p) {
    document.querySelectorAll('.page').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.getElementById(p).classList.add('active');
    event.currentTarget.classList.add('active');
}

function openModal() { document.getElementById('modal-bg').style.display = 'block'; document.getElementById('modal').style.display = 'block'; }
function closeModal() { document.getElementById('modal-bg').style.display = 'none'; document.getElementById('modal').style.display = 'none'; }

init();
