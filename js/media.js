// js/media.js - Kamera və Video Pleyer İdarəsi

let myStream = null;

// Kameranı aktivləşdir/deaktiv et
async function toggleCam() {
    const v = document.getElementById('my-cam');
    const camBtn = document.getElementById('camBtn');
    
    if(!myStream) {
        try {
            // Kamera və Mikrofon icazəsi istəyirik
            myStream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
            v.srcObject = myStream;
            v.style.display = 'block';
            camBtn.classList.add('recording-active');
            camBtn.style.color = '#00f2ff';
        } catch(e) { 
            console.error("Kamera xətası:", e);
            alert("Kameraya giriş qadağan edildi və ya cihaz tapılmadı!"); 
        }
    } else {
        // Kameranı söndürürük
        myStream.getTracks().forEach(track => track.stop());
        myStream = null;
        v.style.display = 'none';
        camBtn.classList.remove('recording-active');
        camBtn.style.color = 'white';
    }
}

// YouTube və HLS (Canlı TV) pleyerlərini Firebase-dən dinləyirik
// Qeyd: 'room' dəyişəni firebase-config.js-dən gəlir
db.ref(`rooms/${room}/media`).on('value', snapshot => {
    const data = snapshot.val() || {t:'yt', id:'j_SInXN2Fas'}; // Boşdursa default video
    const yt = document.getElementById('yt-player');
    const hls = document.getElementById('hls-player');

    if(data.t === 'yt') {
        // YouTube rejimi
        yt.src = `https://www.youtube.com/embed/${data.id}?autoplay=1&mute=0`;
        yt.style.display = 'block'; 
        hls.style.display = 'none';
        hls.pause();
    } else if(data.t === 'hls') {
        // Canlı TV / M3U8 rejimi
        yt.style.display = 'none'; 
        hls.style.display = 'block';
        yt.src = "";
        
        if(Hls.isSupported()){
            let h = new Hls();
            h.loadSource(data.id);
            h.attachMedia(hls);
        } else if (hls.canPlayType('application/vnd.apple.mpegurl')) {
            hls.src = data.id;
        }
    }
});

// Otaq dəyişəndə media yenilənsin
window.addEventListener('storage', (e) => {
    if (e.key === 'v_room') {
        location.reload();
    }
});
