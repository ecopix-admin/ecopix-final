let myPeer, currentCall, dataConn, localStream, timerInt;
let activeId = null;
let mediaRec, chunks = [];

const MY_ID = localStorage.getItem('az_id') || 'az-' + Math.floor(100000 + Math.random() * 900000);
localStorage.setItem('az_id', MY_ID);

// 1. Peer Başlatma
function init() {
    myPeer = new Peer(MY_ID);
    myPeer.on('open', id => document.getElementById('my-status').innerText = "ID: " + id);
    
    // Gələn Zənglər
    myPeer.on('call', call => {
        const caller = getContact(call.peer);
        document.getElementById('call-label').innerText = caller.name;
        document.getElementById('call-img').src = caller.photo || 'https://via.placeholder.com/150';
        document.getElementById('ring-snd').play();
        document.getElementById('call-overlay').style.display = 'flex';
        document.getElementById('ans-btn').style.display = 'block';
        currentCall = call;
    });

    // Gələn Mesajlar
    myPeer.on('connection', conn => {
        dataConn = conn;
        conn.on('data', data => {
            handleData(conn.peer, data);
            document.getElementById('msg-snd').play();
            addToChats(conn.peer);
        });
    });

    // Səs Yazma düyməsinin bas-saxla funksiyası
    const mBtn = document.getElementById('mic-btn');
    mBtn.addEventListener('mousedown', startRec);
    mBtn.addEventListener('mouseup', stopRec);
    mBtn.addEventListener('touchstart', (e) => { e.preventDefault(); startRec(); });
    mBtn.addEventListener('touchend', (e) => { e.preventDefault(); stopRec(); });

    render();
}

// 2. Mesaj Göndərmə (MƏTN)
function sendTextMessage() {
    const txt = document.getElementById('msg-input').value;
    if(!txt || !activeId) return;

    const conn = myPeer.connect(activeId);
    conn.on('open', () => {
        conn.send({ type: 'text', content: txt });
        displayMsg(txt, 'sent');
        document.getElementById('msg-input').value = '';
        addToChats(activeId);
    });
}

// 3. Səs Yazma (Push-to-Talk)
async function startRec() {
    document.getElementById('mic-btn').classList.add('active');
    chunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRec = new MediaRecorder(stream);
    mediaRec.ondataavailable = e => chunks.push(e.data);
    mediaRec.start();
}

function stopRec() {
    document.getElementById('mic-btn').classList.remove('active');
    if (mediaRec && mediaRec.state !== "inactive") {
        mediaRec.stop();
        mediaRec.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/webm' });
            const reader = new FileReader();
            reader.onload = () => {
                const conn = myPeer.connect(activeId);
                conn.on('open', () => {
                    conn.send({ type: 'voice', content: reader.result });
                    displayMsg('🎤 Səsli mesaj', 'sent');
                });
            };
            reader.readAsDataURL(blob);
        };
    }
}

// 4. Zəngi Cavablandırmaq və ya Rədd Etmək
function acceptCall() {
    document.getElementById('ring-snd').pause();
    document.getElementById('ans-btn').style.display = 'none';
    navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
        localStream = stream;
        currentCall.answer(stream);
        currentCall.on('stream', remote => {
            document.getElementById('v-remote').srcObject = remote;
            document.getElementById('v-remote').style.display = 'block';
            startClock();
        });
    });
}

function hangUp() {
    if(currentCall) currentCall.close();
    location.reload();
}

// 5. Söhbətlər Siyahısı (Chat List)
function addToChats(id) {
    let list = JSON.parse(localStorage.getItem('az_chats') || '[]');
    if(!list.includes(id)) list.unshift(id);
    localStorage.setItem('az_chats', JSON.stringify(list));
    render();
}

function render() {
    const chatsPage = document.getElementById('chats');
    let ids = JSON.parse(localStorage.getItem('az_chats') || '[]');
    chatsPage.innerHTML = ids.map(id => {
        const c = getContact(id);
        return `<div class="item-card" onclick="openChat('${id}', '${c.name}')">
            <img src="${c.photo || 'https://via.placeholder.com/50'}" class="avatar">
            <div class="item-info"><b>${c.name}</b><span>Söhbəti açın</span></div>
        </div>`;
    }).join('');
}

// Köməkçi Funksiyalar
function openChat(id, name) {
    activeId = id;
    const c = getContact(id);
    document.getElementById('chat-window').style.display = 'flex';
    document.getElementById('chat-name').innerText = name;
    document.getElementById('chat-avatar').src = c.photo || 'https://via.placeholder.com/50';
}

function closeChat() { document.getElementById('chat-window').style.display = 'none'; }
function toggleAttach() { 
    const m = document.getElementById('attach-menu');
    m.style.display = m.style.display === 'flex' ? 'none' : 'flex';
}

function displayMsg(text, type) {
    const div = document.createElement('div');
    div.className = `msg ${type}`;
    div.innerText = text;
    document.getElementById('chat-msgs').appendChild(div);
    document.getElementById('chat-msgs').scrollTop = 9999;
}

function handleData(id, data) {
    if(data.type === 'text') displayMsg(data.content, 'received');
    if(data.type === 'voice') displayMsg('🎤 Səsli mesaj gəldi', 'received');
}

function getContact(id) {
    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    return contacts.find(c => c.id === id) || { name: id, photo: null };
}

function startClock() {
    let s = 0; clearInterval(timerInt);
    timerInt = setInterval(() => {
        s++;
        let m = Math.floor(s/60).toString().padStart(2,'0');
        let sec = (s%60).toString().padStart(2,'0');
        document.getElementById('call-timer').innerText = `${m}:${sec}`;
    }, 1000);
}

function setPage(p) {
    document.querySelectorAll('.page').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.getElementById(p).classList.add('active');
}

init();
