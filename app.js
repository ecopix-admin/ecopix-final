let myPeer, currentCall, localStream, activeChatId = null, timerInt;
let mediaRecorder, audioChunks = [];
const myID = localStorage.getItem('az_id') || 'az-' + Math.floor(100000 + Math.random() * 900000);
localStorage.setItem('az_id', myID);

function init() {
    myPeer = new Peer(myID);
    myPeer.on('open', id => document.getElementById('my-status').innerText = "ID: " + id);
    
    // Gələn zəng və adın tanınması
    myPeer.on('call', call => {
        const caller = getContact(call.peer);
        document.getElementById('call-user-name').innerText = caller.name;
        document.getElementById('call-user-id').innerText = call.peer;
        document.getElementById('call-photo').src = caller.photo || 'https://via.placeholder.com/150';
        document.getElementById('ringtone').play();
        document.getElementById('call-overlay').style.display = 'flex';
        document.getElementById('ans-btn').style.display = 'block';
        currentCall = call;
    });

    // Mesaj alma
    myPeer.on('connection', conn => {
        conn.on('data', data => {
            handleIncomingData(conn.peer, data);
            document.getElementById('msg-tone').play();
            addToChatList(conn.peer);
        });
    });

    renderAll();
}

// Səs Yazma (Push-to-Talk)
async function startVoiceMsg() {
    document.getElementById('mic-btn').classList.add('active');
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.start();
}

function endVoiceMsg() {
    document.getElementById('mic-btn').classList.remove('active');
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            sendMedia(audioBlob, 'voice');
        };
    }
}

// Söhbətlər Siyahısı (Chat List)
function addToChatList(id) {
    let chatList = JSON.parse(localStorage.getItem('az_chat_list') || '[]');
    if (!chatList.includes(id)) chatList.unshift(id);
    localStorage.setItem('az_chat_list', JSON.stringify(chatList));
    renderAll();
}

function renderAll() {
    // Söhbətlər Səhifəsi
    const chatsPage = document.getElementById('chats');
    let chatIds = JSON.parse(localStorage.getItem('az_chat_list') || '[]');
    chatsPage.innerHTML = chatIds.map(id => {
        const c = getContact(id);
        return `
            <div class="item-card" onclick="openChat('${id}', '${c.name}')">
                <img src="${c.photo || 'https://via.placeholder.com/50'}" class="avatar">
                <div class="item-info"><b>${c.name}</b><span>Son mesaj...</span></div>
            </div>`;
    }).join('');

    // Kontaktlar (A-Z)
    const contactsPage = document.getElementById('contacts');
    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    contacts.sort((a,b) => a.name.localeCompare(b.name));
    contactsPage.innerHTML = contacts.map(c => `
        <div class="item-card">
            <img src="${c.photo || 'https://via.placeholder.com/50'}" class="avatar" onclick="openChat('${c.id}', '${c.name}')">
            <div class="item-info" onclick="openChat('${c.id}', '${c.name}')"><b>${c.name}</b><span>${c.id}</span></div>
            <i class="fas fa-trash" style="color:red; padding:10px;" onclick="deleteContact('${c.id}')"></i>
        </div>`).join('');
}

// Zəng Funksiyaları (Saniyə ölçən və dərhal açılma)
function initiateCall(type) {
    navigator.mediaDevices.getUserMedia({ video: type==='video', audio:true }).then(stream => {
        localStream = stream;
        const call = myPeer.call(activeChatId, stream);
        setupCallUI(activeChatId, type);
        currentCall = call;
        call.on('stream', remote => {
            document.getElementById('v-remote').srcObject = remote;
            if(type==='video') document.getElementById('v-remote').style.display = 'block';
            startTimer();
        });
    });
}

function answerCall() {
    document.getElementById('ringtone').pause();
    document.getElementById('ans-btn').style.display = 'none';
    navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
        localStream = stream;
        currentCall.answer(stream);
        currentCall.on('stream', remote => {
            document.getElementById('v-remote').srcObject = remote;
            document.getElementById('v-remote').style.display = 'block';
            startTimer();
        });
    });
}

function endCall() {
    if(currentCall) currentCall.close();
    location.reload();
}

function startTimer() {
    let s = 0;
    clearInterval(timerInt);
    timerInt = setInterval(() => {
        s++;
        let m = Math.floor(s/60).toString().padStart(2,'0');
        let sec = (s%60).toString().padStart(2,'0');
        document.getElementById('call-timer').innerText = `${m}:${sec}`;
    }, 1000);
}

// Köməkçi Funksiyalar
function getContact(id) {
    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    return contacts.find(c => c.id === id) || { name: id, photo: null };
}

function saveNewContact() {
    const name = document.getElementById('new-c-name').value;
    const id = document.getElementById('new-c-id').value;
    if(!name || !id) return;
    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    contacts.push({name, id, photo: null});
    localStorage.setItem('az_contacts', JSON.stringify(contacts));
    document.getElementById('contact-modal').style.display = 'none';
    renderAll();
}

function openChat(id, name) {
    activeChatId = id;
    const c = getContact(id);
    document.getElementById('chat-window').style.display = 'flex';
    document.getElementById('chat-name').innerText = name;
    document.getElementById('chat-avatar').src = c.photo || 'https://via.placeholder.com/50';
    addToChatList(id);
}

function closeChat() { document.getElementById('chat-window').style.display = 'none'; }
function setPage(p) {
    document.querySelectorAll('.page').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.getElementById(p).classList.add('active');
    event.currentTarget.classList.add('active');
}

init();
