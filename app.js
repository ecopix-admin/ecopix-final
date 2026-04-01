// SABİT ID SİSTEMİ
let myPermanentID = localStorage.getItem('azchat_id');
if (!myPermanentID) {
    myPermanentID = 'az-' + Math.floor(Math.random() * 900000 + 100000);
    localStorage.setItem('azchat_id', myPermanentID);
}

const peer = new Peer(myPermanentID);

peer.on('open', (id) => {
    document.getElementById('my-id').innerText = "ID: " + id;
});

// KONTAKT SİSTEMİ (AD VƏ ID BAĞLANTISI)
function renderContacts() {
    const list = document.getElementById('contact-list');
    let contacts = JSON.parse(localStorage.getItem('azContacts') || '[]');
    list.innerHTML = '';
    contacts.forEach(c => {
        list.innerHTML += `
            <div class="item">
                <div class="avatar"><i class="fas fa-user"></i></div>
                <div class="info" onclick="startChat('${c.id}')"><div class="name">${c.name}</div><div class="sub">${c.id}</div></div>
                <i class="fas fa-video" style="color: var(--green); padding: 10px;" onclick="startCall('${c.id}')"></i>
            </div>`;
    });
}

function addContact() {
    const name = prompt("Kontaktın Adı:");
    const id = prompt("Anten ID-si:");
    if(name && id) {
        let contacts = JSON.parse(localStorage.getItem('azContacts') || '[]');
        contacts.push({name, id});
        localStorage.setItem('azContacts', JSON.stringify(contacts));
        renderContacts();
    }
}

// ZƏNG VƏ TARİXÇƏ
function startCall(peerId) {
    navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
        const call = peer.call(peerId, stream);
        addCallToHistory(peerId);
        // Video pəncərəsi məntiqi burada
        alert("Zəng edilir: " + peerId);
    });
}

function addCallToHistory(id) {
    let history = JSON.parse(localStorage.getItem('azCallHistory') || '[]');
    history.unshift({id, time: new Date().toLocaleTimeString()});
    localStorage.setItem('azCallHistory', JSON.stringify(history.slice(0, 20)));
    renderCalls();
}

function renderCalls() {
    const list = document.getElementById('call-history-list');
    let history = JSON.parse(localStorage.getItem('azCallHistory') || '[]');
    list.innerHTML = history.map(h => `
        <div class="item">
            <div class="info"><div class="name">${h.id}</div><div class="sub">${h.time}</div></div>
            <i class="fas fa-phone-alt"></i>
        </div>`).join('');
}
