const peer = new Peer('az-' + Math.floor(Math.random() * 999999));

peer.on('open', (id) => {
    document.getElementById('my-id').innerText = "Aktiv Anten ID: " + id;
    console.log("Rabitə kanalı açıldı.");
});

function startCall() {
    const peerId = prompt("Zəng etmək istədiyiniz ID:");
    if (!peerId) return;
    navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
        const call = peer.call(peerId, stream);
        alert(peerId + " ilə əlaqə qurulur...");
    }).catch(e => alert("Kameraya icazə verilmədi."));
}

function sendMsg() {
    const peerId = prompt("Mesaj göndəriləcək ID:");
    const msg = prompt("Mesajınız:");
    const conn = peer.connect(peerId);
    conn.on('open', () => conn.send(msg));
}
