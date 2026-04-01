let peer;
let currentCall;
let startTime;
let timerInterval;

// 1. DAİMİ VƏ DƏYİŞİLƏBİLƏN ID
let myID = localStorage.getItem('az_permanent_id') || 'az-' + Math.floor(Math.random()*900000);
localStorage.setItem('az_permanent_id', myID);

function initPeer(id) {
    if(peer) peer.destroy();
    peer = new Peer(id);
    peer.on('open', (id) => {
        document.getElementById('my-display-id').innerText = "ID: " + id;
        // Profil məlumatlarını şəbəkəyə sızdırırıq (Simulyasiya)
        broadcastProfile();
    });
    
    // Gələn zəngi qəbul etmə
    peer.on('call', (call) => {
        if(confirm("Gələn zəng: " + call.peer + ". Cavab verilsin?")) {
            navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
                showCallScreen();
                call.answer(stream);
                handleCall(call, stream);
            });
        }
    });
}

initPeer(myID);

// 2. ZƏNGİ SONLANDIRMA VƏ TARİXÇƏ
function handleCall(call, localStream) {
    currentCall = call;
    startTime = new Date();
    startTimer();
    
    call.on('stream', remoteStream => {
        document.getElementById('remote-video').srcObject = remoteStream;
        document.getElementById('local-video').srcObject = localStream;
    });

    call.on('close', () => endCallProcess());
}

function hangUp() {
    if(currentCall) currentCall.close();
    endCallProcess();
}

function endCallProcess() {
    clearInterval(timerInterval);
    let duration = Math.floor((new Date() - startTime) / 1000);
    saveToHistory(currentCall.peer, duration);
    document.getElementById('call-screen').style.display = 'none';
    // Kamera və mikrafonu söndür
    location.reload(); 
}

// 3. TARİXÇƏ (10 GÜNLÜK VƏ ALT-ALTA)
function saveToHistory(id, duration) {
    let history = JSON.parse(localStorage.getItem('az_history') || '[]');
    let record = {
        id: id,
        name: getContactName(id),
        time: new Date().toLocaleString('az-AZ'),
        duration: duration + " san",
        dateRaw: new Date()
    };
    history.unshift(record);
    // 10 gündən köhnələri sil (Sadələşdirilmiş: son 50 zəng)
    localStorage.setItem('az_history', JSON.stringify(history.slice(0, 50)));
    renderHistory();
}

// 4. VİRTUAL ID (NÖMRƏ DƏYİŞMƏ)
function changeMyID() {
    let newID = document.getElementById('custom-id').value;
    if(newID) {
        localStorage.setItem('az_permanent_id', newID);
        alert("Yeni ID-niz aktivdir: " + newID);
        initPeer(newID);
    }
}

// 5. PROFİL VƏ KONTAKT REDAKTƏSİ
function saveMyProfile() {
    let profile = {
        name: document.getElementById('my-name').value,
        bio: document.getElementById('my-bio').value,
        photo: document.getElementById('my-photo').src
    };
    localStorage.setItem('my_profile', JSON.stringify(profile));
    alert("Profil yadda saxlanıldı!");
}

function startTimer() {
    let sec = 0;
    timerInterval = setInterval(() => {
        sec++;
        let m = Math.floor(sec/60);
        let s = sec % 60;
        document.getElementById('call-timer').innerText = `${m<10?'0':''}${m}:${s<10?'0':''}${s}`;
    }, 1000);
}

function showPage(p) {
    document.querySelectorAll('.page').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.getElementById(p).classList.add('active');
    event.currentTarget.classList.add('active');
}

function showCallScreen() {
    document.getElementById('call-screen').style.display = 'flex';
}
