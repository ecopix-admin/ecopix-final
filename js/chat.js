async function uploadToCloud(file, type) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('upload_preset', 'ml_default');
    try {
        const res = await fetch('https://api.cloudinary.com/v1_1/dyrfkit3x/auto/upload', {method:'POST', body:fd});
        const d = await res.json();
        db.ref(`rooms/${room}/msgs`).push({user: nick, url: d.secure_url, type: type});
    } catch(e) { alert("Yükləmə xətası! İnterneti yoxlayın."); }
}

function sendMsg() {
    const i = document.getElementById('msgInp');
    if(i.value.trim()) {
        db.ref(`rooms/${room}/msgs`).push({user: nick, text: i.value, type: 'text'});
        i.value = "";
    }
}

// Mesajları dinləmək
db.ref(`rooms/${room}/msgs`).limitToLast(30).on('child_added', s => {
    const d = s.val();
    const div = document.createElement('div');
    div.className = `msg ${d.user === nick ? 'me' : ''}`;
    div.innerHTML = `<b>${d.user}</b>` + (d.type === 'text' ? d.text : `<${d.type} src="${d.url}" controls style="width:100%"></${d.type}>`);
    document.getElementById('msgBox').appendChild(div);
    document.getElementById('msgBox').scrollTop = 99999;
});
